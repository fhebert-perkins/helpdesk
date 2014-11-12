from flask import (Flask, redirect,url_for, render_template,
				   redirect, request, session, g, flash)
from flask.ext.mail import Mail, Message
from pymongo import MongoClient
from app import momentjs, check_hash, get_theme, parse_post
from hashlib import md5
from datetime import datetime



#initializations
app = Flask("helpdesk")
mailer = Mail(app)

Users = MongoClient().helpdesk.profiles.Users
Tickets = MongoClient().helpdesk.data.Tickets

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
	app.jinja_env.globals['language'] = session.get("language", "en")
	app.jinja_env.globals['theme'] = get_theme(session.get("theme"))

@app.route("/")
@app.route("/tickets")
def index():
	if not session.get("logged_in"):
		return redirect(url_for("login", redirect=request.url))
	page = int(request.args.get("p", "0"))
	tickets = []
	[tickets.append(ticket) for ticket in Tickets.find()]
	app.jinja_env.globals['title'] = "View Tickets"
	tickets = tickets[(page*10):(page*10)+10]
	return render_template("tickets_list.html", tickets=tickets)

@app.route("/details/<url>")
def details(url):
	if not session.get("logged_in"):
		return redirect(url_for("login", redirect=request.url))
	ticket = Tickets.find_one({"url" : url})
	app.jinja_env.globals['title'] = ticket["title"]
	if ticket == None:
		return 404
	else:
		return render_template("detail.html", ticket=ticket)

@app.route("/new", methods=['GET', 'POST'])
def new_thread():
	if not session.get("logged_in"):
		return redirect(url_for("login", redirect=request.url))
	app.jinja_env.globals['title'] = "New Ticket"
	if request.method == 'POST':
		is_vip =False
		try:
			if request.form["is_vip"]:
				is_vip = True
		except:
			flash("vip")
		tid = Tickets.insert({"title": request.form["title"],
							"url" : md5(request.form["title"]).hexdigest(),
							"content" : parse_post(request.form["text"]),
							"time" : datetime.utcnow(),
							"status" : 0,
							"author" : request.form["author"],
							"is_vip" : is_vip,
							"read" : False,
							"importance" : int(request.form["urgency"])})
		return str(tid)
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
