import threading, requests, json,queue
from os import path
from bs4 import BeautifulSoup
from collections import OrderedDict

global id
id = int(input("Enter starting ID:"))
end = int(input("Enter ending ID:"))
t = int(input("Enter number of threads:"))
url = 'https://forums.yoworld.com/viewtopic.php?t=';
out = "out.json"
history = "history.txt"
q = queue.Queue()

def uniqsort():
	s = set()
	temp = OrderedDict({'YoWorld': []})
	json_file = open('out.json')
	data = json.load(json_file)
	json_file.close()
	sorted_file = open('out.json', 'w')
	sorted_obj = OrderedDict(data)
	sorted_obj['YoWorld'] = sorted(sorted_obj['YoWorld'], key=lambda x: int(x['player']))
	for d in sorted_obj['YoWorld']:
		if str(d) not in s:
			s.add(str(d))
			temp['YoWorld'].append(OrderedDict(d))

	sorted_file.write(json.dumps(OrderedDict(temp), indent=4,sort_keys=False))

def process(idx):
	site = url + str(idx)
	page = requests.get(site)
	posts=0
	soup = BeautifulSoup(page.content, "html.parser")
	if soup.find("div", {"class": "pagination"}) is not None:
		posts = int(soup.find("div", {"class": "pagination"}).getText().split(" posts")[0])
	temp = 20
	work(idx)
	while posts > 20:
		posts -= 20
		work(str(idx) + "&start=" + str(temp))
		temp += 20


def work(idx):
	data = OrderedDict({'YoWorld': []})
	site = url + str(idx)
	print("Working on " + site)
	page = requests.get(site)
	soup = BeautifulSoup(page.content, "html.parser")
	for dl in soup.findAll("dl", {"class": "postprofile"}):
		name = dl.select('dt')[0].text.strip().split(" (")[0]
		player = dl.select('dt')[0].text.strip().replace(name + " (", "").replace(")", "")
		if not player.isnumeric():
			player = 0
		date = dl.select('dd')[1].text.strip().replace("YoWorld Start Date: ", "")
		level = dl.select('dd')[0].text.strip().replace("YoWorld Level: ", "")
		data['YoWorld'].append(OrderedDict({
			'player': player,
			'name': name,
			'start_date': date,
			'level': level
		}))
	file = open('out.json', 'w')
	s = set()
	temp = OrderedDict({'YoWorld': []})
	obj = OrderedDict(data)
	obj['YoWorld'] = sorted(obj['YoWorld'], key=lambda x: int(x['player']))
	for d in obj['YoWorld']:
		if str(d) not in s:
			s.add(str(d))
			temp['YoWorld'].append(OrderedDict(d))
	file.write(json.dumps(OrderedDict(temp), indent=4, sort_keys=False))


def done(idx):
	file = open(history, 'a')
	file.write("\n" + str(idx))
	file.close()



thread_list = []
while id <= end:
	for i in range(int(t)):
		if id <= end:
			thread = threading.Thread(target=process, args=(id,))
			thread_list.append(thread)
			id += 1
			thread.start()
	thread.join()
	done(id-1)
for thread in thread_list:
	thread.join()
uniqsort()