from hashlib import sha224
def check_hash(password, salt, hashed_pw):
	if sha224(salt+password).hexdigest() == hashed_pw:
		return True
	else:
		return False
