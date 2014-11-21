from time import time
def full_search(searchterm, BySubject=True, ByContent=True, ByUser=True,Limit=100):
	starttime = time()
	from app import Tickets
	searchterms = searchterm.strip().split(" ")
	tickets = Tickets.find()
	ticket_dict = []
	for ticket in tickets:
		ticket_dict.append(ticket)
	subject = []
	content = []
	author = []
	for ticket in ticket_dict:
		for searchterm in searchterms:
			if searchterm in ticket["title"]:
				subject.append(ticket)
			if searchterm in ticket["author"]:
				author.append(ticket)
			if searchterm in ticket["content"]:
				author.append(ticket)
	temp = []
	for i in subject:
		if not i in temp:
			temp.append(i)
	for i in content:
		if not i in temp:
			temp.append(i)
	for i in author:
		if not i in temp:
			temp.append(i)
	to_return = []
	[to_return.append(ticket) for ticket in sorted(temp, key=lambda k: k['time'], reverse=True)]
	return time()-starttime, to_return
