from fabric.api import local
from datetime import datetime

def commit():
	local("pip freeze > requirements.txt")
	local("git add .")
	commit_message = raw_input("commit message: ")
	if commit_message == "":
		commit_message = datetime.now().strftime('%b-%d-%I%M%p-%G')
	local('git commit -m "%s"' % (commit_message))
def test():
	local("python app_tests.py")
