import os
import app
import unittest
import tempfile
from coverage import coverage
from libs import gen_password_arr
from loremipsum import get_paragraphs, get_sentences
from random import randint
import pep8
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
		orv = self.app.get("/")
		# Bad title
		rv = self.add_ticket("", "fhebert-perkins16", get_sentences(1)[0], 1, False)
		assert "Error creating ticket" in rv.data
		# Bad Username
		rv = self.add_ticket("herpderp", "", "Herpderp", 1, False)
		assert "No such Username cannot create ticket" in rv.data
		# No text
		rv = self.add_ticket(get_sentences(1)[0], "fhebert-perkins16", "", 1, False)
		assert "Error creating ticket" in rv.data
		# Fully formed tickets
		rv = self.add_ticket(get_sentences(1)[0], "fhebert-perkins16", get_sentences(1)[0], 1, False)
		assert "created new ticket id" in rv.data
		rv = self.add_ticket(get_sentences(1)[0], "fhebert-perkins16", get_sentences(1)[0], 2, False)
		assert "created new ticket id" in rv.data
		rv = self.add_ticket(get_sentences(1)[0], "fhebert-perkins16", get_sentences(1)[0], 3, False)
		assert "created new ticket id" in rv.data
		rv = self.add_ticket(get_sentences(1)[0], "fhebert-perkins16", get_sentences(1)[0], 1, True)
		assert "created new ticket id" in rv.data
		rv = self.add_ticket(get_sentences(1)[0], "fhebert-perkins16", get_sentences(1)[0], 2, True)
		assert "created new ticket id" in rv.data
		rv = self.add_ticket(get_sentences(1)[0], "fhebert-perkins16", get_sentences(1)[0], 3, True)
		assert "created new ticket id" in rv.data
		rv = self.add_ticket(get_sentences(1)[0], "fhebert-perkins16", get_sentences(1)[0], 3, "Fish")
		assert "created new ticket id" in rv.data
		nrv = self.app.get("/")
		assert orv != nrv
	def test_empty_db(self):
		assert "Redirecting" in self.app.get("/").data # makes sure that authentication is needed
		self.login("fhebert-perkins16", "password")
		rv1 = self.app.get("/")
		rv2 = self.app.get("/tickets")
		assert rv1.data == rv2.data
		tickets = app.Tickets.find({"status" : 0})
		for ticket in tickets:
			rv = self.app.get("/details/{0}".format(ticket["url"]))
			assert ticket["title"] in rv.data
			assert ticket["content"] in rv.data
			assert ticket["author"] in rv.data
		rv1 = self.app.get("/")
		rv2 = self.app.get("/tickets")
		assert rv1.data == rv2.data

	def test_details(self):
		assert "Redirecting" in self.app.get("/details/blarg").data # makes sure that authentication is needed
		self.login("fhebert-perkins16", "password")
		rv = self.app.get("/details/blarg")
		assert 404 == rv.status_code
		test = app.Tickets.find_one()["url"]
		rv = self.app.get("/details/{0}".format(test))
		assert 200 == rv.status_code

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
	def test_settings(self):
		assert "Redirecting" in self.app.get("/settings").data
		assert "Redirecting" in self.app.get("/settings/personal").data
		assert "Redirecting" in self.app.get("/settings/users").data
		assert "Redirecting" in self.app.get("/settings/misc").data
		self.login("fhebert-perkins16","password")
		assert 200 == self.app.get("/settings").status_code
		assert 200 == self.app.get("/settings/personal").status_code
		assert 200 == self.app.get("/settings/users").status_code
		assert 200 == self.app.get("/settings/misc").status_code
		assert 404 == self.app.get("/settings/blarg").status_code

	def test_replies(self):
		tickets = app.Tickets.find({"reply" : []})
		self.login("fhebert-perkins16", "password")
		for ticket in tickets:
			for i in range(randint(0, 200)):
				msg = " ".join(get_sentences(randint(1,5)))
				rv = self.app.post('/details/{0}'.format(ticket["url"]), data=dict(
					text=msg,
				), follow_redirects=True)
				assert msg in rv.data
			msg = get_sentences(1)[0]
			rv = self.app.post('/details/{0}'.format(ticket["url"]), data=dict(
				derp=msg,
			), follow_redirects=True)
			assert not msg in rv.data
	def test_change_pw(self):
		rv = self.login("fhebert-perkins16", "password")
		assert "Logged In" in rv.data
		rv = self.app.post("/settings/personal",data=dict(
			form_name="change_pw",
			newpassword="testtest",
			newpassword2="testtest",
			oldpassword="password"
		))
		assert not "wrong password" in rv.data
		assert not "passwords do not match" in rv.data
		self.logout()
		rv = self.login("fhebert-perkins16", "testtest")
		assert "Logged In" in rv.data
	def test_pep8_conformance(self):
		pep8style = pep8.StyleGuide(quiet=True)
		files = [
				'app.py',
				'libs/__init__.py',
				'libs/auth.py',
				'libs/javascriotlibs.py',
				'libs/search.py',
				'libs/themes.py',
				'app_test.py'
				]
		errors = 0
		for file in files:
			fchecker = pep8.Checker(file, show_source=True)
			errors += fchecker.check_all()
		if errors != 0:
			print("Found %s errors (and warnings)" % errors)
		assert errors == 0
if __name__ == "__main__":
	try:
		unittest.main()
	except:
		pass
	cov.stop()
	cov.save()
	# print "\n\nCoverage Report:\n"
	# cov.report()
	print "HTML version: " + "http://localhost"
	cov.html_report(directory='/home/finley/tmp/coverage/')
	cov.erase()
