import markdown
#import beautifulsoup4
def parse_post(content):
	content = content.replace("<", "&lt;").replace(">", "&gt;")
	return markdown.markdown(content)
def sanitize(string):
	pass
def parse_email(email_body):
	pass
