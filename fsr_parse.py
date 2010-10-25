#!/usr/bin/python
# 2010 Psyjo

import sys
import re
import operator
import os
import signal
import getopt

vmap = {}
smap = []
oldmap = []

valuePattern = re.compile(".*: *([0-9]+) .*: *([0-9]+) .*")
linePattern = re.compile('^extents')

running = 1

def exitHandler():
	global running
	print 'Signal 15'
	running = 0

signal.signal(15, exitHandler)

def genSmap():
	global oldmap
	global smap
	smap = sorted(vmap.iteritems(), reverse=True)
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

def usage():
	print 'usage:\n', sys.argv[0], '[-h|--help] [-p|--print] [-s|--skip-summary]'

try:
	opts, args = getopt.getopt(sys.argv[1:], "hps", ["print", "help", "skip-summary"])
except getopt.GetoptError, err:
	print str(err) # will print something like "option -a not recognized"
	usage()
	sys.exit(2)
help = False
printout = False
summary = True
for o, a in opts:
	if o in ("-h", "--help"):
		usage()
		sys.exit()
	elif o in ("-p", "--print"):
		printout = True
	elif o in ("-s", "--skip-summary"):
		summary = False
	else:
		assert False, "unhandled option"


while running == 1:
	line = sys.stdin.readline()
	if len(line) == 0:
		break
	else:
		if printout:
			print line,
		if linePattern.search(line):
			m = valuePattern.match(line)
			value = float(m.group(1) + '.' + m.group(2))
			if value in vmap:
				vmap[value] += 1
			else:
				vmap[value] = 1
		else:
			continue
		if printout:
			dspl()

if summary:
	os.system('clear')
	print '=' * 47
	print '=' * 20, ' sum ', '=' * 20
	print '=' * 47
	genSmap()
	for k, v in smap:
		print k, '\t', v
