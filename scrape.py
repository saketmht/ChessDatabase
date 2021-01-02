from bs4 import BeautifulSoup as soup
from urllib.request import Request, urlopen  
import os
import json

def f1(foo): return iter(foo.splitlines())

matches = {}
matches['match'] = []

game_no = 1
for page_number in range(1, 80):
	print("Page : " + str(page_number))
	try:
		url = 'https://lichess.org/@/saketmht/all?page=' + str(page_number)
		req = Request(url, headers={'User-Agent': 'XYZ/3.0'})
		response = urlopen(req, timeout=20).read()
	except:
		continue
	page_soup = soup(response, "html.parser")

	div_container = page_soup.find_all('a', class_='game-row__overlay')
	
	for div in div_container:
		try:
			each_url = 'https://lichess.org' + div["href"]
			each_req = Request(each_url, headers={'User-Agent': 'XYZ/3.0'})
			each_response = urlopen(each_req, timeout=20).read()
		except:
			continue
		each_page_soup = soup(each_response, "html.parser")

		# print(each_url)
		try:
			print(game_no)
			hmm = each_page_soup.find("div", {"class" : "pgn"}).get_text()

			text = list(f1(hmm))

			iswhite = True
			if(text[3] != "[White \"saketmht\"]"):
				iswhite = False

			isDraw = False
			won = False

			if(text[5] == "[Result \"1/2-1/2\"]"):
				isDraw = True
			if((text[5] == "[Result \"1-0\"]" and iswhite == True) or (text[5] == "[Result \"0-1\"]" and iswhite == False)):
				won = True

			moves = text[len(text)-1].split()
			# print(moves)
			move = []
			n = len(moves)
			no = 1
			i = 0
			while i < n: 
				if(moves[i] == (str(no) + '.')): 
					turn = ""
					try:
						turn += moves[i]
						move.append(moves[i+1])
						if(moves[i+2] == '{'):
							i = i+2
							while(moves[i] != '}'):
								i = i+1
							if(i == n - 2): break;
							move.append(moves[i+1])
						else:
							move.append(moves[i+2])
						no = no + 1
					except:
						break
				i = i+1

			x = { "isWhite": iswhite, "isDraw": isDraw, "won": won, "moves": move}
			# print(x)

			matches['match'].append(x)
			game_no = game_no + 1
		except:
			continue

outfile = open('db.json', 'w')
json.dump(matches, outfile)
outfile.close()
# with open('db.json') as file_object:
	# data = json.load(file_object)




