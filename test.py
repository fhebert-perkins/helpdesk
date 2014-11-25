from flask import Flask
app = Flask('helpdesk')
@app.route("/derp")
def derp():
	return "Derp"
