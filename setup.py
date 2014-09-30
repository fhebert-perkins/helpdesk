import os
print "Environment setup"
try:
	import tinydb
except:
	os.system("sudo pip install tinydb")
try:
	import flask
except:
	os.system("sudo pip install flask")
print "Done"
