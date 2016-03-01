#!/usr/bin/env python
#####################
# pu.py	            #
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
	if sys.version_info < (3,0): import ConfigParser  # @UnusedImport
	else: import configparser as ConfigParser  # @Reimport

import argparse 
import os
import re

parser = argparse.ArgumentParser(description='blah')

actionParser = parser.add_argument_group(title='Actions', description='At least one should be activated')
actionParser.add_argument('-c', '--conn', action='store', dest='dst_ssh', metavar='<target>', help='Connect via ssh. Use "list" to get a list of available targets.')
actionParser.add_argument('-r', '--rdp', action='store', dest='dst_rdp', metavar='<target>', help='Connect via rdesktop. Use "list" to get a list of available targets.')

optionParser = parser.add_argument_group(title='Options', description='optional arguments')
optionParser.add_argument('-C', '--command', action='store', dest='ssh_remote_command', metavar='<command>', help='Pass this command to the target. To be used with -c/--conn')
optionParser.add_argument('-u', '--user', action='store', dest='user', help='Login with this user. To be used with -r/--rdp')
optionParser.add_argument('-p', '--password', action='store', dest='password', help='Login with this password. To be used with -r/--rdp')
optionParser.add_argument('-d', '--domain', action='store', dest='domain', help='Login using this domain. To be used with -r/--rdp')
optionParser.add_argument('-P', '--port', action='store', dest='port', help='Use this Port. To be used with -c/--conn')
optionParser.add_argument('-x', '--context', action='store', dest='context', default='', help='use this destination context')
optionParser.add_argument('-S', '--show', action='store_const', const=True, dest='show', default=False, help='Show found entry end exit')
optionParser.add_argument('-H', '--show-host', action='store_const', const=True, dest='showHost', default=False, help='Show just the host if found')
optionParser.add_argument('-i', '--ping', action='store_const', const=True, dest='pingHost', default=False, help='Ping the host instead of connecting to it. To be used with -c/--conn')
optionParser.add_argument('-q', '--quiet', action='store_true', dest='quiet', default=False, help='do not print informations')

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
			max_cols=0
			for j in rows:
				if len(str(j[i]))>max_cols: max_cols=len(str(j[i]))
			self.fieldlen.append(max_cols)

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
		#self.regex = re.compile('((?P<user>[^:@]+)(:(?P<password>[^@]+))?@)?(?P<host>[^:@]+)(:(?P<port>\d+))?')
		self.regex = re.compile('(((?P<domain>[^\\\\]+)\\\\)?(?P<user>[^:@]+)(:(?P<password>[^@]+))?@)?(?P<host>[^:@]+)(:(?P<port>\d+))?')
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
				if not parsed.quiet:
					print ('assuming "%s" is the right target' % self.target)
			else:
				print ('"%s" not found.' % keyword)
				if len(self.suggest) > 0:
					print ('You may mean one of the following:')
					print (Table('matching', ['name', 'address'], [[itm, l[itm]] for itm in  self.suggest]))
				exit(1)

		#return self.value
		self.value = self.regex.match(self.value).groupdict()
		if parsed.show:
			print (self.value)
			exit(0)
		if parsed.showHost:
			print (self.value['host'])
			exit(0)
		#print self.value

	def getFromValue(self, key):
		return self.value[key]

	def getHost(self):
		try:
			return self.fmt(self.getFromConfig('targetFmt'), self.getFromValue('host'), None, '')
		except:
			return self.getFromValue('host')

	def getDomain(self):
		return self.getFromValue('domain')
	def getUser(self):
		return self.getFromValue('user')
	def getPassword(self):
		return self.getFromValue('password')
	def getPort(self):
		return self.getFromValue('port')

	def getFromConfig(self, key, default='', msg=True, exit_=True):
		try: value = config.get('%s_Options' % self.section, key)
		except:
			if msg:
				print('"%s" not set in section "%s_Options" !' % ( key, self.section ))
			if exit_:
				sys.exit(1)
			value = default
		return value

	def getArgs(self):
		self.args = self.getFromConfig('args', default='', msg=False, exit_=False)
		return self.args

	def getBin(self):
		return self.getFromConfig('bin')

	def concat(self, glue, one, two):
		return '%s%s%s' % ( one, glue, two )

	def quote(self, txt, tryQuote = 1):
		if tryQuote:
			if '"' in txt or "'" not in txt:	return "'%s'" % txt
			elif "'" in txt or '"' not in txt:	return '"%s"' % txt
			else:					return txt
		else:	return txt

	def mkConcat(self, first, glue, localchoice, configchoice, fallback):
		if localchoice:		return self.concat(glue, first, localchoice)
		elif configchoice:	return self.concat(glue, first, configchoice)
		else:			return fallback
	
	def fmt( self, fmt, localchoice, configchoice, fallback ):
		if localchoice:		return fmt % localchoice
		elif configchoice:	return fmt % configchoice
		else:				return fallback

	def mkPortArg(self, port):
		#return self.mkConcat(self.getFromConfig('portArg'), ' ', port, self.getFromValue('port'), '')
		return self.fmt(self.getFromConfig('portFmt'), port, self.getFromValue('port'), '')
	def mkDomainArg(self, domain):
		#return self.mkConcat(self.getFromConfig('domainArg'), ' ', domain, self.getFromValue('domain'), '')
		return self.fmt(self.getFromConfig('domainFmt'), domain, self.getFromValue('domain'), '')
	def mkUserArg(self, user):
		#return self.mkConcat(self.getFromConfig('userArg'), ' ', user, self.getFromValue('user'), '')
		return self.fmt(self.getFromConfig('userFmt'), user, self.getFromValue('user'), '')
	def mkPasswordArg(self, password):
		#return self.mkConcat(self.getFromConfig('passwordArg'), ' ', password, self.getFromValue('password'), '')
		return self.fmt(self.getFromConfig('passwordFmt'), password, self.getFromValue('password'), '')
	def mkHostPort(self, port):
		return self.mkConcat(self.getHost(), ':', port, self.getFromValue('port'), self.getHost())

p = Dataparser()
p.setContext(parsed.context)

#def print_wrapper(*args, **kwargs):
#	print(*args, **kwargs)
def print_wrapper(s):
	print(s)

if parsed.dst_ssh:
	p.setSection('SSH')
	p.suggestTarget(parsed.dst_ssh)

	if parsed.dbg:
		f = print_wrapper
	else:
		f = os.system
	if parsed.pingHost:
		f('ping %s' % (	p.getHost() ) )
	else:
		f('%s %s %s %s %s %s' % (p.getBin(),
				p.getArgs(),
				p.mkPortArg(parsed.port),
				p.mkUserArg(parsed.user),
				p.getHost(),
				'\'%s\'' % parsed.ssh_remote_command if parsed.ssh_remote_command else ''))

if parsed.dst_rdp:
	p.setSection('RDP')
	p.suggestTarget(parsed.dst_rdp)
	if parsed.dbg:
		f = print_wrapper
	else:
		f = os.system

	f('%s %s %s %s %s' % (p.getBin(),
	#print('%s %s %s %s %s' % (p.getBin(),
				p.getArgs(),
				p.mkUserArg(parsed.user),
				p.mkPasswordArg(parsed.password),
				p.mkHostPort(parsed.port) ))
