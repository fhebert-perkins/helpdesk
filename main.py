from flask import Flask, redirect, session, url_for, render_template, request, abort
from tinydb import TinyDB, where
from uuid import uuid4
from hashlib import md5

user_db = TinyDB('dbs/users.json')
ticket_db = TinyDB('dbs/tickets.json')
app = Flask(__name__)

app.config.update(
    DEBUG=True,
    SECRET_KEY='imaderpybird12345'
)


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
	else:
		if request.method == "POST":
			if request.form["password"] == user_db.search(where('username') == request.form["username"])[0]["password"]:
				session["logged_in"] = True
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
		to_display = ticket_db.all()[((25*page)-25):(25*page)+25]
		for i in to_display:
			i["userid"] = md5(i["email"]).hexdigest()
		return render_template("tickets.html", to_display=to_display)
@app.route("/ticket/<ticket_id>", methods=["POST","GET"])
def ticket_detail(ticket_id):
	if not session.get("logged_in"):
		return redirect(url_for("login"))
	else:
		results = ticket_db.search(where("uuid") == ticket_id)
		if len(results) == 0:
			abort(404)
		else:
			return render_template("ticket_detail.html", details=ticket_db[0])
@app.route("/user/<userid>")
def user(userid):
	return render_template("unimplemented.html")
# ERROR HANLDERS
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404




if __name__ == "__main__":
	app.run()
