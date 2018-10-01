# -*- coding: utf-8 -*-
"""
	fyircd.server
	~~~~~~~~~~~~~~~~
	:license: BSD, see LICENSE for more details.
"""
import time, logging, signal, sys, datetime
from gevent.server import StreamServer
from gevent.pool import Pool
from gevent import monkey
monkey.patch_all()
from gevent import Greenlet
from gevent import sleep

from fyircd.user import User
from fyircd.message import Message
from fyircd.ext import fake_users, load_ext, when_server_ready
from fyircd.channel import Channel


def decode_irc(bytes):
    try:
        text = bytes.decode('utf-8')
    except UnicodeDecodeError:
        try:
            text = bytes.decode('iso-8859-1')
        except UnicodeDecodeError:
            text = bytes.decode('cp1252')
    return text


class Server(object):
    default_config = {
        'secret_key': None,
        'name': None,
        'host': '0.0.0.0',
        'port': 6667,
        'debug': False,
        'ipv6': False,
        'ping_timeout': 240.0
    }

    def __init__(self, config):

        self.config = config

        self.ipv6 = self.config.get('ipv6') or Server.default_config['ipv6']
        self.host = self.config.get('host') or Server.default_config['host']
        self.port = self.config.get('port') or Server.default_config['port']
        self.name = self.config.get('name') or Server.default_config['name']
        self.debug = self.config.get('debug') or Server.default_config['debug']
        self.ping_timeout = self.config.get('ping_timeout') or Server.default_config['ping_timeout']
        self.version = 'FyIRCd 0.1.0'
        self.logger = logging.getLogger('fyircd')
        self.created = datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p")

        self.services = []
        self.host_cache = {}

        for ext in config.get('exts'):
            load_ext(ext)

        for user_data in fake_users:
            u = User.fake(user_data, self)

        if config.get('motd'):
            with open(config['motd']) as f:
                self.motd = f.readlines()
        else:
            self.motd = [self.name]

        for cb in when_server_ready:
            cb(self)

    def handle(self, socket, address):

        user = User(socket, address, self)
        #: gevent.Greenlet.spawn(Server.is_alive, socket)
        #: gevent.Greenlet.spawn(Server.update, socket) gevent.sleep(5)
        #: gevent.Greenlet.spawn(self.update, user)
        while True:
            try:
                line = user.socket_file.readline()
            except:
                break

            print('<<<<<<<<< :: {0}'.format(line))

            line = decode_irc(line)
            user.update(line)
            raw, params = Message.from_string(line)
            message = Message(user, raw=raw, params=params)

        user.quit('Write error: Connection reset by peer')

    def update_all(self):
        _users = [
            user for user in User.by_nick.values()
            if user.fake == False and user.greet == True and (time.time() - user.ping) > self.ping_timeout
        ]
        for user in _users:
            user.quit('Ping timeout: {0}'.format(int(time.time() - user.ping)))

        half_timeout = self.ping_timeout / 2.0

        _users = [
            user for user in User.by_nick.values()
            if user.fake == False and user.greet == True and (time.time() - user.ping) > half_timeout
        ]
        for user in _users:
            user.write('PING :%s' % (self.name))

        sleep(5)

    def signal_handler(self, signum, frame):
        self.logger.info('Stoping FyIRCd ... Byebye.')
        if 'avengers' in self.config.get('exts'):
            operserv = User.by_nickname('loki')
            _users = User.by_nick.copy()

            for user in _users.values():
                if user.fake == False and user.greet:
                    user.write(
                        ':%s %s %s :%s' % (
                            operserv, 'NOTICE', user.nickname,
                            'The world is ending ... it\'s possible it\'s just a restart... FyIRCd is not stable ^_^ https://github.com/Fy-/Fy_IRCd'
                        )
                    )
                    user.quit('The world is ending')

        if self.server:
            self.server.stop()

        sys.exit(0)

    def run(self):
        signal.signal(signal.SIGINT, self.signal_handler)

        self.pool = Pool(10000)

        Greenlet.spawn(self.update_all)
        self.server = StreamServer((self.host, self.port), self.handle, spawn=self.pool)

        self.logger.info('Starting FyIRCd on {0}:{1}'.format(self.host, self.port))

        self.server.serve_forever()
