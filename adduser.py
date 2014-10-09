username = raw_input("username: ")
password = raw_input("password: ")
email = raw_input("email: ")
is_admin = 0
if raw_input("is admin[y/n]: ").lower() == "y":
	is_admin = 1
from tinydb import TinyDB
db = TinyDB("dbs/users.json")
from hashlib import md5
db.insert({"username" : username, "password" : md5(password).hexdigest(), "email" : email, "permission" : is_admin, "posts":0, "user_id": md5(email).hexdigest()})
print "added", username
