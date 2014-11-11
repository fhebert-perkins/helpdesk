from flask import (Flask, redirect,url_for, render_template,
				   redirect, request, session, g, flash)
from flask.ext.mail import Mail, Message
from pymongo import MongoClient
from app import momentjs, check_hash, get_theme



#initializations
app = Flask("helpdesk")
mailer = Mail(app)

Users = MongoClient().helpdesk.profiles.Users
Tickets = MongoClient().helpdesk.data.Profiles

def get_unread():
	if Tickets.find({"read" : False}) == None:
		return "0"
	else:
		tickets = Tickets.find({"read" : False})
		return str(tickets.explain()["nscanned"])

@app.before_request
def setup():
	app.jinja_env.globals['momentjs'] = momentjs
	app.jinja_env.globals['unread'] = get_unread()
	app.jinja_env.globals['theme'] = get_theme(session.get("theme", None))

@app.route("/")
@app.route("/tickets")
def index():
	if not session.get("logged_in"):
		return redirect(url_for("login", redirect=request.url))
	return render_template("tickets_list.html")

@app.route("/details/<url>")
def details(url):
	if not session.get("logged_in"):
		return redirect(url_for("login", redurect=request.url))
	ticket = Tickets.findone({"url" : url})
	if ticket == None:
		return 404
	else:
		return render_template("detail.html", ticket=ticket)

@app.route("/new", methods=["post", "get"])
def new_thread():
	if not session.get("logged_in"):
		return redirect(url_for("login", redurect=request.url))
	if request.method == "post":
		pass
	return render_template("new_ticket.html")
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

@app.route("/logout")
def logout():
	if session.get("logged_in"):
		session.pop("logged_in", None)
	return redirect(url_for("index"))



if __name__ == "__main__":
	import os
	app.secret_key=os.urandom(16)
	app.run(debug=True)
