import os
from time import time, timezone
from pyinotify import WatchManager, Notifier, EventsCodes, ProcessEvent
import sys
from sqlalchemy import create_engine, event, func, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

wm = WatchManager()

mask = EventsCodes.FLAG_COLLECTIONS['OP_FLAGS']['IN_DELETE'] | EventsCodes.FLAG_COLLECTIONS['OP_FLAGS']['IN_CREATE']

db_uri = 'sqlite:////root/.dir_index.db'

engine = create_engine(db_uri, echo=False)


#noinspection PyUnusedLocal
@event.listens_for(engine, 'connect')
def set_sqlite_pragma(dbapi_con, con_record):
    """Set SQLite PRAGMA on connect.

    :param dbapi_con:
    :param con_record:
    """
    dbapi_con.execute('PRAGMA journal_mode = MEMORY')
    dbapi_con.execute('PRAGMA synchronous = 0')
    dbapi_con.execute('PRAGMA cache_size = -1024')
    dbapi_con.execute('PRAGMA foreign_keys=ON')

Session = sessionmaker(bind=engine)
"""session generator"""
Base = declarative_base()


class CountableBase(Base):
    """ Abstract, countable Base """
    __abstract__ = True

    @classmethod
    def count(cls, session=Session()):
        """ count rows of self
        :param session: the session to use
        """
        # noinspection PyBroadException
        try:
            return session.query(func.count(cls.id)).first()[0]
        except:
            return 0

S = Session()


def mkts():
    """
    Make a UTC timestamp as float.

    :return: current UTC-timestamp
    """
    return time() + timezone


class File(CountableBase):
    """ File Schema

    All recorded files
    """
    __tablename__ = 'file'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True)

    created_at = Column(Integer, default=0)
    updated_at = Column(Integer, default=0)
    path = Column(String(255))
    size = Column(Integer, default=0)

    @classmethod
    def find(cls, path):
        """

        :param path: the path to search for
        :return: File instance or None
        :rtype: File
        """
        return S.query(cls).filter_by(path=path)

    @classmethod
    def remove(cls, path):
        S.query(cls).filter_by(path=path).delete()

Base.metadata.create_all(engine, checkfirst=True)

join = os.path.join


class PTmp(ProcessEvent):
    # noinspection PyMethodMayBeStatic,PyPep8Naming
    def process_IN_CREATE(self, ev):
        p = join(ev.path, ev.name)
        print('Create: %s' % p)
        f = File.find(p)
        if not f:
            f = File()
            f.path = p
            f.created_at = mkts()
            S.add(f)
        else:
            f.updated_at = mkts()
        f.size = os.path.getsize(p)

    # noinspection PyMethodMayBeStatic,PyPep8Naming
    def process_IN_DELETE(self, ev):
        p = join(ev.path, ev.name)
        print('Remove: %s' % p)
        File.remove(p)

notifier = Notifier(wm, PTmp())
wdd = wm.add_watch(sys.argv[1], mask, rec=True)

while True:  # loop forever
    try:
        # process the queue of events as explained above
        notifier.process_events()
        if notifier.check_events():
            # read notified events and enqeue them
            notifier.read_events()
        S.commit()
        print('files: %s' % S.count())
    # you can do some tasks here...
    except KeyboardInterrupt:
        # destroy the inotify's instance on this interrupt (stop monitoring)
        notifier.stop()
        break
