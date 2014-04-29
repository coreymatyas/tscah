#!/usr/bin/python

from random import shuffle, seed
import sys, telnetlib, re, time, copy, argparse

adminUIDs = []
bot_nickname = "TSCAH"

keep_alive_time = 30
round_length = 60
white_filename = "whitecards.txt"
black_filename = "blackcards.txt"
replacements = [[92,92],[47,47],[32,115],[124,112],[7,97],[8,98],[12,102],[10,110],[13,114],[9,116],[1,118]]

loop_running = True
keep_alive = 0

cid = 1
game_running = False
current_players = {}
czar = None
current_black = None
deck = None
r_cards = None
offered_cards = {}
round_start = 0

inqueue = []
outqueue = []
events = []

class Event(object):
	type = ''
	params = {}
	def __init__(self, type, params):
		self.type = type
		self.params = params

class Deck(object):
	white_cards = []
	black_cards = []
	white_discard = []
	black_discard = []

	def __init__(self):
		self.reset()

	def draw(self):
		shuffle(self.white_cards)
		if len(self.white_cards) > 0:
			new_white = self.white_cards.pop(0)
			self.white_discard.append(new_white)
			return new_white
		else:
			self.white_cards, self.white_discard = self.white_discard, self.white_cards
			shuffle(self.white_cards)
			return self.draw()

	def black(self):
		shuffle(self.black_cards)
		if len(self.black_cards) > 0:
			new_black = self.black_cards.pop(0)
			self.black_discard.append(new_black)
			return new_black
		else:
			self.black_cards, self.black_discard = self.black_discard, self.black_cards
			shuffle(self.black_cards)
			return self.black()

	def reset(self):
		white_file = open(white_filename, 'r')
		black_file = open(black_filename, 'r')
		self.white_cards = white_file.read().split('\n')
		self.black_cards = black_file.read().split('\n')
		white_file.close()
		black_file.close()
		self.white_discard = []
		self.black_discard = []

class Player(object):
	clid = 0
	uid = ''
	name = ''
	cards = []
	points = 0
	needs_cards = 10

	def __init__(self, clid, uid, name):
		self.clid, self.uid, self.name = clid, uid, name
		self.cards = []
		self.draw()

	def draw(self):
		if self.uid != czar:
			for i in range(self.needs_cards):
				self.cards.append(deck.draw())

	def awesome(self):
		self.points += 1

def t_encode(text):
	for replacement in replacements:
		text = text.replace(chr(replacement[0]), '\\' + chr(replacement[1]))
	return text

def t_decode(text):
	for replacement in replacements:
		text = text.replace('\\' + chr(replacement[1]), chr(replacement[0]))
	return text

def t_send(line):
	outqueue.append(line)

def t_send_channel_message(msg):
	t_send("sendtextmessage targetmode=2 target=%s msg=%s\n" % (cid, t_encode(msg)))

def t_send_priv_message(clid, msg):
	t_send("sendtextmessage targetmode=1 target=%s msg=%s\n" % (clid, t_encode(msg)))

def none_check(value, default):
	if value == None:
		return default
	return value

def fill_blank(black, white):
	if '___' in black:
		return black.replace('___', white)
	else:
		return black + ' ' + white

def process_events():
	for line in inqueue:
		new_event = None
		if line.startswith("notifytextmessage"):
			new_event = Event("textmessage", dict(
				targetmode=none_check(re.compile('targetmode=([0-9]+)').search(line), re.match('a(.)?', 'a ')).group(1), 
				msg=t_decode(none_check(re.compile('msg=([^\s]+)').search(line), re.match('a(.)?', 'a ')).group(1)),
				invokerid=none_check(re.compile('invokerid=([0-9]+)').search(line), re.match('a(.)?', 'a ')).group(1), 
				invokername=t_decode(none_check(re.compile('invokername=([^\s]+)').search(line), re.match('a(.)?', 'a ')).group(1)), 
				invokeruid=none_check(re.compile('invokeruid=([0-9a-zA-Z=]+)').search(line), re.match('a(.)?', 'a ')).group(1)))
		elif line.startswith("notifyclientmoved"):
			new_event = Event("clientmoved", dict(
				ctid=re.compile('ctid=([0-9]+)').search(line).group(1), 
				reasonid=re.compile('reasonid=([0-9]+)').search(line).group(1), 
				clid=re.compile('clid=([0-9]+)').search(line).group(1)))
		elif line == None:
			continue
		else:
			new_event = Event("raw", [['text', line]])
		events.append(new_event)
	inqueue[:] = []

def run_game():
	global loop_running, game_running, current_black, current_players, offered_cards, r_cards, round_start, czar, deck

	players_noczar = copy.deepcopy(current_players)
	players_noczar.pop(czar, None)

	if len(events) != 0:
		event = events.pop(0)
		if event.type == "textmessage":
			if event.params['msg'] == "diebot" and (event.params['invokeruid'] in adminUIDs or not adminUIDs):
				t_send_channel_message("Goodbye!")
				loop_running = False
			if event.params['msg'] == "join" and not event.params['invokeruid'] in current_players.keys() and not game_running:
				current_players[event.params['invokeruid']] = Player(event.params['invokerid'], event.params['invokeruid'], event.params['invokername'])
				t_send_priv_message(event.params['invokerid'], "Welcome to TSCAH!")
			elif event.params['msg'] == "quit" and not game_running:
				current_players.pop(event.params['invokeruid'], None)
			if event.params['msg'] == "listplayers":
				t_send_channel_message("Current Players: " + ' / '.join([x.name + " - " + str(x.points) for x in current_players.values()]))
			elif event.params['msg'] == "help":
				help_string = 	("Help ---\n"
								"join - Enter the current TSCAH game or lobby.\n"
								"quit - Leave the current TSCAH game or lobby.\n"
								"startgame - Start a game of TSCAH.\n"
								"stopgame - Stop the current game of TSCAH.\n"
								"listplayers - Show players in order of play with current scores.")
				t_send_channel_message(help_string)
			elif event.params['msg'] == "startgame" and len(current_players) > 1:
				game_running = True
				round_start = time.time()
				offered_cards = {}
				current_black = deck.black()
				if czar == None:
					czar = current_players.keys()[0]
				t_send_channel_message("Card Czar: " + current_players[czar].name)
				t_send_channel_message("Black Card: " + current_black)
				t_send_channel_message("Type \"choose <number>\" to choose your card!")
				for player in players_noczar:
					current_players[player].needs_cards = 0
					send_line = "Your cards are: \n"
					for i in range(len(current_players[player].cards)):
						send_line += str(i) + " - " + current_players[player].cards[i] + "\n"
					t_send_priv_message(current_players[player].clid, send_line)
			elif event.params['msg'] == "stopgame":
				game_running = False
				current_black = None
				current_players = {}
				czar = None
				offered_cards = {}
				r_cards = None
				round_start = 0
				deck.reset()
			elif event.params['msg'].startswith("choose") and not (event.params['invokeruid'] in offered_cards.keys()) and event.params['invokeruid'] != czar and game_running:
					if re.match('^choose [0-9]$', event.params['msg']):
						offered_cards[event.params['invokeruid']] = current_players[event.params['invokeruid']].cards.pop(int(event.params['msg'].split(' ')[1]))
						current_players[event.params['invokeruid']].needs_cards = 1
					else:
						t_send_channel_message(event.params['invokername'] + ", please choose a card number 0-9.")
			elif event.params['msg'].startswith("final") and current_black != None and event.params['invokeruid'] == czar:
				if re.match('^final [0-%d]$' % (len(r_cards) - 1), event.params['msg']):
					winner = current_players[r_cards[int(event.params['msg'].split(' ')[1])][0]]
					next_czar = current_players.keys().index(czar) + 1

					for player in players_noczar:
						t_send_priv_message(current_players[player].clid, "---------------------------------------------")
						current_players[player].draw()

					czar = current_players.keys()[next_czar if next_czar < len(current_players) else 0]
					t_send_channel_message("Winner: " + winner.name + " // " + fill_blank(current_black, offered_cards[winner.uid]))
					t_send_channel_message("---------------------------------------------")
					winner.awesome()
					events.append(Event("textmessage", dict(msg="startgame", invokeruid=(adminUIDs[0] if adminUIDs else ''))))
				else:
					t_send_channel_message(event.params['invokername'] + ", please choose a card number 0-%d." % (len(r_cards) - 1))
		elif event.type == "clientmoved":
			if event.params['ctid'] == cid:
				t_send_priv_message(event.params['clid'], "Welcome to the TSCAH Channel! Type 'help' for a command list.")
				t_send_priv_message(event.params['clid'], "There is " + ("" if game_running else "not") + " currently a game in progress.")
			else:
				kick_player = ''
				for player in current_players:
					if current_players[player].clid == event.params['clid']:
						kick_player = current_players[player].uid
				current_players.pop(kick_player, None)

	if (reduce((lambda x, y: y in offered_cards.keys() if x else False), players_noczar, True) or (round_start + round_length < time.time())) and game_running:
		r_cards = offered_cards.items()
		shuffle(r_cards)
		t_send_channel_message("Black Card: " + current_black)
		if len(r_cards) == 0:
			t_send_channel_message("Nobody submitted a card in time! You all lose!")
			events.append(Event("textmessage", dict(msg="startgame", invokeruid=(adminUIDs[0] if adminUIDs else ''))))
		else:
			t_send_channel_message("White Cards: ")
			for i in range(len(r_cards)):
				t_send_channel_message(str(i) + " - " + r_cards[i][1])
			t_send_channel_message(current_players[czar].name + ", type \"final <number>\" to choose the winner!")
		game_running = False

if __name__ == "__main__":
	## TODO: verify functionality, remove intermediary vars, add help messages, add CLI output during play, add verbose option
	parser = argparse.ArgumentParser(description='Cards Against Humanity clone playable in TeamSpeak.')

	parser.add_argument(["-h", "--host"], dest="host", default="localhost")
	parser.add_argument(["-p", "--port"], dest="port", type=int)

	parser.add_argument("username")
	parser.add_argument("password")
	parser.add_argument("channelid")

	args = parser.parse_args()

	# if len(sys.argv) < 5:
	# 	print("Usage: %s <host> <username> <password> <cid> [port]" % sys.argv[0])
	# 	sys.exit(1)

	host = args.host #sys.argv[1]
	username = args.username #sys.argv[2]
	password = args.password #sys.argv[3]
	cid = args.channelid #sys.argv[4]
	port = args.port #int(sys.argv[5]) if len(sys.argv) > 5 else 10011

	seed(time.time())
	deck = Deck()

	tel = telnetlib.Telnet(host, port)

	tel.write("login %s %s\n" % (username, password))
	tel.write("use 1\n")
	tel.write("clientupdate client_nickname=%s\n" % bot_nickname)
	tel.write("whoami\n")
	clid = re.compile('client_id=([0-9]+)').search(tel.read_until("client_origin_server_id")).group(1)
	tel.write("clientmove clid=%s cid=%s\n" % (clid, cid))
	tel.write("servernotifyregister event=channel id=%s\n" % cid)
	tel.write("servernotifyregister event=textchannel id=%s\n" % cid)
	tel.write("servernotifyregister event=textprivate\n")
	
	while loop_running:
		intext = tel.read_very_eager()
		inqueue.extend(intext.split("\n\r"))

		process_events()
		run_game()
		
		if time.time() > (keep_alive + keep_alive_time):
			keep_alive = time.time()
			t_send("version\n")

		if len(outqueue) != 0:
			tel.write(outqueue.pop(0))

	tel.write("quit\n")
	tel.close()
	sys.exit(0)