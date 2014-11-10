def add_users():
	from pymongo import MongoClient
	import requests
	import json
	import bcrypt
	import time

	client = MongoClient()
	db = client.helpdesk
	users = db.Users
	objects = users.objects

	num_users = input("how many users to generate? ")
	outstring = []
	for i in range(num_users):
		user = json.loads(requests.get("http://api.randomuser.me").text)["results"][0]
		username = user["user"]["username"]
		firstname = user["user"]["name"]["first"]
		lastname = user["user"]["name"]["last"]
		password = user["user"]["password"]
		email = user["user"]["email"]
		salt =  bcrypt.gensalt()
		password = bcrypt.hashpw(password, salt)
		objects.insert({"username" : username,
						"fname" : firstname,
						"lname" : lastname,
						"password" : password,
						"salt" : salt,
						"email" : email})
		print "generated {0:4}/{1:4} users".format(i+1,num_users)
		outstring.append({"username" : username, "password" : user["user"]["password"],"email" : email})
	out_file = open("resources/users.json", "a")
	out_file.write(json.dumps(outstring))
	out_file.close()
	print "all users outputed to 'tests/resources/users.json' for testing purposes"
