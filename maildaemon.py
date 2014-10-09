import imaplib, time, email, json, os, pprint, email, re
from uuid import uuid4
from tinydb import TinyDB

def parse_date(ts):
	ts = ts.split(" ")
	time = "d"
	month = "d"
	day = "d"
	year = "d"
	return day+"-"+month+"-"+year+" "+time

months = {
	"Jan" : "01",
	"Feb" : "02",
	"Mar" : "03",
	"Apr" : "04",
	"May" : "05",
	"Jun" : "06",
	"Jul" : "07",
	"Aug" : "08",
	"Sep" : "09",
	"Oct" : "10",
	"Nov" : "11",
	"Dec" : "12"
}

ticket_db = TinyDB("dbs/tickets.json")
if not os.path.exists("config.json"):
	os.system("cat default_config.json > config.json")

config_file = open("config.json", "r")
config = json.loads(config_file.read())
config_file.close()
# while True:
conn = imaplib.IMAP4(config["mail_server"])
conn.login(config["mail_username"], config["mail_password"])
conn.select(config["mail_mailbox"])
ret, messages = conn.search(None, '(UNSEEN)')
if ret == 'OK':
	for num in messages[0].split(" ")[0:1]:
		print num
		typ, data = conn.fetch(num,'(RFC822)')
		msg =  email.message_from_string(data[0][1])
		typ, data = conn.store(num, '-FLAGS', '\\Seen')
		author = msg["From"]
		title = msg["Subject"]
		date = parse_date(msg["Date"])

	# if is_vip:
	# 	severity = 1
	# elif is_high_priority:
	# 	severity = 2
	# else:
	# 	severity = 3
	# ticket_db.insert({"status":0,"uuid":uuid4().hex,"title":title,"text":content,"severity":severity,"email":author.lower(),"replies":[],"time":timestamp})
