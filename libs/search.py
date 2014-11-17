from time import time
def full_search(searchterm, BySubject=True, ByContent=True, ByUser=True,Limit=100):
	searchterms = searchterm.split(" ")
	from app import Tickets, Users
	searchable_columns = ["title","content", "author"]
	tickets = []
	tickets = Tickets.find().sort("time", -1)
	iterable = 0
	possible_results = []
	starttime = time()
	for ticket in tickets:
		score = 0
		for item in searchable_columns:
			for word in searchterm:
				if word in ticket[item]:
					score+=1
			if score != 0:
				possible_results.append([score, ticket])
		if len(possible_results) == Limit:
			break
	endtime = time()
	results = []
	possible_results = sorted(possible_results, reverse=True)
	timedelta = endtime-starttime
	return timedelta, results
