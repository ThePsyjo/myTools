from datetime import datetime, timedelta
from os import path
import re
import argparse

parser = argparse.ArgumentParser(description='blah')

source_parser = parser.add_mutually_exclusive_group(required=True)

source_parser.add_argument('-i', '--ical', action='store', dest='ical')
source_parser.add_argument('-c', '--csv', action='store', dest='csv')
source_parser.add_argument('-l', '--sqlite', action='store', dest='sqlite')

parser.add_argument('-b', '--blocksize', action='store', dest='blocksize', default=900, type=int)
parser.add_argument('-x', '--tudiff', action='store', dest='tudiff', default=1, type=int)
parser.add_argument('-d', '--discount', action='store', dest='discount', default=120, type=int)
parser.add_argument('-P', '--person', action='store', dest='person', required=True)
parser.add_argument('-p', '--prefix', action='store', dest='prefix', default='.*')
parser.add_argument('-X', '--plain', action='store_const', dest='plain', default=False, const=True)
parser.add_argument('-B', '--block', action='store_const', dest='block', default=False, const=True)

parsed = parser.parse_args()

tu = 0
what = ''

def readICal(filename):
	from icalendar import Calendar, Event
	l = []
	#extract data from calendar
	cal = Calendar.from_string(open(path.expanduser(filename),'rb').read())
	for comp in cal.walk():
	#	print comp
		try:	comment = comp['comment'].pop()
		except:	comment = ''
		try:
			if re.match('^%s' % parsed.prefix, comp['summary']):
				l.append([datetime.strptime(str(comp['dtstart']), '%Y%m%dT%H%M%S'), datetime.strptime(str(comp['dtend']), '%Y%m%dT%H%M%S') + timedelta(seconds=59), comp['summary'], comment])
		except:	pass
	return l

def readCSV(filename):
	import csv
	l = []
	for row in csv.reader(open(filename, 'rb'), delimiter=';'):
		if len(row) < 2: continue
		try:	comment = row[3]
		except:	comment = ''
		if re.match('^%s' % parsed.prefix, row[2]):
			l.append([datetime.strptime(row[0], '%Y%m%dT%H%M%S'), datetime.strptime(row[1], '%Y%m%dT%H%M%S'), row[2], comment])
	return l

def readSqlite(filename):
	import sqlite3
	l = []
	db = sqlite3.connect(filename)
	cursor = db.cursor()
	cursor.execute('SELECT time_begin, time_end, description, note FROM tt')
	for row in cursor.fetchall():
		if len(row) < 3: continue
		if re.match('^%s' % parsed.prefix, row[2]):
			l.append([datetime.fromtimestamp(row[0]), datetime.fromtimestamp(row[1]), row[2], row[3]])
	return l

if parsed.csv:
	l = readCSV(parsed.csv)
elif parsed.ical:
	l = readICal(parsed.ical)
elif parsed.sqlite:
	l = readSqlite(parsed.sqlite)
# else: die

def getsortkey(x):
	return x[0]

# sort by start_date
l = sorted(l, key=getsortkey, reverse=False)

block_begin_idx = 0

# test data
#l = [
#[datetime.strptime('20120501T100100', '%Y%m%dT%H%M%S'), datetime.strptime('20120501T100500', '%Y%m%dT%H%M%S'), 'eins', 'blah'],
#[datetime.strptime('20120501T100700', '%Y%m%dT%H%M%S'), datetime.strptime('20120501T100900', '%Y%m%dT%H%M%S'), 'zwei', 'blah'],
#[datetime.strptime('20120501T101200', '%Y%m%dT%H%M%S'), datetime.strptime('20120501T102000', '%Y%m%dT%H%M%S'), 'drei', 'blah'],
#[datetime.strptime('20120501T102100', '%Y%m%dT%H%M%S'), datetime.strptime('20120501T102400', '%Y%m%dT%H%M%S'), 'vier', 'blah'],
#[datetime.strptime('20120501T110100', '%Y%m%dT%H%M%S'), datetime.strptime('20120501T111400', '%Y%m%dT%H%M%S'), 'last', 'blah'],
#[datetime.strptime('20120501T111500', '%Y%m%dT%H%M%S'), datetime.strptime('20120501T111620', '%Y%m%dT%H%M%S'), 'verylast', 'blah'],
#]

future = datetime(3000,1,1,0,0,0)
l.append([future,future,'dummy', 'dummy'])

if parsed.plain:
	for itm in l:
		print '%s - %s\t%s' % ( itm[0].strftime('%Y-%m-%d %H:%M'), itm[1].strftime('%Y-%m-%d %H:%M'), '%s%s' % (itm[2], ' (%s)' % itm[3] if itm[3] else '' ) )
if parsed.block:
	for n in range(len(l)):
		try:
			# current end to next start gt 15min ?
			if ( l[n+1][0] - l[n][1] ) > timedelta(seconds=parsed.blocksize):
				block_end = True
	#			print l[n+1][0] - l[n][1], 'gt 15min'
	#			print 'start-block', block_begin_idx
			else:	block_end = False
		except:
			block_end = True
			pass

		# exit before last dummy
		if n == len(l) - 1:	break

		if block_end:

			# concat summaries
			what = []
			for idx in range(block_begin_idx, n + 1):
				what.append('%s%s' % (l[idx][2], ' (%s)' % l[idx][3] if l[idx][3] else '' ))

			# kill dupes
			what = set(what)

			duration = l[n][1] - l[block_begin_idx][0]

			if duration.seconds > parsed.blocksize:
				discount = parsed.discount
			else:
				discount = 0

			#print duration
			tu = float( (duration.seconds - discount + parsed.blocksize - 1 ) / parsed.blocksize ) / parsed.tudiff
			print('%s;%s;%s;%s;%s' % ( l[block_begin_idx][0].strftime('%Y-%m-%d %H:%M'), l[n][1].strftime('%Y-%m-%d %H:%M'), str(tu).replace('.',','), parsed.person, ', '.join(what)))

			# set new begin_index to next item
			block_begin_idx = n + 1

		else:		continue
