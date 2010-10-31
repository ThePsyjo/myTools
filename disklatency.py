
import os
import time
import sys
import operator

tbl = {}

try:
	while True:
	
		#raw = os.popen("cat data | sed '1,2d' | grep -v da0s").read().split('\n')
		raw = os.popen("gstat -b | sed '1,2d' | grep -v da0s").read().split('\n')
		for count in range(0,len(raw)-1):
			k = raw[count].split()[9]
			v = raw[count].split()[4]
			if k in tbl:
				tbl[k] += float(v)
			else:
				tbl[k] = float(v)

	
		os.system('clear')
		for k, v in sorted(tbl.iteritems(), key=operator.itemgetter(1), reverse=True):
			print k, " = ", v
		time.sleep(1)
except KeyboardInterrupt:
	print
	sys.exit(0)


