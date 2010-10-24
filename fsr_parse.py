#!/usr/bin/python
# 2010 Psyjo

import sys
import re
import operator
import os
import signal

vmap = {}
oldmap = []

valuePattern = re.compile(".*: *([0-9]+) .*: *([0-9]+) .*")
linePattern = re.compile('^extents')

running = 1

def exitHandler():
	print 'Signal 15'
	running = 0
	exit

signal.signal(15, exitHandler)

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
		smap = sorted(vmap.iteritems(), key=operator.itemgetter(1),reverse=True)
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
