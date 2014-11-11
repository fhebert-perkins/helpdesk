from flask import (Flask, redirect,url_for, render_template,
				   redirect, request, session, g, flash)
from flask.ext.mail import Mail, Message
from pymongo import MongoClient
from app import momentjs, check_hash



#initializations
app = Flask("helpdesk")
mailer = Mail(app)

app.jinja_env.globals['momentjs'] = momentjs

Users = MongoClient().helpdesk.profiles.Users
Tickets = MongoClient().helpdesk.data.Profiles

@app.route("/")
@app.route("/tickets")
def index():
	if not session.get("logged_in"):
		return redirect(url_for("login", redirect=request.url))
	return render_template("tickets_list.html")


@app.route("/login", methods=["post", "get"])
def login():
	if session.get("logged_in"):
		if request.args.get("redirect", None) == None:
			return redirect(url_for("index"))
		return redirect(request.args.get("redirect", None))
	if request.method == "POST":
			password = Users.find_one({"username" : request.form["username"]})["password"]
			if check_hash(request.form["password"], password[0], password[1]):
				session["logged_in"] = True
				session["username"] = request.form["username"]
				if request.args.get("redirect", None) == None:
					return redirect(url_for("index"))
				return redirect(request.args.get("redirect", None))
			else:
				flash("error: could not login")
	return render_template("login.html")


if __name__ == "__main__":
	import os
	app.secret_key=os.urandom(16)
	app.run(debug=True)
