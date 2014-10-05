import imaplib
import time
import email
import json
import os
import pprint
import email
from uuid import uuid4
from tinydb import TinyDB

ticket_db = TinyDB("dbs/tickets.json")
if not os.path.exists("config.json"):
	os.system("cat default_config.json > config.json")

config_file = open("config.json", "r")
config = json.loads(config_file.read())
config_file.close()
# while True:
mail = imaplib.IMAP4_SSL(config["mail_server"])
mail.login(config["mail_username"], config["mail_password"])
mail.list()
mail.select("INBOX")
result, data = mail.search(None, "ALL")
ids = data[0]
id_list = ids.split()
for email_id in id_list:
	is_high_priority = False
	is_vip = False
	content = ""
	result, data = mail.fetch(email_id, "(RFC822)")
	raw_email = data[0][1]
	email_message = email.message_from_string(raw_email)
	author = email.utils.parseaddr(email_message['From'])[1]
	if author.lower in config["vips"]:
		is_vip = True
	is_high_importance = False
	for item in email_message.items():
		if item[0] == "Importance" and item[1] == "high":
			is_high_priority = True
	title = email_message["subject"]
	maintype = email_message.get_content_maintype()
	if maintype == 'multipart':
		for part in email_message.get_payload():
			if part.get_content_maintype() == 'text':
				content = part.get_payload()
			elif maintype == 'text':
				content = email_message.get_payload()
	if is_vip:
		severity = 1
	elif is_high_priority:
		severity = 2
	else:
		severity = 3
	# pprint.pprint({"status":0,"uuid":uuid4(),"title":title,"text":content,"severity":severity,"email":author.lower(),"replies":[],"time":time.strftime("%m-%d-%Y %H:%M", time.localtime())})
	print is_vip
	print is_high_priority
