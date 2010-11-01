
import os
import time
import sys
import operator
import getopt

tbl = {}

def usage():
        print 'usage:\n', sys.argv[0], '[-h|--help] [-r|--read] [-w|--write]'

try:
        opts, args = getopt.getopt(sys.argv[1:], "hrw", ["help", "read", "write"])
except getopt.GetoptError, err:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
	
help = False
read_enable = False
write_enable = False

for o, a in opts:
        if o in ("-h", "--help"):
                usage()
                sys.exit()
        elif o in ("-r", "--read"):
                read_enable = True
        elif o in ("-w", "--write"):
                write_enable = True
        else:
                assert False, "unhandled option"

if not read_enable and not write_enable:
	read_enable = True
	write_enable = True

try:
	while True:
		#raw = os.popen("cat data | sed '1,2d' | grep -v da0s").read().split('\n')
		raw = os.popen("gstat -b | sed '1,2d' | grep -v da0s").read().split('\n')
		for count in range(0,len(raw)-1):
			disk = raw[count].split()[9]
			r = raw[count].split()[4]
			w = raw[count].split()[7]
			if disk in tbl:
				if read_enable:
					tbl[disk] += float(r)
				if write_enable:
					tbl[disk] += float(w)
			else:
				if read_enable and write_enable:
					tbl[disk] = float(r) + float(w)
				elif write_enable:
					tbl[disk] = float(w)
				elif read_enable:
					tbl[disk] = float(r)
	
		os.system('clear')
		for k, v in sorted(tbl.iteritems(), key=operator.itemgetter(1), reverse=True):
			print k, " = ", v
		time.sleep(1)
except KeyboardInterrupt:
	print
	sys.exit(0)


