# -*- coding: utf-8 -*-
"""
	fyircd.user
	~~~~~~~~~~~~~~~~
	:license: BSD, see LICENSE for more details.
"""
import time, logging
import regex as re
import socket as pysocket
import gevent
import uuid
import hashlib

class UserModes(object):
	supported_modes = {
		# https://github.com/LukeB42/psyrcd/blob/master/psyrcd.py - Uppercase modes are oper-only
		'A': "IRC Administrator.",
		#           'b':"Bot.",
		'D': "Deaf. User does not recieve channel messages.",
		'H': "Hide ircop line in /whois.",
		#           'I':"Invisible. Doesn't appear in /whois, /who, /names, doesn't appear to /join, /part or /quit",
		'L': "Connection is a remote server link.",
		'N': "Network Administrator.",
		'O': "IRC Operator.",
		#           'P':"Protected. Blocks users from kicking, killing, or deoping the user.",
		#           'p':"Hidden Channels. Hides the channels line in the users /whois",
		'Q': "Kick Block. Cannot be /kicked from channels.",
		'S': "See Hidden Channels. Allows the IRC operator to see +p and +s channels in /list",
		'W': "Wallops. Recieve connect, disconnect and traceback notices.",
		#           'X':"Whois Notification. Allows the IRC operator to see when users /whois him or her.",
		'x': "Masked hostname. Hides the users hostname or IP address from other users.",
		'r': "Registed user ... Try /msg nickserv help",
		'Z': "SSL connection."
	}

	def __init__(self, user):
		self.data = {'x': 1, 'r' : 0}
		self.user = user

	@staticmethod
	def concat():
		return ''.join(UserModes.supported_modes.keys())

	def concat_used(self):
		s = '+'
		for key, value in self.data.items():
			if value == 1:
				s += str(key)
		return s

	def send(self):
		s = '+'
		for key, value in self.data.items():
			if value == 1:
				s += key

		if len(s) > 1:
			self.user.write('MODE %s %s' % (self.user.nickname, s))


class User(object):
	re_nick = re.compile(r"^[][\`_^{|}A-Za-z][][\`_^{|}A-Za-z0-9]{0,50}$")
	by_nick = {}

	#: this is used for services like nickserv.
	@staticmethod
	def fake(data, server):
		user = User(None, None, server, data)

		return user

	#: get an user instance for nickname
	@staticmethod
	def by_nickname(nick):
		if nick.lower() in User.by_nick:
			return User.by_nick[nick.lower()]
		return False

	def __init__(self, socket, address, server, data=False):

		self.server = server
		self.logger = logging.getLogger('fyircd')

		if not data:
			self.ip = address[0]
			self.socket = socket
			self.socket_file = socket.makefile('rbw', -1)
			self.fake = False
			self.logger.info('*** New user: {1} / {0}'.format(socket, address[0]))
		else:
			self.fake = True
			self.socket = uuid.uuid4()
			
		self.modes = UserModes(self)
		self.channels = set()
		self.relatives = set()
		self.ping = time.time()
		self.greet = False
		self.killed_by = None
		self.nickname = None
		self.reverse = None
		self.username = "unknown"
		self.realname = "unknown"
		self.hostname = None
		self.vhost = None
		self.oper = False
		self.quit_txt = ""
		self.disconnected = False
		self.away = None
		self.created = int(time.time())
		self.idle = self.created
		
		self.service_user = None


		if self.fake:
			if data['oper'] == True:
				self.oper = True
				self.modes.data['O'] = 1
				self.modes.data['W'] = 1

			self.nickname = data['nickname']
			self.realname = data['realname']
			self.hostname = data['hostname']
			self.username = data['nickname']
			self.greet = True
			self.logger.info('*** New fake user: {0} / {1}'.format(self.socket, self.nickname))
			User.by_nick[self.nickname.lower()] = self

		elif not self.fake:
			if self.ip in self.server.host_cache:
				self.hostname = self.server.host_cache[self.ip]
			else:
				try:
					self.hostname = pysocket.gethostbyaddr(self.ip)[0]
				except:
					self.hostname = self.ip

				self.server.host_cache[self.ip] = self.hostname

			if self.modes.data['x'] == 1:
				self.hostname = hashlib.new('sha512', self.hostname.encode('utf-8')).hexdigest(
				)[:len(self.hostname.encode('utf-8'))] + server.config['hostmask']

	#: user has been greeted?
	def is_ready(self):
		return self.greet

	#: used for nick
	def rename(self, new_name):
		User._update_nickname(self.nickname, new_name, self)
		self.nickname = new_name

	#: used for idle & exts.
	def update(self, line):
		if 'PONG :' not in line:
			self.idle = int(time.time())

	#: reply to ping
	def update_ping(self):
		self.ping = int(time.time())

	#: used for quit
	def quit(self, msg=''):
		self.quit_txt = msg

		if not self.disconnected:
			self.write('QUIT: Closing Link: %s' % self.quit_txt)

		if self.killed_by:
			self.write_relatives(':%s KILL %s :%s' % (self.killed_by, self.nickname, self.quit_txt), True)
		else:
			self.write_relatives(':%s QUIT :%s' % (self, self.quit_txt), True)



		self.disconnect()

	#: disconnect the user close the socket.
	def disconnect(self):
		if not self.disconnected:
			self.disconnected = True

			for channel in self.channels:
				channel.users.discard(self)

			relatives_copy = self.relatives.copy()
			for cuser in relatives_copy:
				cuser.relatives.discard(self)
			del relatives_copy

			if self.nickname.lower() in User.by_nick:
				del User.by_nick[self.nickname.lower()]

			
			self.socket.shutdown(gevent.socket.SHUT_WR)
			self.socket.close()
			self.logger.info('*** User disconnected: %s', self.nickname)

	#: join a channel
	def join(self, channel):
		if channel not in self.channels:
			self.channels.add(channel)
			channel.join(self)

	#: being kick from a channel by source
	def kick(self, source, channel, reason):
		if channel in self.channels:
			self.channels.discard(channel)
			channel.kick(source, self, reason)

	#: leave a channel
	def part(self, channel):
		if channel in self.channels:
			self.channels.discard(channel)
			channel.part(self)

	#: privmsg or notice
	def privmsg(self, source, target, msg, t='PRIVMSG'):
		from fyircd.channel import Channel # :bouh

		the_target_str = ''
		if isinstance(target, str):
			if '#' in target:
				c = Channel.by_id(target)
				if not c:
					return
				the_target_str = c.name
			else:
				u = User.by_nickname(target)
				if not u:
					return
				the_target_str = c.nickname
		elif isinstance(target, User):
			the_target_str = target.nickname
		elif isinstance(target, Channel):
			the_target_str = target.name

		if not the_target_str or the_target_str == '':
			return

		target.write(
			':%s %s %s :%s' % (
				source, t, the_target_str,
				msg
			)
		)

	#: helper with server.name (see IRC RFC)
	def send(self, data):
		self.write(':%s %s' % (self.server.name, data))

	#: raw writing
	def write(self, data):
		if not self.fake and self.disconnected == False:
			print('>>>>>>>>>', '{0}\r\n'.format(data))
			self.socket_file.write(bytes('{0}\r\n'.format(data), 'utf-8'))
			self.socket_file.flush()
			
			


	#: send a message to all relatives, used for quit (for example)
	def write_relatives(self, data, ignore_me=False):
		relatives_copy = self.relatives.copy()
		for relative in relatives_copy:
			relative.write(data)

		del relatives_copy
		if not ignore_me:
			self.write(data)

	#: same as send but to all relatives
	def send_relatives(self, data, ignore_me=False):
		for relative in self.relatives:
			relative.send(data)

		if not ignore_me:
			self.send(data)

	#: helper for rename
	def _update_nickname(old, new, user):
		User.by_nick[new.lower()] = user

		if old:
			del User.by_nick[old.lower()]

	#: return a string corresponding to the user IRC style: nick!username@hostname
	def __str__(self):
		if self.nickname:
			return '%s!%s@%s' % (self.nickname, self.username, self.hostname)
		else:
			return self.ip
