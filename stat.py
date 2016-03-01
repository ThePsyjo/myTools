import sys
import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func, desc, event

engine = create_engine('sqlite:///%s' % os.path.expanduser('~/.stat.db'), echo=False)

#noinspection PyUnusedLocal
@event.listens_for(engine, 'connect')
def set_sqlite_pragma(dbapi_con, con_record):
	dbapi_con.execute('PRAGMA journal_mode = MEMORY')
	dbapi_con.execute('PRAGMA synchronous = 0')
	dbapi_con.execute('PRAGMA cache_size = -102400')
	#dbapi_con.execute('PRAGMA foreign_keys=ON')

Session = sessionmaker(bind=engine)
'''session generator'''
Base = declarative_base()

class CountableBase(Base):
	""" Abstract, countable Base """
	__abstract__ = True

	@classmethod
	def count(cls):
		""" count rows of self """
		session = Session()
		try:
			n = session.query(func.count(cls.id)).first()[0]
		except:
			n = 0
		session.close()
		return n

class Stat(CountableBase):
	""" DeployLog Schema.   """
	__tablename__ = 'stat'

	id = Column(Integer, primary_key=True, autoincrement=True)
	atime = Column(Integer)
	ctime = Column(Integer)
	size = Column(Integer)
	path = Column(String, index=True)
	found = Column(Boolean)

	@classmethod
	def find(cls, fp, session):
		return session.query(cls).filter_by(path=fp).first()

	@classmethod
	def count_found(cls, session):
		try:
			n = session.query(func.count(cls.id)).filter_by(found=True).first()[0]
		except:
			n = 0
		return n

	@classmethod
	def count_missing(cls, session):
		try:
			n = session.query(func.count(cls.id)).filter_by(found=False).first()[0]
		except:
			n = 0
		return n

Base.metadata.create_all(engine, checkfirst=True)

def gen(path = '.'):
	j = os.path.join
	s = os.stat
	for (path, dirs, files) in os.walk(sys.argv[1]):
		for f in files:
			fp = j(path, f)
			yield fp, s(fp)

sess = Session()

def main():
	cnt = 0
	gcnt = 0
	new = 0
	sess.query(Stat).update({"found": False})
	sess.commit()
	f = sys.stdout.flush
	
	for fp, stat in gen(sys.argv[1]):
		gcnt += 1
		if gcnt % 100 == 0:
			print('%s - %s new\r' % (gcnt, new)),
			f()
		s = Stat.find(fp, sess)
		if not s:
			s = Stat()
			sess.add(s)
			s.path = fp
			new += 1
		s.atime = stat.st_atime
		s.ctime = stat.st_ctime
		s.size = stat.st_size
		s.found = True
		if cnt > 10000:
			cnt = 0
			sess.commit()
		else:
			cnt += 1
	
	sess.commit()
	
	print('\ndone')
	print('found %s files, %s new, %s are missing.' % (Stat.count_found(sess), new, Stat.count_missing(sess)))
	print('cleanup')
	print(sess.query(Stat).filter_by(found=False).delete())
	sess.commit()
	print('done')

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		sess.commit()
	finally:
		sess.close()
