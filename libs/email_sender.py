import smtplib # Pragma: No Cover
import email # Pragma: No Cover
import json # Pragma: No Cover
from email.mime.multipart import MIMEMultipart # Pragma: No Cover
from email.mime.text import MIMEText # Pragma: No Cover

config = json.loads(open("config.json", "r").read())

def send_email(recipeient_email, message,subject=None, HTML=False):
	try:
		from app import Users
		server = smtplib.SMTP(config["email_server"], config["email_port"])
		server.ehlo()
		if config["email_tls"]:
			server.starttls()
		server.login(config["email_username"], config["email_password"])
		msg = MIMEMultipart('alternative')
		if subject == None:
			subject = config["email_default_subject"]
		msg = MIMEMultipart('alternative')
		msg['Subject'] = subject
		msg['From'] = config["email_username"]
		msg['To'] = recipeient_email
		text = MIMEText(message, "html")
		msg.attach(text)
		server.sendmail(config["email_username"], recipeient_email, msg.as_string())
		server.quit()
		return True
	except:
		return False
