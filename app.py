from flask import (Flask, redirect,url_for, render_template,
				   redirect, request, session, g, flash, abort) # Pragma: No Cover
from flask.ext.mail import Mail, Message # Pragma: No Cover
from pymongo import MongoClient # Pragma: No Cover
from libs import (momentjs, check_hash, get_theme, parse_post, themes,
				allowed_file, gen_obf_filename, full_search) # Pragma: No Cover
from hashlib import md5, sha224 # Pragma: No Cover
from datetime import datetime # Pragma: No Cover
from uuid import uuid4 # Pragma: No Cover
import json # Pragma: No Cover
from werkzeug import secure_filename # Pragma: No Cover
import os # Pragma: No Cover

#initializations
app = Flask("helpdesk") # Pragma: No Cover
mailer = Mail(app) # Pragma: No Cover

Users = MongoClient().helpdesk.profiles.Users # Pragma: No Cover
app.config["TESTING"] = True # Pragma: No Cover
if not app.config["TESTING"]: # Pragma: No Cover
	Tickets = MongoClient().helpdesk.data.Tickets
else: # Pragma: No Cover
	Tickets = MongoClient().helpdesktest.profiles.Tickets

def get_unread():
	if Tickets.find({"status" : 0}) == None:
		return "0"
	else:
		tickets = Tickets.find({"status" : 0})
		return str(tickets.count())

@app.before_request # Pragma: No Cover
def setup():
	app.jinja_env.globals['momentjs'] = momentjs
	app.jinja_env.globals['unread'] = get_unread()
	app.jinja_env.globals['language'] = session.get("language", "en")
	app.jinja_env.globals['theme'] = get_theme(session.get("theme"))
	app.jinja_env.globals['len'] = len

@app.route("/") # Pragma: No Cover
@app.route("/tickets") # Pragma: No Cover
def index():
	if not session.get("logged_in"):
		return redirect(url_for("login", redirect=request.url))
	page = int(request.args.get("p", "0"))
	tickets = []
	[tickets.append(ticket) for ticket in Tickets.find().sort("time", -1)]
	tickets
	app.jinja_env.globals['title'] = "View Tickets"
	tickets = tickets[(page*10):(page*10)+10]
	return render_template("tickets_list.html", tickets=tickets, page=[page+1, page-1, page])

@app.route("/details/<url>", methods=["post", "get"]) # Pragma: No Cover
def details(url):
	if not session.get("logged_in"):
		return redirect(url_for("login", redirect=request.url))
	app.jinja_env.globals['unread'] = get_unread()
	ticket = Tickets.find_one({"url" : url})
	if ticket == None:
		abort(404)
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

@app.route("/new", methods=['GET', 'POST']) # Pragma: No Cover
def new_thread():
	if not session.get("logged_in"):
		return redirect(url_for("login", redirect=request.url))
	app.jinja_env.globals['title'] = "New Ticket"
	if request.method == 'POST':
		if Users.find_one({"username" :  request.form["author"]}) != None:
			filenames = []
			if len(request.files.getlist("file[]")) != 0:
				exceptions = 0
				files = request.files.getlist("file[]")
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

			ticket_title = request.form.get("title",None)
			ticket_content = parse_post(request.form.get("text"))
			ticket_urgency = int(request.form.get("urgency"))
			if len(ticket_title) > 2 and len(ticket_content) > 1 and ticket_urgency <= 3 and ticket_urgency >= 1:
				ticket_url = uuid4().hex
				tid = Tickets.insert({
					"title": ticket_title,
					"url" : ticket_url,
					"content" : ticket_content,
					"time" : datetime.utcnow(),
					"status" : 0,
					"author" : request.form.get("author"),
					"is_vip" : is_vip,
					"reply" : [],
					"attachment" : filenames,
					"importance" : ticket_urgency
				})
				flash("created new ticket id:{0} ".format(ticket_url))
			else:
				flash("Error creating ticket")
		else:
			flash("No such Username cannot create ticket")
	return render_template("new_ticket.html")

@app.route("/user/<user>") # Pragma: No Cover
def user_page(user):
	if not session.get("logged_in"):
		return redirect(url_for("login", redirect=request.url))
	user_data = Users.find_one({"username" : user})
	if user_data == None:
		abort(404)
	app.jinja_env.globals["title"] = user
	recent_tickets = Tickets.find({"author" : user}).sort("time", -1)[0:10]
	tickets_submitted = {
						"total_submitted" : Tickets.find({"author" : user}).count(),
						"percentage" : (float(Tickets.find({"author" : user}).count())/float(Tickets.find().count()))*100
						}
	return render_template("user_profile.html", user=user_data, tickets=tickets_submitted, recent_tickets= recent_tickets)
@app.route("/settings") # Pragma: No Cover
@app.route("/settings/<window>", methods=["POST", "GET"]) # Pragma: No Cover
def settings_view(window=None):
	if not session.get("logged_in"):
		return redirect(url_for("login", redirect=request.url))
	if window == "personal":
		app.jinja_env.globals["settings_panel"] = 1
		app.jinja_env.globals["title"] = "settings : Personal"
		if request.method == "post":
			if request.form["form_name"] == "change_pw":
				if request.form["newpassword"] == request.form["newpassword2"]:
					user = Users.find_one({"username" : session.get("username")})
					if check_hash(request.form["password"], user["password"][0], user["password"][1]):
						salt = os.urandom(16).encode('base_64')
						User.update({"_id" : user["_id"]}, {"$set" : {"password" : [salt, sha224(salt+password)]}})
					else:
						flash("wrong password")
				else:
					flash("passwords do not match")
		user = Users.find_one({"username" : session.get("username")})
		return render_template("settings/personal.html", user=user, themes=themes)
	elif window == "users":
		app.jinja_env.globals["settings_panel"] = 2
		app.jinja_env.globals["title"] = "settings : user"
		if request.method == "POST":
			if Users.find_one({"username" : request.form["username"]}) == None and Users.find_one({"email" : request.form["email"]})==None:
				salt = os.urandom(16).encode('base_64')
				uid = Users.insert({
									"username" : request.form["username"],
									"email" : request.form["email"],"fname" : request.form["fname"],
									"lname" : request.form["lname"],
									"password" : [salt, sha224(salt+request.form["password"]).hexdigest()],
									"last_login" : None
								})
				flash("New user created")
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
	elif window == None:
		return render_template("settings/personal.html")
	else:
		abort(404)

@app.route("/search")
def search():
	query = request.args.get("q", None)
	app.jinja_env.globals["title"] = "search"
	if query == None:
		return render_template("search.html", results=[], time_taken=0)
	else:
		timedelta, results = full_search(query)
		return render_template("search.html", results=results, time_taken=timedelta)

@app.route("/login", methods=["post", "get"]) # Pragma: No Cover
def login():
	if session.get("logged_in"):
		if request.args.get("redirect", None) == None:
			return redirect(url_for("index"))
		return redirect(request.args.get("redirect", None))
	if request.method == "POST":
			user = Users.find_one({"username" : request.form["username"]})
			try:
				password = user["password"]
				if check_hash(request.form["password"], password[0], password[1]):
					session["logged_in"] = True
					session["username"] = request.form["username"]
					session["theme"] = user.get("theme", None)
					Users.update({"_id" : user["_id"]}, {"$set" : {"last_login" : datetime.utcnow()}})
					flash("Logged In")
					return redirect(request.args.get("redirect") or url_for("index"))
				else:
					flash("Error: Could Not Login")
			except:
				flash("Error: Could Not Login")
	return render_template("login.html")

@app.route("/logout") # Pragma: No Cover
def logout():
	if session.get("logged_in"):
		session.pop("logged_in", None)
	return redirect(url_for("index"))

if __name__ == "__main__": # Pragma: No Cover
	import os # Pragma: No Cover
	app.secret_key= "TESTING123"#os.urandom(32).encode('base_64') # Pragma: No Cover
	app.run(debug=True) # Pragma: No Cover
