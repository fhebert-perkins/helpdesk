import imaplib, time, email, json, os, pprint, email, re
from uuid import uuid4
from tinydb import TinyDB

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

def parse_date(ts):
	ts = ts.split(" ")
	minute = ts[4].split(":")[1]
	if len(minute) < 2:
		minute = "0"+minute
	hour = ts[4].split(":")[0]
	if len(minutes) < 2:
		hour = "0"+hour
	time = hour+":"+minute
	month = months[ts[2]]
	day = ts[1]
	year = ts[3]
	return day+"-"+month+"-"+year+" "+time
	#return ts
def is_vip(author):
	vip_db = TinyDB("dbs/vips.json")
	try:
		vip_db.get(where("email") == author)
		return True
	except:
		return False

ticket_db = TinyDB("dbs/tickets.json")
if not os.path.exists("config.json"):
	os.system("cat default_config.json > config.json")

config_file = open("config.json", "r")
config = json.loads(config_file.read())
config_file.close()
# while True:
conn = imaplib.IMAP4_SSL(config["mail_server"])
conn.login(config["mail_username"], config["mail_password"])
conn.select(config["mail_mailbox"])
ret, messages = conn.search(None, '(UNSEEN)')
if ret == 'OK':
	if not messages[0].split(" ") == [""]:
		for num in messages[0].split(" "):
			severity = 3
			typ, data = conn.fetch(num,'(RFC822)')
			msg =  email.message_from_string(data[0][1])
			typ, data = conn.store(num, 'FLAGS', '\\Seen')
			author = msg["From"].lower()
			title = msg["Subject"]
			date = parse_date(msg["Date"])
			text=msg["Content"]
			print str(msg)
			for i in msg.items():
				if i[0] == "X-Priority":
					print i[1]
					if int(i[1]) == 1:
						severity = 2
			if is_vip(author):
				severity = 1
			print severity
			if subject[0:2] == "RE:":
				t = ticket_db.search(where("title") == subject[3:] & where("email") == author)[0]
				t["replies"].append({"content":text, "email":author})
			else:
				pass
				# ticket_db.insert({"status":0,"uuid":uuid4().hex,"title":title,"text":content,"severity":severity,"email":author,"replies":[],"time":timestamp})

	# if is_vip:
	# 	severity = 1
	# elif is_high_priority:
	# 	severity = 2
	# else:
	# 	severity = 3
