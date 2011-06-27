import sys
from difflib import SequenceMatcher
print ('"%s" and "%s" match for %f%%' % (sys.argv[1], sys.argv[2], SequenceMatcher(None, open(sys.argv[1]).read(), open(sys.argv[2]).read()).ratio()*100))
