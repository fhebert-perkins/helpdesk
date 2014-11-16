import markdown # Pragma: No Cover
from uuid import uuid4 # Pragma: No Cover
#import beautifulsoup4
def parse_post(content):
	content = content.replace("<", "&lt;").replace(">", "&gt;")
	return markdown.markdown(content)
def allowed_file(filename):
	ALLOWED_EXTENSIONS = ["png", "jpg", "jpeg", "gif"]
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
def gen_obf_filename(filename):
	return ".".join([uuid4().hex, filename.split(".").pop(-1)])

def parse_email(email_body):
	pass
