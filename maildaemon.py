import imaplib
import time
import email
import json

if not os.path.exists("config.json"):
	os.system("cat default_config.json > config.json")
while True:
	time.sleep(300)
