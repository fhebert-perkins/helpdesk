import os

print "This only works on ubuntu based system and only installs the python deps."
print "This may require the root password."
print "It will create a virtualenv and install pip on the system"

try:
	import pip
except:
	os.system("sudo apt-get install python-pip")
try:
	import virtualenv
except:
	os.system("sudo apt-get install virtualenv")
os.system("virtualenv venv")
os.system("source venv/bin/activate")
try:
	import flask
except:
	os.system("pip install flask")
try:
	import pymongo
except:
	os.system("pip install pymongo")

os.system("pip install -r requirements.txt")
os.system("cp default_config.json config.json")
print "####reqs done installing####"
print "You will need to edit the config.json file with the servers email credentials"
