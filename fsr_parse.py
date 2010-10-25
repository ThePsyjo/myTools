#!/usr/bin/python
# 2010 Psyjo

import sys
import re
import operator
import os
import signal

vmap = {}
smap = []
oldmap = []

valuePattern = re.compile(".*: *([0-9]+) .*: *([0-9]+) .*")
linePattern = re.compile('^extents')
keyPattern = re.compile('from_([0-9]+).*')

running = 1

def exitHandler():
	global running
	print 'Signal 15'
	running = 0

signal.signal(15, exitHandler)

def comparekeys(x, y):
        return int(keyPattern.match(y[0]).group(1)) - int(keyPattern.match(x[0]).group(1))

def genSmap():
	global oldmap
	global smap
	# v makes the list correct soerted but slow
	smap = sorted(vmap.iteritems(), cmp=comparekeys)
	smap = sorted(smap, key=operator.itemgetter(1), reverse=True)

def dspl():
	global oldmap
	global smap
	genSmap()
	if oldmap == map(operator.itemgetter(0), smap):
		os.system('tput cup 0 0')
	else:
		os.system('clear')
	oldmap = map(operator.itemgetter(0), smap)
	cnt = 0
	for k, v in smap:
		cnt += 1
		if cnt > 50:
			break
		print k, '\t', v

while running == 1:
	line = sys.stdin.readline()
	if len(line) == 0:
		break
	else:
		print line,
		if linePattern.search(line):
			m = valuePattern.match(line)
			str = 'from_' + m.group(1) + '_to_' + m.group(2)
			if str in vmap:
				vmap[str] += 1
			else:
				vmap[str] = 1
		else:
			continue
		dspl()

os.system('clear')
print '=' * 47
print '=' * 20, ' sum ', '=' * 20
print '=' * 47
genSmap()
for k, v in smap:
	print k, '\t', v
