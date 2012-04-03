#!/usr/bin/env python
#####################
# pu.py             #
# PsyjoUtil         #
#                   #
# 2012 (c) by Psyjo #
#####################
# Distributed under the terms of the GNU General Public License v2

import sys

if  sys.version_info < (2,6):
        print ('Python is too old here. Upgrade at least to 2.6!')
        sys.exit(1);
else:
        if sys.version_info < (3,0): import ConfigParser
        else: import configparser as ConfigParser

import os, argparse, time
from datetime import datetime, timedelta, date



parser = argparse.ArgumentParser(description='blah')


actionParser = parser.add_argument_group(title='Actions', description='At least one should be activated')
actionParser.add_argument('-c', '--conn', action='store', dest='dst_ssh', metavar='<target>', help='Connect via ssh. Use "list" to get a list of available targets.')
actionParser.add_argument('-C', '--command', action='store', dest='ssh_remote_command', metavar='<command>', help='Pass this command to the target. If not used with -c/--conn it will be ignored')
actionParser.add_argument('-r', '--rdp', action='store', dest='dst_rdp', metavar='<target>', help='Connect via rdesktop. Use "list" to get a list of available targets.')


miscParser = parser.add_argument_group(title='Miscellaneous', description='Other stuff')
miscParser.add_argument('--config', action='store', dest='configFile',
        default=os.path.join(os.path.dirname(sys.argv[0]) if os.name != 'posix' else os.path.expanduser('~'), '.pu/config.ini'),
        metavar='<file>',
        help='use <file> as configuration')
miscParser.add_argument('--debug', action='store_true', dest='dbg', default=False, help='Show some dev information')
miscParser.add_argument('--test', action='store_true', dest='test')


parsed = parser.parse_args()

if parsed.test:
        print (parsed)
	exit()

config = ConfigParser.ConfigParser()
try:
        config.readfp(open(parsed.configFile))
except Exception as msg:
        print (msg)
        exit()


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

class Dataparser:
	def __init__(self, section = None):
		self.section = section
		self.value = ''
		self.suggest = ''
		self.target = ''
		self.enum = []
		self.args = ''

	def setSection(self, section):
		self.section = section

	def getList(self):
		if not self.section:
			raise ValueError('section not set')
		print (Table('destinations', ['name', 'destination'], config.items(self.section)))

	def suggestTarget(self, keyword):
		if keyword == 'list':
			self.getList()
			exit(0)

		try:
			self.value = config.get(self.section, keyword)
		except:
			self.suggest = [itm for itm in config.options(self.section) if keyword in itm]
			if len(self.suggest) == 1:
				self.target = self.suggest.pop()
				self.value = config.get(self.section, self.target)
				print ('assuming "%s" is the right target' % self.target)
			else:
				print ('"%s" not found.' % keyword)
				if len(self.suggest) > 0:
					for i, v in enumerate(self.suggest): self.enum.append([i,v])
					print ('You may mean one of the following:')
					print (Table('matching', ['#', 'destination'], self.enum))
				exit(1)

		return self.value

	def getArgs(self):
		try: self.args = config.get('%s_Options' % self.section, 'args')
		except: self.args = ''
		return self.args

	def getBin(self):
		try: self.args = config.get('%s_Options' % self.section, 'bin')
		except:
			print('Binary file at section %s not set!' % self.section)
			exit(1)
		return self.args

p = Dataparser()

if parsed.dst_ssh:
	p.setSection('SSH')
	#print('ssh %s %s %s' % (p.getArgs(), p.suggestTarget(parsed.dst_ssh), '\'%s\'' % parsed.ssh_remote_command if parsed.ssh_remote_command else ''))
	os.system('ssh %s %s %s' % (p.getArgs(), p.suggestTarget(parsed.dst_ssh), '\'%s\'' % parsed.ssh_remote_command if parsed.ssh_remote_command else ''))

if parsed.dst_rdp:
	p.setSection('RDP')
	os.system('%s %s %s' % (p.getBin(), p.getArgs(), p.suggestTarget(parsed.dst_rdp)))
