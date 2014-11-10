from flask import (Flask, redirect,url_for, render_template,
				   redirect, request, session, g)
from flask.ext.mail import Mail, Message
from flask.ext.pymongo import PyMongo
from flask.ext.bcrypt import Bcrypt, check_password_hash


#initializations
app = Flask("helpdesk")
mailer = Mail(app)
mongo = PyMongo(app)
bcrypt = Bcrypt(app)

@app.route("/")
def test():
	return mongo.db.Users.objects.findone()

if __name__ == "__main__":
	import os
	app.secret_key=os.urandom(16)
	app.run(debug=True)
