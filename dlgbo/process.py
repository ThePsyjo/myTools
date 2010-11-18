#!/bin/bash
#########################################################################
# process.py                                                            #
# Copyright (C) 2010  Psyjo                                             #
#                                                                       #
# This program is free software; you can redistribute it and/or modify  #
# it under the terms of the GNU General Public License as published by  #
# the Free Software Foundation; either version 3 of the License,        #
# or (at your option) any later version.                                #
#                                                                       #
# This program is distributed in the hope that it will be useful, but   #
# WITHOUT ANY WARRANTY; without even the implied warranty of            #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                  #
# See the GNU General Public License for more details.                  #
#                                                                       #
# You should have received a copy of the GNU General Public License     #
# along with this program; if not, see <http://www.gnu.org/licenses/>.  #
#########################################################################

# -*- coding: utf-8 -*-

import re
import os
import getopt
import sys

from xml.dom.minidom import parse

def usage():
        print 'usage:\n', sys.argv[0], '(-i <input dir>|--input=<input dir>) [-h|--help] [-o <output dir>|--out=<output dir>] [-d <data dir>|--data=<data dir>]'

try:
        opts, args = getopt.getopt(sys.argv[1:], "d:hi:o:", ["input=", "help", "output=", "data="])
except getopt.GetoptError, err:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
help = False
input = ''
output = ''
datadir= ''
for o, a in opts:
        if o in ("-h", "--help"):
                usage()
                sys.exit()
        elif o in ("-i", "--input"):
                input = a
        elif o in ("-o", "--output"):
                output = a
	elif o in ("-d", "--data"):
		datadir = a
        else:
		assert False, "unhandled option"

if not input:
	#input = "./raw/"
	print 'input-dir needs to be set !'
	sys.exit(1)
if not output:
	output = "./processed/"
if not os.path.isdir(output):
	os.makedirs(output)
if not datadir:
	datadir = './data/'
if not os.path.isdir(datadir):
	os.makedirs(datadir)

_latex_special_chars = {
'$':  u'\\$',
'%':  u'\\%',
'&':  u'\\&',
'#':  u'\\#',
'_':  u'\\_',
'{':  u'\\{',
'}':  u'\\}',
'[':  u'{[}',
']':  u'{]}',
'"':  u"{''}",
'\\': u'\\textbackslash{}',
'~':  u'\\textasciitilde{}',
'<':  u'\\textless{}',
'>':  u'\\textgreater{}',
'^':  u'\\textasciicircum{}',
'`':  u'{}`',   # avoid ?` and !`
'\n': u'\\\\',
'¥' : u'\\textyen{}',
'³' : u'$^3$',
'²' : u'$^2$',
'Â' : '',
#'¤' : u'\\geneuro{}',
}

def escape_latex(s):
	#return u''.join(_latex_special_chars.get(c, c) for c in s)
	return ''.join(_latex_special_chars.get(c, c) for c in s)

def processFile(file):
	try:
		dom = parse( os.path.abspath(input + '/' + infile))   # parse an XML file
	except Exception, e:
		try:
			sys.stdout.write('!')
			sys.stdout.flush()
			os.system('cat ' + os.path.abspath(input + '/' + infile) + ' | col > ' + os.path.abspath(input + '/' + infile) + '.new')
			os.rename ( os.path.abspath(input + '/' + infile) + '.new', os.path.abspath(input + '/' + infile) )
			dom = parse( os.path.abspath(input + '/' + infile))   # parse an XML file
		except Exception, e:
			print '\n\nfilename was',  os.path.abspath(input + '/' + infile), '\n\n'
			raise


	f = open(output + '/' + file, 'w+')

	for node in dom.getElementsByTagName('div'):  # visit every node <div>
		if node.getAttribute('class') == 'zitat':
			# <div class="zitat">
			#  <span class="quote_zeile">...
			for textnode in node.getElementsByTagName('span'):
				if textnode.getAttribute('class') == 'quote_zeile':
					if textnode.firstChild:
						if textnode.firstChild.data:
							for c in textnode.firstChild.data.strip().encode('utf-8') + '\n':
								f.write( escape_latex (c))
	f.close()




count = 0
filelist = os.listdir(input)
print 'extracting text (0..' + str(len(filelist)) + ')...'
for infile in filelist:
	if count % 100 == 0:
		sys.stdout.write(str(count) + '\n')
	else:
		sys.stdout.write('.')
	count += 1
	sys.stdout.flush()
	processFile( infile )
#	if count >= 700:
#		break

print '\nraw data generation done.'



filelist = os.listdir(output)
print 'generating datafiles (0..' + str(len(filelist)) + ')...'

quotecount = 500
filecount = 0
datafile = file

for infile in filelist:
	if quotecount >= 500:
		if not datafile.closed:
			datafile.close()
		filecount += 1

		datafile = open( datadir + '/all_data' + str(filecount) + '.tex', 'w+' )
		print '\nnew datafile', datadir + '/all_data' + str(filecount) + '.tex'
		quotecount = 0
	if quotecount % 100 == 0:
		sys.stdout.write(str(quotecount) + '\n')
	else:
		sys.stdout.write('.')
	sys.stdout.flush()
	datafile.write( '\\gboquote{' + infile + '}\n{\n' + open(output + '/' + infile, "rb").read() + '\n}\n' )
	quotecount += 1

print
