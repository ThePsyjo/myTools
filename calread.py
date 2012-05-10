from icalendar import Calendar, Event
from datetime import datetime
from os import path

cal = Calendar.from_string(open(path.expanduser('~/.kde/share/apps/ktimetracker/ktimetracker.ics'),'rb').read())

for comp in cal.walk():
	try:	comment = ' (%s)' % str(comp['comment'][1]) if comp['comment'][1] else ''
	except:	comment = ''

	try:
#		print comp
		print('%s - %s\t%s%s' % ( datetime.strptime(str(comp['dtstart']),
						'%Y%m%dT%H%M%S').isoformat(' '), datetime.strptime(str(comp['dtend']),
						'%Y%m%dT%H%M%S').isoformat(' '),
						str(comp['summary']),
						comment
					))
	except:
		pass
