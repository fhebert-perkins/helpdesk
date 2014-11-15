from hashlib import sha224
from os import urandom
def check_hash(password, salt, hashed_pw):
	if sha224(salt+password).hexdigest() == hashed_pw:
		return True
	else:
		return False
def gen_password_arr(password):
	salt = urandom(16).encode("base_64")
	return [salt, sha224(salt+password).hexdigest()]
