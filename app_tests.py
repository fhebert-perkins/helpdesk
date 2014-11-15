import os
import app
import unittest
import tempfile
from coverage import coverage
from libs import gen_password_arr
cov = coverage(branch=True, omit=['venv/*', 'app_tests.py', "fabfile.py"])
cov.start()

class AppTestCases(unittest.TestCase):
	def setUp(self):
		app.app.config["TESTING"] = True
		app.app.secret_key = os.urandom(32).encode('base_64')
		# uid = app.Users.insert({
		# 					"username" : "test",
		# 					"email" : "test@example.com",
		# 					"fname" : "john",
		# 					"lname" : "doe",
		# 					"password" : gen_password_arr("password"),
		# 					"last_login" : None
		# 				})
		self.app = app.app.test_client()
		# print str(uid)
	def login(self, username, password):
	    return self.app.post('/login', data=dict(
	        username=username,
	        password=password
	    ), follow_redirects=True)
	def add_ticket(self, title, username, text, urgency, vip):
		return self.app.post("/new", data=dict(
			title=title,
			author=username,
			text=text,
			urgency=urgency,
			is_vip=vip
		), follow_redirects=True)

	def test_login(self):
		#Test response with bad username
		rv = self.login("fhebert-perkins16X", "password")
		assert "Error" in rv.data
		rv = self.login("fhebert-perkins16", "PassWord123")
		assert "Error" in rv.data
		rv = self.login("fhebert-perkins16", "password")
		assert "Logged In" in rv.data
	def test_add_ticket(self):
		assert "Redirecting" in self.app.get("/new").data # makes sure that authentication is needed
		self.login("fhebert-perkins16", "password")
		# Bad title
		rv = self.add_ticket("", "fhebert-perkins16", "HERPDERPDERPDERP", 1, False)
		assert "Error creating ticket" in rv.data
		# Bad Username
		rv = self.add_ticket("herpderp", "", "Herpderp", 1, False)
		assert "No such Username cannot create ticket" in rv.data
		# No text
		rv = self.add_ticket("herpderp", "fhebert-perkins16", "", 1, False)
		assert "Error creating ticket" in rv.data
		# Fully formed tickets
		rv = self.add_ticket("herpderp", "fhebert-perkins16", "HERPDERPDERPDERP", 1, False)
		assert "created new ticket id" in rv.data
		rv = self.add_ticket("herpderp", "fhebert-perkins16", "HERPDERPDERPDERP", 2, False)
		assert "created new ticket id" in rv.data
		rv = self.add_ticket("herpderp", "fhebert-perkins16", "HERPDERPDERPDERP", 3, False)
		assert "created new ticket id" in rv.data
		rv = self.add_ticket("herpderp", "fhebert-perkins16", "HERPDERPDERPDERP", 1, True)
		assert "created new ticket id" in rv.data
		rv = self.add_ticket("herpderp", "fhebert-perkins16", "HERPDERPDERPDERP", 2, True)
		assert "created new ticket id" in rv.data
		rv = self.add_ticket("herpderp", "fhebert-perkins16", "HERPDERPDERPDERP", 3, True)
		assert "created new ticket id" in rv.data
		rv = self.add_ticket("herpderp", "fhebert-perkins16", "HERPDERPDERPDERP", 3, "Fish")
		assert "created new ticket id" in rv.data
	def test_empty_db(self):
		assert "Redirecting" in self.app.get("/").data # makes sure that authentication is needed
		self.login("fhebert-perkins16", "password")
		rv1 = self.app.get("/")
		rv2 = self.app.get("/tickets")
		assert rv1.data == rv2.data

	def test_details(self):
		assert "Redirecting" in self.app.get("/details/blarg").data # makes sure that authentication is needed
		self.login("fhebert-perkins16", "password")
		rv = self.app.get("/detail/blarg")
		assert 404 == rv.status_code
	def test_user(self):
		assert "Redirecting" in self.app.get("/user/fhebert-perkins16").data
		assert "Redirecting" in self.app.get("/user/imnotarealuser").data
		self.login("fhebert-perkins16","password")
		rv = self.app.get("/user/fhebert-perkins16")
		assert "%" in rv.data
		assert "/" in rv.data
		rv = self.app.get("/user/imnotarealuserherpderp")
		assert 404 == rv.status_code
	def test_logout(self):
		assert "Redirecting" in self.app.get("/logout").data
		self.login("fhebert-perkins16", "password")
		assert "Redirecting" in self.app.get("/logout").data
	def test_login(self):
		assert not "Redirecting" in self.app.get("/login").data
		self.login("fhebert-perkins16", "password")
		rv = self.app.get("/login")
		assert "Redirecting" in self.app.get("/login").data

if __name__ == "__main__":
	try:
		unittest.main()
	except:
		pass
	cov.stop()
	cov.save()
	# print "\n\nCoverage Report:\n"
	# cov.report()
	print "HTML version: " + "tmp/coverage/"
	cov.html_report(directory='tmp/coverage/')
	cov.erase()
