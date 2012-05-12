#!/usr/bin/env python
#####################
# pu.py             #
# PsyjoUtil         #
#                   #
# 2012 (c) by Psyjo #
#####################
# Distributed under the terms of the GNU General Public License v2

import sys
import re

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
actionParser.add_argument('-r', '--rdp', action='store', dest='dst_rdp', metavar='<target>', help='Connect via rdesktop. Use "list" to get a list of available targets.')


optionParser = parser.add_argument_group(title='Options', description='optional arguments')
optionParser.add_argument('-C', '--command', action='store', dest='ssh_remote_command', metavar='<command>', help='Pass this command to the target. To be used with -c/--conn')
optionParser.add_argument('-u', '--user', action='store', dest='user', help='Login with this user. To be used with -r/--rdp')
optionParser.add_argument('-p', '--password', action='store', dest='password', help='Login with this password. To be used with -r/--rdp')
optionParser.add_argument('-P', '--port', action='store', dest='port', help='Use this Port. To be used with -c/--conn')
optionParser.add_argument('-x', '--context', action='store', dest='context', default='', help='use this destination context')

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
		self.userArg = ''
		self.passwordArg = ''
		self.portArg = ''
		#self.regex = re.compile('((?P<login>\w+)(:(?P<password>\w+))?@)?(?P<host>[^:@]+)(:(?P<port>\d+))?')
		self.regex = re.compile('((?P<login>[^:@]+)(:(?P<password>[^@]+))?@)?(?P<host>[^:@]+)(:(?P<port>\d+))?')
		self.context = ''

	def setSection(self, section):
		self.section = section

	def setContext(self, context):
		self.context = context

	def getList(self):
		if not self.section:
			raise ValueError('section not set')
		if self.context != '':
			print (Table('destinations', ['name', 'destination'], [itm for itm in config.items(self.section) if re.match('^%s\.' % self.context, itm[0])]))
		else:
			print (Table('destinations', ['name', 'destination'], [itm for itm in config.items(self.section)]))

	def suggestTarget(self, keyword):
		if keyword == 'list':
			self.getList()
			exit(0)

		if self.context != '':
			l = dict(itm for itm in config.items(self.section) if re.match('^%s.' % self.context, itm[0]))
		else:
			l = dict(config.items(self.section))

		try:
			self.value = l[keyword]
		except:
			if self.context != '':
				self.suggest = [itm for itm in l if re.match('^%s\..*%s.*' % (self.context, keyword) , itm)]
			else:
				self.suggest = [itm for itm in l if keyword in itm]

			if len(self.suggest) == 1:
				self.target = self.suggest.pop()
				self.value = l[self.target]
				print ('assuming "%s" is the right target' % self.target)
			else:
				print ('"%s" not found.' % keyword)
				if len(self.suggest) > 0:
					print ('You may mean one of the following:')
					print (Table('matching', ['name', 'address'], [[itm, l[itm]] for itm in  self.suggest]))
				exit(1)

		#return self.value
		self.value = self.regex.match(self.value).groupdict()
		#print self.value

	def getHost(self):
		return self.value['host']
	def getUser(self):
		return self.value['login']
	def getPassword(self):
		return self.value['password']
	def getPort(self):
		return self.value['port']

	def getArgs(self):
		try: self.args = config.get('%s_Options' % self.section, 'args')
		except: self.args = ''
		return self.args

	def getUserArg(self):
		try: self.userArg = config.get('%s_Options' % self.section, 'userArg')
		except:
			print('"userArg" not set in section %s !' % '"%s_Options"' % self.section)
			sys.exit(1)
		return self.userArg

	def getPasswordArg(self):
		try: self.passwordArg = config.get('%s_Options' % self.section, 'passwordArg')
		except:
			print('"passwordArg" not set in section %s !' % '"%s_Options"' % self.section)
			sys.exit(1)
		return self.passwordArg

	def getPortArg(self):
		try: self.portArg = config.get('%s_Options' % self.section, 'portArg')
		except:
			print('"portArg" not set in section %s !' % '"%s_Options"' % self.section)
			sys.exit(1)
		return self.portArg

	def getBin(self):
		try: self.args = config.get('%s_Options' % self.section, 'bin')
		except:
			print('"bin" not set in section %s !' % '"%s_Options"' % self.section)
			exit(1)
		return self.args

	def concat(self, glue, one, two):
		return '%s%s%s' % ( one, glue, two )

	def quote(self, txt, tryQuote = 1):
		if tryQuote:
			if '"' in txt or "'" not in txt:	return "'%s'" % txt
			elif "'" in txt or '"' not in txt:	return '"%s"' % txt
			else:					return txt
		else:	return txt

	def mkPortArg(self, port):
		if port:		return self.concat(' ', self.getPortArg(), port)
		elif self.getPort():	return self.concat(' ', self.getPortArg(), self.getPort())
		else:			return ''

	def mkUserArg(self, user):
		if user:		return self.concat(' ', self.getUserArg(), user)
		elif self.getUser():	return self.concat(' ', self.getUserArg(), self.getUser())
		else:			return ''

	def mkPasswordArg(self, password):
		if password:		return self.concat(' ', self.getPasswordArg(), self.quote(password))
		elif self.getPassword():return self.concat(' ', self.getPasswordArg(), self.quote(self.getPassword()))
		else:			return ''

	def mkHostPort(self, port):
		if port:		return self.concat(':', self.getHost(), port)
		elif self.getPort():	return self.concat(':', self.getHost(), self.getPort())
		else:			return self.getHost()

p = Dataparser()
p.setContext(parsed.context)

if parsed.dst_ssh:
	p.setSection('SSH')
	p.suggestTarget(parsed.dst_ssh)

	os.system('%s %s %s %s %s %s' % (p.getBin(),
					p.getArgs(),
					p.mkPortArg(parsed.port),
					p.mkUserArg(parsed.user),
					p.getHost(),
					'\'%s\'' % parsed.ssh_remote_command if parsed.ssh_remote_command else ''))

if parsed.dst_rdp:
	p.setSection('RDP')
	p.suggestTarget(parsed.dst_rdp)

	os.system('%s %s %s %s %s' % (p.getBin(),
				p.getArgs(),
				p.mkUserArg(parsed.user),
				p.mkPasswordArg(parsed.password),
				p.mkHostPort(parsed.port) ))
