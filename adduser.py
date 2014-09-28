username = raw_input("username: ")
password = raw_input("password: ")
email = raw_input("email: ")
from tinydb import TinyDB
db = TinyDB("dbs/users.json")
db.insert({"username" : username, "password" : password, "email" : email, "permission" : 0})
print "added", username
