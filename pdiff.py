import sys

from difflib import SequenceMatcher
f1 = open(sys.argv[1]).read()
f2 = open(sys.argv[2]).read()
m = SequenceMatcher(None, f1, f2)
print(m.ratio()*100)

