#!/usr/bin/env python
######################
# wsstats.py         #
#                    #
# 2012 (c) by Psyjo  #
######################
# Distributed under the terms of the GNU General Public License v2

import sys

if  sys.version_info < (2,6):
        print ('Python is too old here. Upgrade at least to 2.6!')
        sys.exit(1);
else:
        if sys.version_info < (3,0): import ConfigParser
        else: import configparser as ConfigParser

import os, argparse
from time import sleep
from threading import Thread, active_count


parser = argparse.ArgumentParser(description='blah')

parser.add_argument('-s', action='store', dest='fileSize', required=True, help='Generate files with the given size')
parser.add_argument('-n', action='store', dest='numFiles', required=True, help='Generate this amount of files')
parser.add_argument('-o', action='store', dest='outDir', default='.', help='Use this directory. Default is ".".')
parser.add_argument('-p', action='store', dest='maxJobs', default=os.sysconf("SC_NPROCESSORS_ONLN"), help='Run more than one job. Default is the number of cores.')

parsed = parser.parse_args()

maxJobs = int(parsed.maxJobs)
fileSize = parsed.fileSize
numFiles = int(parsed.numFiles)
outDir = parsed.outDir + '/' + fileSize


if not os.path.exists(outDir):
	os.makedirs(outDir)

if not os.path.isdir(outDir):
	print ('something went wrong')
	exit(1)

def rundd(n, outDir, fileSize):
	os.system('dd if=/dev/urandom of=%s/%d bs=%s count=1' % (outDir, n, fileSize))

for n in range(numFiles):
	while  active_count() > maxJobs:
		#print('active count is %d, sleeping' % active_count())
		sleep(1)
	Thread(target=rundd, args=(n,outDir,fileSize)).start()

