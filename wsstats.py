######################
# wsstats.py         #
#                    #
# 2011 (c) by Psyjo  #
######################
# Distributed under the terms of the GNU General Public License v2
"""
CREATE TABLE `apachelog` (
  `datetime` datetime DEFAULT NULL,
  `filename` text,
  `requestmethod` varchar(8) DEFAULT NULL,
  `remote_ip` varchar(15) DEFAULT NULL,
  `remote_user` varchar(128) DEFAULT NULL,
  `site` varchar(64) DEFAULT NULL,
  `host` varchar(64) DEFAULT NULL,
  `url` text,
  `status` smallint(6) NOT NULL,
  `bytes_sent` int(10) unsigned DEFAULT NULL,
  `bytes_received` int(10) unsigned DEFAULT NULL,
  `delay` int(10) unsigned DEFAULT NULL,
  `referer` text,
  `content_type` varchar(32) DEFAULT NULL,
  `seq` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`seq`),
  KEY `site` (`site`),
  KEY `host` (`host`),
  KEY `datetime` (`datetime`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

INSERT INTO apachelog (datetime, filename, requestmethod, remote_ip, remote_user, site, host, url, status, bytes_sent, bytes_received, delay, referer, content_type)\
	VALUES ('%{%Y-%m-%d %H:%M:%S}t', '%f', '%m', '%a', '%u', '%{Host}i', '%v', '%U%q', '%s', '%B', '%I', '%D', '%{Referer}i', '%{Content-Type}o');
"""

import ConfigParser, os, MySQLdb, argparse, sys, decimal
from datetime import datetime, timedelta, date

parser = argparse.ArgumentParser(description='Extract stats from webserverlogs')

parser.add_argument('-t', '--traffic', action='append_const', const='traffic', default=[], dest='Actions', help='show incomming and outgoing traffic')
parser.add_argument('-R', '--returncode-stats', action='append_const', const='status', default=[], dest='Actions', help='count returncodes')
parser.add_argument('-C', '--content', action='append_const', const='content', default=[], dest='Actions', help='content stats')
parser.add_argument('-S', '--hoststat', action='append_const', const='hoststat', default=[], dest='Actions', help='host stats')
parser.add_argument('-l', '--limit', action='store', dest='resultLimit', metavar='N', help='limit to N results')
parser.add_argument('-T', '--top', action='append', choices='t to ti v d f all'.split(), default=[], dest='top', help='generate top x (-l) for each (traffic = \'t\', traffic out = \'to\', traffic in = \'ti\', views = \'v\', delay = \'d\', files = \'f\' or all trailing = \'all\'')

parser.add_argument('--SQL', action='store', dest='query', metavar='\'<query>\'', help='execute \'<query>\'')

dt_group = parser.add_mutually_exclusive_group()
dt_group.add_argument('-f', '--from', action='store', dest='time_from', metavar='<datetime>', help='results beginning this time ("Y-m-d H:M:S")')
dt_group.add_argument('-j', '--today', action='store_const', dest='time_from', const=date.today().isoformat()+' 00:00:00', help='Alias for "-f \'<today> 00:00:00\'"')
dt_group.add_argument('-L', '--last', action='store', dest='time_last', metavar='<time>=0:10:0', help='results in the last <time> (H:M:S)')
parser.add_argument('-u', '--until', action='store', dest='time_until', metavar='<datetime>', help='results until this time ("Y-m-d H:M:S")')

parser.add_argument('-H', '--host', action='store', dest='host', metavar='hostname', help='results relating to hostname')
parser.add_argument('-s', '--site', action='store', dest='site', metavar='sitename', help='results relating to sitename')
parser.add_argument('-i', '--ip', action='store', dest='ip', metavar='remote-ip', help='results relating to remote-ip')

code_group = parser.add_mutually_exclusive_group()
code_group.add_argument('-o', '--200', action='store_true', dest='ok200', help='results with returncode 200')
code_group.add_argument('-n', '--not200', action='store_true', dest='notok200', help='results w/o returncode 200')
code_group.add_argument('-r', '--returncode', action='store', dest='returncode', metavar='<code>', help='only results with returncode <code>')

parser.add_argument('--config', action='store', dest='configFile', default=os.path.join(os.path.dirname(sys.argv[0]),'wsstats.cfg'), metavar='<file>', help='use <file> as configuration')


parsed = parser.parse_args()

config = ConfigParser.ConfigParser()
try:
	config.readfp(open(parsed.configFile))
except Exception as msg:
	print (msg)
	exit()

parsed.Actions += ['top'] if parsed.top else ''
parsed.Actions += ['query'] if parsed.query else ''

parsed.top = set(parsed.top)
if 'all' in parsed.top:
	parsed.top = 'to ti v d f'.split()

def tpart(f): return int(parsed.time_last.split(':')[f])
try:
	from_dt = ''
	from_dt += (datetime.now() - timedelta(hours=tpart(0), minutes=tpart(1), seconds=tpart(1))).strftime('%Y-%m-%d %H:%M:%S') if parsed.time_last  else ''
	from_dt += datetime.strptime(parsed.time_from,  "%Y-%m-%d %H:%M:%S").isoformat(' ') if parsed.time_from  else ''
	until_dt = datetime.strptime(parsed.time_until, "%Y-%m-%d %H:%M:%S").isoformat(' ') if parsed.time_until else ''
except ValueError as msg:
	print (msg)
	exit()

qwhere = ''
qwhere += (' AND datetime >= \'' + from_dt  + '\'' if qwhere else ' WHERE datetime >= \'' + from_dt  + '\'') if from_dt  else ''
qwhere += (' AND datetime <= \'' + until_dt + '\'' if qwhere else ' WHERE datetime <= \'' + until_dt + '\'') if parsed.time_until else ''
qwhere += (' AND site LIKE \'' + parsed.site + '%\'' if qwhere else ' WHERE site LIKE \'' + parsed.site + '%\'') if parsed.site else ''
qwhere += (' AND host LIKE \'' + parsed.host + '%\'' if qwhere else ' WHERE host LIKE \'' + parsed.host + '%\'') if parsed.host else ''
qwhere += (' AND remote_ip LIKE \'' + parsed.ip + '\'' if qwhere else ' WHERE remote_ip LIKE \'' + parsed.cluster + '\'') if parsed.ip else ''
qwhere += (' AND status LIKE \'' + parsed.returncode + '\'' if qwhere else ' WHERE status LIKE \'' + parsed.returncode + '\'') if parsed.returncode else ''
qwhere += (' AND status = 200 ' if qwhere else ' WHERE status = 200 ') if parsed.ok200 else ''
qwhere += (' AND status != 200 ' if qwhere else ' WHERE status != 200 ') if parsed.notok200 else ''

limit = (' LIMIT ' + parsed.resultLimit) if parsed.resultLimit else ''

#print qwhere
#exit()

class Table:
	def __init__(self,title,headers,rows):
		self.title=title
		self.headers=headers
		self.rows=rows
		self.nrows=len(self.rows)
		self.fieldlen=[]

		ncols=len(headers)

		for i in range(ncols):
			max=0
			for j in rows:
				if len(str(j[i]))>max: max=len(str(j[i]))
			self.fieldlen.append(max)

		for i in range(len(headers)):
			if len(str(headers[i]))>self.fieldlen[i]: self.fieldlen[i]=len(str(headers[i]))

		self.width=sum(self.fieldlen)+(ncols-1)*3+4

	def __str__(self):
		bar = '+'
		for i in range(len(self.headers)):
			bar+='-'*(self.fieldlen[i]+2)
			bar+='+'
		title="| "+self.title+" "*(self.width-3-(len(self.title)))+"|"
		out=['+'+'-'*(self.width-2)+'+',title,bar]
		header=""
		for i in range(len(self.headers)):
			header+="| %s" %(str(self.headers[i])) +" "*(self.fieldlen[i]-len(str(self.headers[i])))+" "
		header+="|"
		out.append(header)
		out.append(bar)
		for i in self.rows:
			line=""
			for j in range(len(i)):
				line+="| %s" %(str(i[j])) +" "*(self.fieldlen[j]-len(str(i[j])))+" "
			out.append(line+"|")

		out.append(bar)
		return "\n".join(out)

def mkTitle(c):
	return [d[0] for d in c.description]

def mkData(data, modcol, mode):
	new = []
	for row in data:
		nrow = []
		for i in range(len(row)):
			if i in modcol:
				if mode is 'i':
					nrow.append(humanreadablei(row[i]))
				elif mode is 'time':
					nrow.append(timedelta(microseconds=int(row[i])))
				else:
					nrow.append(humanreadable(row[i]))
			else:
				nrow.append(row[i])
		new.append(nrow)
	return new


def printTableC(caption, c):
	print Table(caption, [d[0] for d in c.description], c.fetchall())

def printTable(caption, titles, data):
	print Table(caption, titles, data)

def _humanreadable(div,val):
	affix = ['', 'K', 'M', 'G', 'T', 'P']
	index = 0
	val = float(val)

	while val > div:
		val /= div
		index += 1

	return ''.join(['{0:.4}'.format(float(val if val else 0)), affix[index]])

def humanreadable(val):
	return _humanreadable(1000,val)

def humanreadablei(val):
	return _humanreadable(1024,val)

try:
	conn = MySQLdb.connect( host = config.get('DB', 'host'), user = config.get('DB', 'user'), passwd = config.get('DB', 'password'))
	cursor = conn.cursor();
	conn.select_db(config.get('DB', 'database'))
except Exception as msg:
	print (msg)
	exit()

for Action in parsed.Actions:
	if Action is 'traffic':
		cursor.execute('SELECT SUM(bytes_sent) outbound, SUM(bytes_received) inbound FROM apachelog ' + qwhere)
		Data = cursor.fetchall()
		printTable('Traffic Stats', mkTitle(cursor), mkData(Data,[0,1], 'i'))

	if Action is 'status':
		cursor.execute('SELECT status,COUNT(status) cnt,COUNT(status) alias FROM apachelog ' + qwhere + ' GROUP BY status ORDER BY cnt DESC' + limit)
		printTable('Returncode Stats', mkTitle(cursor), mkData(cursor.fetchall(), [2], 'n'))

	if Action is 'content':
		cursor.execute('SELECT content_type,COUNT(content_type) cnt,COUNT(content_type) alias FROM apachelog ' + qwhere + ' GROUP BY content_type ORDER BY cnt DESC' + limit)
		printTable('Content Stats', mkTitle(cursor), mkData(cursor.fetchall(), [2], 'n'))

	if Action is 'hoststat':
		cursor.execute('SELECT host,COUNT(host) cnt, COUNT(host) alias FROM apachelog ' + qwhere + ' GROUP BY host ORDER BY cnt DESC' + limit)
		printTable('Host Stats', mkTitle(cursor), mkData(cursor.fetchall(), [2], 'n'))

	if Action is 'query':
		try:
			cursor.execute(parsed.query)
		except Exception as msg:
			print (msg)
			continue
		printTableC('Sql', cursor)

	if Action is 'top':
		toplimit = limit if limit else ' LIMIT 10'
		def mkTopCaption(text):
			return ' Top' + toplimit.split()[1] +' '+ text

		for top in parsed.top:
			if top == 't' or top == 'to':
				cursor.execute('SELECT site,SUM(bytes_sent) data FROM apachelog ' + qwhere + ' GROUP BY site ORDER BY data DESC' + toplimit)
				printTable(mkTopCaption('Traffic Outbound'), mkTitle(cursor), mkData(cursor.fetchall(), [1], 'i'))

			if top == 'ti':
				cursor.execute('SELECT site,SUM(bytes_received) data FROM apachelog ' + qwhere + ' GROUP BY site ORDER BY data DESC' + toplimit)
				printTable(mkTopCaption('Traffic Inbound'), mkTitle(cursor), mkData(cursor.fetchall(), [1], 'i'))

			if top == 'v':
				cursor.execute('SELECT site,COUNT(site) cnt,COUNT(site) alias FROM apachelog ' + qwhere + ' GROUP BY site ORDER BY cnt DESC' + toplimit)
				printTable(mkTopCaption('Views'), mkTitle(cursor), mkData(cursor.fetchall(), [2], 'n'))

			if top == 'd':
				cursor.execute('SELECT site,SUM(delay) delay FROM apachelog ' + qwhere + ' GROUP BY site ORDER BY delay DESC' + toplimit)
				printTable(mkTopCaption('Time'), mkTitle(cursor), mkData(cursor.fetchall(), [1], 'time'))

			if top == 'f':
				cursor.execute('SELECT site,url,COUNT(site) cnt,COUNT(site) alias FROM apachelog ' + qwhere + ' GROUP BY url ORDER BY cnt DESC' + toplimit)
				printTable(mkTopCaption('Files'), mkTitle(cursor), mkData(cursor.fetchall(), [3], 'n'))
cursor.close()
conn.close()

