#!/usr/bin/env python
######################
# wsstats.py         #
#                    #
# 2011 (c) by Psyjo  #
######################
# Distributed under the terms of the GNU General Public License v2

import ConfigParser, os, MySQLdb, argparse, sys, time
from datetime import datetime, timedelta, date
from threading import Thread, Event

parser = argparse.ArgumentParser(description='Extract stats from webserverlogs')

actionParser = parser.add_argument_group(title='Actions', description='At least one shouls be activated')

actionParser.add_argument('-t', '--traffic', action='append_const', const='traffic', default=[], dest='Actions', help='show incomming and outgoing traffic')
actionParser.add_argument('-R', '--returncode-stats', action='append_const', const='status', default=[], dest='Actions', help='count returncodes')
actionParser.add_argument('-C', '--content', action='append_const', const='content', default=[], dest='Actions', help='content stats')
actionParser.add_argument('-S', '--hoststat', action='append_const', const='hoststat', default=[], dest='Actions', help='host stats')
actionParser.add_argument('-T', '--top', action='append', choices='t to ti v d f all'.split(), default=[], dest='top', help='generate top 10 (-l to modify) for each (traffic out = \'to\' = \'t\', traffic in = \'ti\', views = \'v\', delay = \'d\', files = \'f\' or all trailing = \'all\'')
actionParser.add_argument('--SQL', action='store', dest='query', metavar='\'<query>\'', help='execute \'<query>\'')
actionParser.add_argument('-Q', '--configured_query', action='append', dest='confq', default=[], metavar='<item>', help='execute <item> (\'list\' to list available)')

limitParser = parser.add_argument_group(title='Limiters', description='Limit Database search to the given limits')

from_group = limitParser.add_mutually_exclusive_group()
until_group = limitParser.add_mutually_exclusive_group()

from_group.add_argument('-f', '--from', action='store', dest='time_from', metavar='<datetime>', help='results beginning this time ("Y-m-d H:M:S")')
from_group.add_argument('-j', '--today', action='store_const', dest='time_from', const=date.today().isoformat()+' 00:00:00', help='Alias for "-f \'<today> 00:00:00\'"')
from_group.add_argument('-L', '--last', action='store', dest='time_last', metavar='<time>', help='results in the last <time> (H:M:S)')
from_group.add_argument('-y', '--yesterday', action='store', dest='yesterdays', metavar='<days>', nargs='?', type=int, const=1, help='results from yesterday <days> days ago (this will override -u/--until)')
until_group.add_argument('-u', '--until', action='store', dest='time_until', metavar='<datetime>', help='results until this time ("Y-m-d H:M:S")')

limitParser.add_argument('-l', '--limit', action='store', dest='resultLimit', metavar='N', help='limit to N results')
limitParser.add_argument('-H', '--host', action='store', dest='host', metavar='hostname', help='results relating to hostname')
limitParser.add_argument('-s', '--site', action='store', dest='site', metavar='sitename', help='results relating to sitename')
limitParser.add_argument('-i', '--ip', action='store', dest='ip', metavar='remote-ip', help='results relating to remote-ip')
limitParser.add_argument('-w', '--where', action='append', dest='awhere', default=[], metavar='\'condition\'', help='filter by given condition(s). i.e. -w \'bytes_send > 1000\'')

code_group = limitParser.add_mutually_exclusive_group()
code_group.add_argument('-o', '--200', action='store_true', dest='ok200', help='results with returncode 200')
code_group.add_argument('-n', '--not200', action='store_true', dest='notok200', help='results w/o returncode 200')
code_group.add_argument('-r', '--returncode', action='append', dest='returncode', default=[], metavar='<code>', help='only results with returncode <code>')

miscParser = parser.add_argument_group(title='Miscellaneous', description='Other stuff')

miscParser.add_argument('--config', action='store', dest='configFile', 
	default=os.path.join(os.path.dirname(sys.argv[0]) if os.name != 'posix' else '/etc/','wsstats.cfg'),
	metavar='<file>',
	help='use <file> as configuration')
miscParser.add_argument('--debug', action='store_true', dest='dbg', default=False, help='Show some dev information')
miscParser.add_argument('--outformat', action='store', dest='outformat', choices='ascii html'.split(), default='ascii', help='Output with specific format')
miscParser.add_argument('--test', action='store_true', dest='test')


parsed = parser.parse_args()

config = ConfigParser.ConfigParser()
try:
	config.readfp(open(parsed.configFile))
except Exception as msg:
	print (msg)
	exit()

if parsed.top: parsed.Actions.append('top')
if parsed.query: parsed.Actions.append('query')
if parsed.confq: parsed.Actions.append('confq')

parsed.confq = set(parsed.confq)
parsed.top = set(parsed.top)

if 'all' in parsed.top:
	parsed.top = 'to ti v d f'.split()

qwhere = []

def tpart(f): return int(parsed.time_last.split(':')[f])
try:
	from_dt  = ''
	until_dt = ''
	if parsed.time_last: from_dt   = (datetime.now() - timedelta(hours=tpart(0), minutes=tpart(1), seconds=tpart(2))).strftime('%Y-%m-%d %H:%M:%S')
	if parsed.time_from: from_dt   = datetime.strptime(parsed.time_from,  "%Y-%m-%d %H:%M:%S").isoformat(' ')
	if parsed.time_until: until_dt = datetime.strptime(parsed.time_until, "%Y-%m-%d %H:%M:%S").isoformat(' ')
	# override both if parsed.yesterdays is set
	if parsed.yesterdays:
		qwhere.append('datetime >= CURDATE() - INTERVAL {0} DAY'.format(parsed.yesterdays))
		qwhere.append('datetime <= CURDATE() - INTERVAL {0} DAY'.format(parsed.yesterdays - 1))
		from_dt = until_dt = ''
except ValueError as msg:
	print (msg)
	exit()

if from_dt:		qwhere.append('datetime >= \'' + from_dt  + '\'')
if until_dt:		qwhere.append('datetime <= \'' + until_dt + '\'')
if parsed.site:		qwhere.append('site LIKE \'' + parsed.site + '%\'')
if parsed.host:		qwhere.append('host LIKE \'' + parsed.host + '%\'')
if parsed.ip:		qwhere.append('remote_ip LIKE \'' + parsed.ip + '\'')
if parsed.ok200:	qwhere.append('status = 200')
if parsed.notok200:	qwhere.append('status != 200')

if parsed.returncode:
	qwhere.append('(' + ' OR '.join(['status LIKE \'' + code + '\'' for code in parsed.returncode]) + ')')

for condition in parsed.awhere:
	qwhere.append(condition)

qwhere = 'WHERE ' + ' AND '.join(qwhere) if qwhere else ''

limit = (' LIMIT ' + parsed.resultLimit) if parsed.resultLimit else ''

class AsciiTable:
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

def htmlTable(titles, headers, rows):
	out = ['<div id="floating-box"><div id="tbl"><div id="tblcaption">' + titles + '</div><div id="headrow">']
	for header in headers:
		out.append('<div id="headitem">' + header + '</div>')
	out.append('</div>')

	odd = False
	for row in rows:
		if odd:
			out.append('<div id="itemrow1">')
			odd = False
		else:
			out.append('<div id="itemrow2">')
			odd = True
		for cell in row:
			out.append('<div id="item">' + str(cell) + '</div>')
		out.append('</div>')
	out.append('</div></div>')
	return '\n'.join(out)

def Table(titles, headers, rows):
	if parsed.outformat == 'ascii':
		return AsciiTable(titles, headers, rows)
	if parsed.outformat == 'html':
		return htmlTable(titles, headers, rows)

if parsed.test:
	print (parsed)
	print (qwhere)
	for cq in parsed.confq:
		try:
			print ('cq: ', config.get('Queries', cq).replace('{{WHERE}}', qwhere + ' AND ' if qwhere else 'WHERE') + limit)
		except Exception as msg:
			print (msg)
	exit()

if 'list' in parsed.confq:
	print (Table('Configured Queries', ['name', 'Query'], config.items('Queries')))
	exit(0)

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
	if c.rowcount > 0:
		printTable(caption, mkTitle(c), c.fetchall())

def printTable(caption, titles, data):
	print (Table(caption, titles, data))

def _humanreadable(div,val):
	affix = ['', 'K', 'M', 'G', 'T', 'P']
	index = 0
	val = float(val) if val else float(0)

	while val > div:
		val /= div
		index += 1

	return ''.join(['{0:.4}'.format(val), affix[index]])

def humanreadable(val):
	return _humanreadable(1000,val)

def humanreadablei(val):
	return _humanreadable(1024,val)

class Twirl(Thread):
        def __init__(self, chars, sleep_time = 0.2):
                Thread.__init__(self)
                self.state = 0
                self.chars = chars
                self.sleep_time = sleep_time
                self.running = True
                self.ev = Event()
		self.output = False

        def run(self):
		self.ev.wait(2)
		self.output = True
		if self.running:
	                sys.stdout.write(' '*len(self.chars[self.state]))
                while self.running:
                        for self.state in range(len(self.chars)):
                                if self.running:
                                        sys.stdout.write('\b'*len(self.chars[self.state]) + self.chars[self.state])
                                        sys.stdout.flush()
                                        self.ev.wait(self.sleep_time)
                                else:   break

        def stop(self):
                self.running = False
		if self.output:
	                sys.stdout.write('\b'*len(self.chars[self.state]) + ' '*len(self.chars[self.state]) + '\b'*len(self.chars[self.state]))
			sys.stdout.flush()
                self.ev.set()
                self.join()

def mkTwirl():
	return Twirl(['.  ', '.. ', '...',' ..','  .','   ',])

def doQuery(q):
	if parsed.dbg:
		print (q)
	tw = mkTwirl()
	tw.start()
	try: cursor.execute(q)
	except Exception as msg:
		print (msg)
	finally:
		tw.stop()

try:
	conn = MySQLdb.connect( host = config.get('DB', 'host'), user = config.get('DB', 'user'), passwd = config.get('DB', 'password'))
	cursor = conn.cursor();
	conn.select_db(config.get('DB', 'database'))
except Exception as msg:
	print (msg)
	exit()

if parsed.outformat == 'html':
	print ('<html><head><STYLE type="text/css">\n#floating-box {float:left; padding: 3px;}\n#tbl {display: table; border-width: 3px; border: solid}\n#tblcaption {display: table-caption; text-align: center; background: #FFFFD7}\n#headrow {display: table-row; background: #D7FFAF; border-bottom: 3px solid;}\n#headitem {display: table-cell; padding:2px 5px; border-right: .5px solid; border-left: .5px solid; border-bottom: 1px solid;}\n#itemrow1 {display: table-row; background: #C6E1FF}\n#itemrow2 {display: table-row; background: #8FA2B8}\n#item {display: table-cell; padding:2px 5px; border-right: .5px solid; border-left: .5px solid;}</STYLE></head><body>')

for Action in parsed.Actions:
	if Action is 'traffic':
		doQuery('SELECT SUM(bytes_sent) outbound, SUM(bytes_received) inbound FROM ' + config.get('DB', 'table') + ' ' + qwhere)
		Data = cursor.fetchall()
		printTable('Traffic Stats', mkTitle(cursor), mkData(Data,[0,1], 'i'))

	if Action is 'status':
		doQuery('SELECT status,COUNT(status) cnt,COUNT(status) alias FROM ' + config.get('DB', 'table') + ' ' + qwhere + ' GROUP BY status ORDER BY cnt DESC' + limit)
		printTable('Returncode Stats', mkTitle(cursor), mkData(cursor.fetchall(), [2], 'n'))

	if Action is 'content':
		doQuery('SELECT content_type,COUNT(content_type) cnt,COUNT(content_type) alias FROM ' + config.get('DB', 'table') + ' ' + qwhere + ' GROUP BY content_type ORDER BY cnt DESC' + limit)
		printTable('Content Stats', mkTitle(cursor), mkData(cursor.fetchall(), [2], 'n'))

	if Action is 'hoststat':
		doQuery('SELECT host,COUNT(host) cnt, COUNT(host) alias FROM ' + config.get('DB', 'table') + ' ' + qwhere + ' GROUP BY host ORDER BY cnt DESC' + limit)
		printTable('Host Stats', mkTitle(cursor), mkData(cursor.fetchall(), [2], 'n'))

	if Action is 'query':
		doQuery(parsed.query)
		printTableC('Sql', cursor)

	if Action is 'confq':
		for cq in parsed.confq:
			try:
				doQuery(config.get('Queries', cq).replace('{{WHERE}}', qwhere + ' AND ' if qwhere else 'WHERE') + limit)
				printTableC(cq, cursor)
			except Exception as msg:
				print (msg)

	if Action is 'top':
		toplimit = limit if limit else ' LIMIT 10'
		def mkTopCaption(text):
			return ' Top' + toplimit.split()[1] +' '+ text

		for top in parsed.top:
			if top == 't' or top == 'to':
				doQuery('SELECT site,SUM(bytes_sent) data FROM ' + config.get('DB', 'table') + ' ' + qwhere + ' GROUP BY site ORDER BY data DESC' + toplimit)
				printTable(mkTopCaption('Traffic Outbound'), mkTitle(cursor), mkData(cursor.fetchall(), [1], 'i'))

			if top == 'ti':
				doQuery('SELECT site,SUM(bytes_received) data FROM ' + config.get('DB', 'table') + ' ' + qwhere + ' GROUP BY site ORDER BY data DESC' + toplimit)
				printTable(mkTopCaption('Traffic Inbound'), mkTitle(cursor), mkData(cursor.fetchall(), [1], 'i'))

			if top == 'v':
				doQuery('SELECT site,COUNT(site) cnt,COUNT(site) alias FROM ' + config.get('DB', 'table') + ' ' + qwhere + ' GROUP BY site ORDER BY cnt DESC' + toplimit)
				printTable(mkTopCaption('Views'), mkTitle(cursor), mkData(cursor.fetchall(), [2], 'n'))

			if top == 'd':
				doQuery('SELECT site,SUM(delay) delay FROM ' + config.get('DB', 'table') + ' ' + qwhere + ' GROUP BY site ORDER BY delay DESC' + toplimit)
				printTable(mkTopCaption('Time'), mkTitle(cursor), mkData(cursor.fetchall(), [1], 'time'))

			if top == 'f':
				doQuery('SELECT site,url,COUNT(site) cnt,COUNT(site) alias FROM ' + config.get('DB', 'table') + ' ' + qwhere + ' GROUP BY url ORDER BY cnt DESC' + toplimit)
				printTable(mkTopCaption('Files'), mkTitle(cursor), mkData(cursor.fetchall(), [3], 'n'))

if parsed.outformat == 'html':
	print ('</body></html>')
cursor.close()
conn.close()

