from flask import Flask, redirect, session, url_for, render_template, request, abort, g
from tinydb import TinyDB, where
from uuid import uuid4
from hashlib import md5
from os import urandom
from time import localtime, strftime, time

user_db = TinyDB('dbs/users.json')
ticket_db = TinyDB('dbs/tickets.json')
vip_db = TinyDB("dbs/vips.json")
app = Flask(__name__)

app.config.update(
    DEBUG=True,
    SECRET_KEY=urandom(24)
)
@app.before_request
def before_request():
    g.pending = dict(pending=str(len(ticket_db.search(where("status") == 0))))
@app.context_processor
def inject_user():
    return g.pending

@app.route("/")
def main():
	if session.get("logged_in"):
		return redirect(url_for("tickets"))
	else:
		return redirect(url_for("login"))

@app.route("/login", methods = ["POST", "GET"])
def login():
	error = None
	if session.get("logged_in"):
		return redirect(url_for("tickets"))
        if request.method == "POST":
            # user = user_db.search(where('username') == request.form["username"])[0]
            try:
                user = user_db.search(where('username') == request.form["username"])[0]
            except:
                error = "No such Username or Password"
                return render_template("login.html", error=error)
            if md5(request.form["password"]).hexdigest() == user["password"]:
                session["logged_in"] = True
                session["username"] = request.form["username"]
                t = user_db.get(where('username') == request.form["username"])
                t["last_login"] = time()
                session["email"] = t["email"]
                user_db.update(t, eids=[t.eid])
                return redirect(url_for("tickets"))
            else:
                error = "No such Username or Password"
                return render_template("login.html", error=error)
        elif request.method == "GET":
            return render_template("login.html")

@app.route("/logout")
def logout():
	if session.get("logged_in"):
		session.pop("logged_in", None)
		return redirect(url_for("login"))
	else:
		return redirect(url_for("login"))

@app.route("/tickets", methods = ["GET"])
def tickets():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    else:
        page = int(request.args.get("page", 0))
        to_display = ticket_db.all()[25*page:(25*page)+25]
        for i in to_display:
            i["userid"] = md5(i["email"]).hexdigest()
        to_display = sorted(to_display, key=lambda k: k['time'], reverse=True)
        return render_template("tickets.html", to_display=to_display, page=page)

@app.route("/ticket/<ticket_id>", methods=["POST","GET"])
def ticket_detail(ticket_id):
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    else:
        if request.method == "GET":
            results = ticket_db.search(where("uuid") == ticket_id)
            action_url = request.path
            status = int(request.args.get("status", 10))
            if status < 0 or status > 3:
                pass
            else:
                t = ticket_db.get(where('uuid') == ticket_id)
                t["status"] = status
                ticket_db.update(t, eids=[t.eid])
            if len(results) == 0:
                abort(404)
            else:
                results[0]["text"].replace("\;", ";")
                return render_template("ticket_detail.html", details=results[0], actionurl=action_url)
        else:
            content = request.form["content"].replace("\n", "<br>")
            user = session.get("username")
            t = ticket_db.get(where('uuid') == ticket_id)
            if t["replies"] == None:
                t["replies"] = []
            t["replies"].append({"content" : content, "author": user})
            ticket_db.update(t, eids=[t.eid])
            return redirect(request.path)

@app.route("/new", methods =["POST", "GET"])
def new_ticket():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    else:
        if request.method == "POST":
            user = request.form["email"]
            title = request.form["title"]
            content = request.form["content"].replace("\n", "<br>").replace(";", "\;")
            ticket_id = uuid4().hex
            severity = int(request.form["severity"])
            time = strftime("%m-%d-%Y %H:%M", localtime())
            ticket_db.insert({"severity" : severity, "email" : user, "title":title, "text":content,"uuid":ticket_id, "time":time, "status":0, "replies":[]})
            redirect_url = url_for("ticket_detail", ticket_id=ticket_id)
            return redirect(redirect_url)
        else:
            return render_template("newticket.html")
@app.route("/user")
def user():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    else:
        return redirect(url_for("tickets"))

@app.route("/user/<userid>")
def view_user(userid):
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    else:
        user = user_db.get(where('user_id') == userid)
        if len(user) < 0:
            abort(404)
        else:
            tickets = user_db.search(where('author') == user["email"])
            user["tickets"] = tickets
            user["posts"] = len(tickets)
            return render_template("user.html", user=user)
@app.route("/account")
def account():
    return redirect(url_for("view_user" , userid=md5(session.get("email")).hexdigest()))

@app.route("/settings", methods=["POST", "GET"])
def settings():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    request_user = user_db.get(where('username') == session["username"])
    if request_user["permission"] == 1:
        if request.method == "GET":
            vips = vip_db.all()
            return render_template("admin_settings.html", vips=vips, admins=admins )
        if request.method == "POST":
            if request.form["submit"] == "delete_vip":
                vip_db.remove([vip_db.get(where("email") == request.form["email"]).eid])
                return redirect(url_for("settings"))
            elif request.form["submit"] == "add_vip":
                vip_db.insert({"email": request.form["email"], "reason":request.form["reason"]})
                return redirect(url_for("settings"))
            else:
                return redirect(url_for("settings"))
        else:
            return render_template("settings.html")

# ERROR HANLDERS
@app.errorhandler(404)
def page_not_found(e):
    
    return render_template('404.html'), 404
if __name__ == "__main__":
	app.run()
