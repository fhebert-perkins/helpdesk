username = raw_input("username: ")
password = raw_input("password: ")
email = raw_input("email: ")
from tinydb import TinyDB
db = TinyDB("dbs/users.json")
from hashlib import md5, sha224
db.insert({"username" : username, "password" : sha224(password).hexdigest(), "email" : email, "permission" : 0, "posts":0, "user_id": md5(email).hexdigest()})
print "added", username
