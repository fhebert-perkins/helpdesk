from hashlib import sha224 # Pragma: No Cover
from os import urandom # Pragma: No Cover
def check_hash(password, salt, hashed_pw):
	if sha224(salt+password).hexdigest() == hashed_pw:
		return True
	else:
		return False
def gen_password_arr(password):
	salt = urandom(16).encode("base_64")
	return [salt, sha224(salt+password).hexdigest()]
