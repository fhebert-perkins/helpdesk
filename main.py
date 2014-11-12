from flask import (Flask, redirect,url_for, render_template,
				   redirect, request, session, g, flash)
from flask.ext.mail import Mail, Message
from pymongo import MongoClient
from app import momentjs, check_hash, get_theme, parse_post
from hashlib import md5
from datetime import datetime
from uuid import uuid4



#initializations
app = Flask("helpdesk")
mailer = Mail(app)

Users = MongoClient().helpdesk.profiles.Users
Tickets = MongoClient().helpdesk.data.Tickets

def get_unread():
	if Tickets.find({"status" : 0}) == None:
		return "0"
	else:
		tickets = Tickets.find({"status" : 0})
		return str(tickets.count())

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
	[tickets.append(ticket) for ticket in Tickets.find().sort("time", -1)]
	app.jinja_env.globals['title'] = "View Tickets"
	tickets = tickets[(page*10):(page*10)+10]
	return render_template("tickets_list.html", tickets=tickets)

@app.route("/details/<url>", methods=["post", "get"])
def details(url):
	if not session.get("logged_in"):
		return redirect(url_for("login", redirect=request.url))
	ticket = Tickets.find_one({"url" : url})
	if ticket == None:
		return 404
	app.jinja_env.globals['title'] = ticket["title"]
	if request.method == "POST":
		try:
			replies = ticket["reply"]
		except:
			replies = []
		reply_dict ={
					"author" : session.get("username"),
					"time" : datetime.utcnow(),
					"content" : parse_post(request.form["text"])
					}
		replies.append(reply_dict)
		Tickets.update({"_id" : ticket["_id"]}, {"$set" : {"reply" : replies}})
		flash("reply submitted")
		return render_template("ticket_detail.html", ticket=ticket)
	if ticket["status"] == 0:
		Tickets.update({"_id" : ticket["_id"]}, {"$set" : {"status" : 1}})
	new_status = request.args.get("u", None)
	if new_status != None and new_status != 0 and new_status != 1 and new_status <= 4:
		Tickets.update({"_id" : ticket["_id"]}, {"$set" : {"status" : new_status}})
	else:
		return render_template("ticket_detail.html", ticket=ticket)

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
			pass
		tid = Tickets.insert({"title": request.form["title"],
							"url" : uuid4().hex,
							"content" : parse_post(request.form["text"]),
							"time" : datetime.utcnow(),
							"status" : 0,
							"author" : request.form["author"],
							"is_vip" : is_vip,
							"reply" : [],
							"importance" : int(request.form["urgency"])})
		flash("created new ticket <a href='/detail/{0}'>here</a> ".format(md5(request.form["title"]).hexdigest()))
	return render_template("new_ticket.html")

@app.route("/user/<user>")
def user_page(user):
	if not session.get("logged_in"):
		return redirect(url_for("login", redirect=request.url))
	user_data = Users.find_one({"username" : user})
	if user_data == None:
		return 404
	app.jinja_env.globals["title"] = user
	recent_tickets = Tickets.find({"author" : user}).sort("time", -1)[0:10]
	tickets_submitted = {
						"total_submitted" : Tickets.find({"author" : user}).count(),
						"percentage" : (float(Tickets.find({"author" : user}).count())/float(Tickets.find().count()))*100
						}
	return render_template("user_profile.html", user=user_data, tickets=tickets_submitted, recent_tickets= recent_tickets)

@app.route("/settings")
def settings():
	return "NYI"

@app.route("/login", methods=["post", "get"])
def login():
	if session.get("logged_in"):
		if request.args.get("redirect", None) == None:
			return redirect(url_for("index"))
		return redirect(request.args.get("redirect", None))
	if request.method == "POST":
			user = Users.find_one({"username" : request.form["username"]})
			password = user["password"]
			if check_hash(request.form["password"], password[0], password[1]):
				session["logged_in"] = True
				session["username"] = request.form["username"]
				session["theme"] = user.get("theme", None)
				Users.update({"_id" : user["_id"]}, {"$set" : {"last_login" : datetime.utcnow()}})
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
	app.secret_key=os.urandom(24)
	app.run(debug=True)
