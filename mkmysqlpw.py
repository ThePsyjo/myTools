import hashlib

def mysql_password(_str):
	"""
	Hash string twice with SHA1 and return uppercase hex digest,
	prepended with an asterix.
	
	This function is identical to the MySQL PASSWORD() function.
	"""
	pass1 = hashlib.sha1(_str.encode()).digest()
	pass2 = hashlib.sha1(pass1).hexdigest()
	return '*' + pass2.upper()

if __name__ == '__main__':
	import sys
	for pw in sys.argv[1:]:
		print('%s : "%s"' % (mysql_password(pw), pw))
