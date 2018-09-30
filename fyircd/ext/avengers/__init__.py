# -*- coding: utf-8 -*-
"""
    fyircd.ext.avengers
    ~~~~~~~~~~~~~~~~
    Services ^_^
    :license: BSD, see LICENSE for more details.
"""
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, synonym, Session

from fyircd.ext import add_fake_user, add_user_privmsg_callback, add_chan_privmsg_callback, on_server_ready, on_create_chan
from fyircd.user import User
from fyircd.channel import Channel

db_string = 'sqlite:///services.db'
engine = create_engine(db_string)

Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

bot_list = [
	'Deadpool', 'BlackWindow', 'Domino', 'Thor', 'IronMan', 'TheWasp', 'Hulk', 'TheCaptain', 'Hawkeye', 'ScarletWitch', 
	'BackPanther', 'Mantis', 'She-Hulk', 'DoctorStrange', 'Spider-Man', 'Vision', 'WarMachine', 'Logan'
]
bot_list_lower = [v.lower() for v in bot_list]

class AvengerUser(Base):
	__tablename__ = 'user'
	nick = Column(String(50), primary_key=True)
	_password = Column('password', String(120), nullable=False)
	email = Column(String(50))

	def _get_password(self):
		return self._password

	def _set_password(self, password):
		if not password:
			return

		self._password = generate_password_hash(password)

	password = synonym('_password', descriptor=property(_get_password, _set_password))

class AvengerChan(Base):
	__tablename__ = 'chan'
	id = Column(String(50), primary_key=True)
	name = Column(String(50))
	bot = Column(String(50), index=True, nullable=True)
	topic = Column(String(250), nullable=True)
	id_owner = Column(String(50), ForeignKey('user.nick'))

def _on_load():

	add_fake_user({
		'nickname' : 'NickServ',
		'realname' : 'NickServ',
		'hostname' : 'nickserv.fy.to',
		'oper'	   : True
	})
	add_fake_user({
		'nickname' : 'ChanServ',
		'realname' : 'ChanServ',
		'hostname' : 'chanserv.fy.to',
		'oper'	   : True
	})
	add_fake_user({
		'nickname' : 'Loki',
		'realname' : 'Loki',
		'hostname' : 'Loki.fy.to',
		'oper'	   : True
	})

	add_user_privmsg_callback('Loki'.lower(), operserv)
	add_user_privmsg_callback('ChanServ'.lower(), chanserv)
	add_user_privmsg_callback('NickServ'.lower(), nickserv)

	for bot in bot_list:
		add_fake_user({
			'nickname' : bot,
			'realname' : bot,
			'hostname' : 'avengers.fy.to',
			'oper'	   : True
		})

	on_server_ready(on_ready)
	return 'Avenger Services for FyIRCd - by Fy <m@fy.to>'

def on_ready(server):
	try:
		channels = session.query(AvengerChan).all()
	except:
		channels = []

	for chan in channels:
		on_create_chan(chan.name.lower(), chanserv_on_create)
		if chan.bot != None:
			add_chan_privmsg_callback(chan.id, chanserv_on_privmsg)


def chanserv_on_privmsg(target, channel, params):
	args = params[1].lower().split(' ')
	chan = session.query(AvengerChan).filter(AvengerChan.id==channel.id).first()
	if chan.bot != None:
		bot = User.by_nickname(chan.bot)
		if bot:
			if target.service_user != None:
				if target.service_user.nick == chan.id_owner:
					print(args)
					if args[0] == '!topic' and len(args) > 1:
						chan.topic = ' '.join(params[1].split(' ')[1:])
						session.commit()
						channel.change_topic(bot, chan.topic)
					elif args[0] == '!op':
						if len(args) == 1:
							channel.modes.add(bot, ['', '+o', target.nickname])
						else:
							user = User.by_nickname(args[1])
							if user:
								channel.modes.add(bot, ['', '+o', user.nickname])
					elif args[0] == '!deop':
						if len(args) == 1:
							channel.modes.add(bot, ['', '-o', target.nickname])
						else:
							user = User.by_nickname(args[1])
							if user:
								channel.modes.add(bot, ['', '-o', user.nickname])
					elif args[0] == '!voice':
						if len(args) == 1:
							channel.modes.add(bot, ['', '+v', target.nickname])
						else:
							user = User.by_nickname(args[1])
							if user:
								channel.modes.add(bot, ['', '+v', user.nickname])
					elif args[0] == '!devoice':
						if len(args) == 1:
							channel.modes.add(bot, ['', '-v', target.nickname])
						else:
							user = User.by_nickname(args[1])
							if user:
								channel.modes.add(bot, ['', '-v', user.nickname])
					elif args[0] == '!owner':
						if len(args) == 1:
							channel.modes.add(bot, ['', '+ovhqa', target.nickname])
						else:
							user = User.by_nickname(args[1])
							if user:
								channel.modes.add(bot, ['', '+ovhqa', user.nickname])
					elif args[0] == '!rip':
						if len(args) == 1:
							channel.modes.add(bot, ['', '-ovhqa', target.nickname])
						else:
							user = User.by_nickname(args[1])
							if user:
								channel.modes.add(bot, ['', '+ovhqa', user.nickname])

def chanserv_on_create(channel):
	chan = session.query(AvengerChan).filter(AvengerChan.id==channel.id).first()
	if chan.bot != None:
		bot = User.by_nickname(chan.bot)
		bot.join(channel)

		channel.modes.add(bot, ['', '+r'])
		channel.modes.add(bot, ['', '+ovhqa', bot.nickname])

		channel.write(':%s %s %s :%s' % (bot, 'PRIVMSG', channel.name, 'Yo!'))
		if chan.topic != None:
			channel.change_topic(bot, chan.topic)

		for user in channel.users:
			if user.nickname.lower() != chan.bot.lower():
				channel.modes.add(user, ['', '-ovhqa', user.nickname])


def operserv(target, params):
	operserv = User.by_nickname('loki')
	args = params[1].lower().split(' ')
	if target.oper == False:
		target.write(':%s %s %s :%s' % (operserv, 'NOTICE', target.nickname, 'Enough! You are, all of you are beneath me! I am a god, you dull creature, and I will not be bullied ... YOU\'RE NOT A GOD HERE!'))
	elif args[0] == 'initdb':
		Base.metadata.create_all(engine)
		for bot in bot_list:
			_bot = User.by_nickname(bot)
			_bot_chans = _bot.channels.copy()
			for chan in _bot_chans:
				_bot.part(chan)

		for user in target.server.users.values():

			user.modes.data['r'] = 0
			user.service_user = None
			user.modes.send()
			user.write(':%s %s %s :%s' % (operserv, 'NOTICE', target.nickname, 'Service Database has been wiped - please use /msg nickserv help ^_^'))


def chanserv(target, params):
	chanserv = User.by_nickname('chanserv')
	args = params[1].lower().split(' ')
	if args[0] == 'register':
		if len(args) == 2:
			channel = Channel.by_id(args[1])
			if not channel:
				target.write(':%s %s %s :%s' % (chanserv, 'NOTICE', target.nickname, 'Nope --- Register: You obviously need to be on the channel.'))
			if target not in channel.modes.data['q']:
				target.write(':%s %s %s :%s' % (chanserv, 'NOTICE', target.nickname, 'Nope --- Register: You\'re not the owner of this channel. But nice try. Dream big!'))
			else:
				exist = session.query(AvengerChan).filter(AvengerChan.name==channel.name).first()
				if exist:
					target.write(':%s %s %s :%s' % (chanserv, 'NOTICE', target.nickname, 'Nope --- Register: This channel is already registered.'))
				else:
					if target.modes.data['r'] == 1 and target.service_user != None:
						chan = AvengerChan(id=channel.id, name=channel.name, id_owner=target.service_user.nick, bot=None)
						session.add(chan)
						session.commit()
						channel.modes.add(chanserv, ['', '+r'])
						on_create_chan(chan.name.lower(), chanserv_on_create)
					else:
						target.write(':%s %s %s :%s' % (chanserv, 'NOTICE', target.nickname, 'Nope --- Register: You need to be logged with NickServ.'))
		else:
			target.write(':%s %s %s :%s' % (nickserv, 'NOTICE', target.nickname, 'Register: /msg chanserv register <chan>'))

	elif args[0] == 'assign':
		if len(args) == 3:
			channel = Channel.by_id(args[1])

			if not channel:
				target.write(':%s %s %s :%s' % (chanserv, 'NOTICE', target.nickname, 'Nope --- Assign: You obviously need to be on the channel.'))
			else:
				exist = session.query(AvengerChan).filter(AvengerChan.id==channel.id).first()
				if not exist:
					target.write(':%s %s %s :%s' % (chanserv, 'NOTICE', target.nickname, 'Nope --- Assign: You need to register this channel.'))
				elif exist and target.service_user == None or exist.id_owner != target.service_user.nick:
					target.write(':%s %s %s :%s' % (chanserv, 'NOTICE', target.nickname, 'Nope --- Assign: You are not the owner of this channel. IDENTIFY YOURSELF!'))
				else:
					if args[2].lower() in bot_list_lower:
						exist.bot = args[2].lower()
						session.commit()
						print(bot_list_lower)
						for bot in bot_list_lower:
							_bot = User.by_nickname(bot)
							if _bot.nickname.lower() == args[2].lower():
								_bot.join(channel)
								channel.modes.add(_bot, ['', '+ovhqa', _bot.nickname])
								channel.modes.add(target, ['', '+ovhqa', target.nickname])
								target.write(':%s %s %s :%s' % (_bot, 'PRIVMSG', channel.name, 'Yo!'))
							else:
								_bot.part(channel)
					else:
						target.write(':%s %s %s :%s' % (chanserv, 'NOTICE', target.nickname, 'Nope --- Assign: These aren\'t the droids you\'re looking for - /msg chanserv bots'))


		else:
			target.write(':%s %s %s :%s' % (chanserv, 'NOTICE', target.nickname, 'Assign a bot: /msg chanserv <chan> <bot_name>'))
			target.write(':%s %s %s :%s' % (chanserv, 'NOTICE', target.nickname, 'List all bots: /msg chanserv bots'))

	elif args[0].lower() == 'help':
		target.write(':%s %s %s :%s' % (nickserv, 'NOTICE', target.nickname, '----------------------------------------'))

		target.write(':%s %s %s :%s' % (nickserv, 'NOTICE', target.nickname, 'Help with NickServ: '))
		target.write(':%s %s %s :%s' % (nickserv, 'NOTICE', target.nickname, 'Register: /msg nickserv register <pass> <mail> '))
		target.write(':%s %s %s :%s' % (nickserv, 'NOTICE', target.nickname, 'Identify: /msg nickserv identify <pass> '))

		target.write(':%s %s %s :%s' % (nickserv, 'NOTICE', target.nickname, '----------------------------------------'))

		target.write(':%s %s %s :%s' % (nickserv, 'NOTICE', target.nickname, 'Help  with ChanServ: '))
		target.write(':%s %s %s :%s' % (nickserv, 'NOTICE', target.nickname, 'Register: /msg chanserv register <chan>'))
		target.write(':%s %s %s :%s' % (nickserv, 'NOTICE', target.nickname, 'Assign a bot: /msg chanserv <chan> <bot_name>'))
		target.write(':%s %s %s :%s' % (nickserv, 'NOTICE', target.nickname, 'List all bots: /msg chanserv bots'))

		target.write(':%s %s %s :%s' % (nickserv, 'NOTICE', target.nickname, '----------------------------------------'))
	else:
		target.write(':%s %s %s :%s' % (nickserv, 'NOTICE', target.nickname, '❓ Donde esta la biblioteca ❓ (try /msg ChanServ help)'))

def nickserv(target, params):
	nickserv = User.by_nickname('nickserv')
	args = params[1].lower().split(' ')
	if args[0] == 'register':
		if len(args) != 3:
			target.write(':%s %s %s :%s' % (nickserv, 'NOTICE', target.nickname, 'Nope --- Register: /msg nickserv register <pass> <mail> '))
		else:
			exist = session.query(AvengerUser).filter(AvengerUser.nick==target.nickname.lower()).first()
			if exist:
				target.write(':%s %s %s :%s' % (nickserv, 'NOTICE', target.nickname, '.... This nickname is already registered.'))
			else:
				user = AvengerUser(nick=target.nickname.lower(), password=args[1], email=args[2])
				session.add(user)
				target.write(':%s %s %s :%s' % (nickserv, 'NOTICE', target.nickname, 'GG, Welcome!. Now use /msg nickserv identify <pass>.'))
				session.commit()
	elif args[0] == 'identify':
		if len(args) != 2:
			target.write(':%s %s %s :%s' % (nickserv, 'NOTICE', target.nickname, 'Nope --- Register: /msg nickserv identify <pass> '))
		else:
			user = session.query(AvengerUser).filter(AvengerUser.nick==target.nickname.lower()).first()
			if check_password_hash(user.password, args[1]):
				target.write(':%s %s %s :%s' % (nickserv, 'NOTICE', target.nickname, 'Mot de passe accepté - vous êtes maintenant identifié.'))
				target.modes.data['r'] = 1
				target.service_user = user
				target.hostname = user.nick+'.'+target.server.name
				target.modes.send()
			else:
				target.write(':%s %s %s :%s' % (nickserv, 'NOTICE', target.nickname, 'Nice try ... (incorrect password)'))

	elif args[0].lower() == 'help':
		target.write(':%s %s %s :%s' % (nickserv, 'NOTICE', target.nickname, '----------------------------------------'))

		target.write(':%s %s %s :%s' % (nickserv, 'NOTICE', target.nickname, 'Help with NickServ: '))
		target.write(':%s %s %s :%s' % (nickserv, 'NOTICE', target.nickname, 'Register: /msg nickserv register <pass> <mail> '))
		target.write(':%s %s %s :%s' % (nickserv, 'NOTICE', target.nickname, 'Identify: /msg nickserv identify <pass> '))

		target.write(':%s %s %s :%s' % (nickserv, 'NOTICE', target.nickname, '----------------------------------------'))

		target.write(':%s %s %s :%s' % (nickserv, 'NOTICE', target.nickname, 'Help  with ChanServ: '))
		target.write(':%s %s %s :%s' % (nickserv, 'NOTICE', target.nickname, 'Register: /msg chanserv register <chan>'))
		target.write(':%s %s %s :%s' % (nickserv, 'NOTICE', target.nickname, 'Assign a bot: /msg chanserv <chan> <bot_name>'))
		target.write(':%s %s %s :%s' % (nickserv, 'NOTICE', target.nickname, 'List all bots: /msg chanserv bots'))

		target.write(':%s %s %s :%s' % (nickserv, 'NOTICE', target.nickname, '----------------------------------------'))
	else:
		target.write(':%s %s %s :%s' % (nickserv, 'NOTICE', target.nickname, '❓ Donde esta la biblioteca ❓ (try /msg NickServ help)'))

