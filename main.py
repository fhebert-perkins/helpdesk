from flask import (Flask, redirect,url_for, render_template,
				   redirect, request, session, g, flash)
from flask.ext.mail import Mail, Message
from pymongo import MongoClient
from app import (momentjs, check_hash, get_theme, parse_post, themes,
				allowed_file, gen_obf_filename)
from hashlib import md5
from datetime import datetime
from uuid import uuid4
import json
from werkzeug import secure_filename
import os

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
	app.jinja_env.globals['len'] = len

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
	return render_template("tickets_list.html", tickets=tickets, page=[page+1, page-1, page])

@app.route("/details/<url>", methods=["post", "get"])
def details(url):
	if not session.get("logged_in"):
		return redirect(url_for("login", redirect=request.url))
	app.jinja_env.globals['unread'] = get_unread()
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
		if Users.find_one({"username" :  request.form["author"]}) != None:
			if request.files.getlist("file[]") != None:
				exceptions = 0
				files = request.files.getlist("file[]")
				filenames = []
				for file in files:
					if file and allowed_file(file.filename):
						filename = secure_filename(file.filename)
						filename = gen_obf_filename(filename)
						file.save(os.path.join("static/images/usercontent/", filename))
						filenames.append(filename)
					else:
						exceptions += 1
				if exceptions > 0:
					flash("Failed to upload {0}/{1} files".format(str(exceptions), str(len(files))))
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
								"attachment" : filenames,
								"importance" : int(request.form["urgency"])})
			flash("created new ticket <a href='/detail/{0}'>here</a> ".format(md5(request.form["title"]).hexdigest()))
		else:
			flash("No such Username cannot create ticket")
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
@app.route("/settings/<window>", methods=["post", "get"])
def settings_view(window=None):
	if not session.get("logged_in"):
		return redirect(url_for("login", redirect=request.url))
	if window == "personal":
		app.jinja_env.globals["settings_panel"] = 1
		app.jinja_env.globals["title"] = "settings : Personal"
		if request.method == "post":
			if form["submit"] == "changepw":
				flash("NYI")
			elif form["submit"] == "changetheme":
				flash("NYI")
			else:
				pass
		user = Users.find_one({"username" : session.get("username")})
		return render_template("settings/personal.html", user=user, themes=themes)
	elif window == "users":
		app.jinja_env.globals["settings_panel"] = 2
		app.jinja_env.globals["title"] = "settings : user"
		if request.method == "post":
			if form["submit"] == "add_user":
				if User.find_one({"username" : request.form["username"]}) == None and User.find_one({"email" : request.form["email"]}) == None:
					salt = salt = os.urandom(16).encode('base_64')
					Users.insert({
									"username" : request.form["username"],
									"email" : request.form["email"],
									"fname" : request.form["fname"],
									"lname" : request.form["lname"],
									"password" : [salt, sha224(salt+password)]
								})
					flash("New user created")
				else:
					flash("Something went wrong")
			else:
				pass
		return render_template("settings/users.html")
	elif window == "misc":
		app.jinja_env.globals["settings_panel"] = 3
		app.jinja_env.globals["title"] = "settings : misc"
		config_file = open("config.json", "r")
		config = json.loads(config_file.read())
		config_file.close()
		if request.method == "post":
			if form["submit"] == "changeemailcredentials":
				flash("NYI")
			elif form["submit"] == "addalloweddomain":
				flash("NYI")
			else:
				pass
		return render_template("settings/email.html", config=config)
	else:
		return render_template("settings/personal.html")



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
	app.secret_key= "TESTING123"#os.urandom(32).encode('base_64')
	app.run(debug=True)
