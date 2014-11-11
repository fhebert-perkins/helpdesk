from fabric.api import local
from tests import add_users
from datetime import datetime

def addusers():
	add_users()
def commit():
	local("pip freeze >> requirements.txt")
	local("git add .")
	local("git commit -m %s" % (datetime.now().strftime('%b-%d-%I%M%p-%G')))
