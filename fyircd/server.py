# -*- coding: utf-8 -*-
import time, logging, signal, sys, datetime
from gevent.server import StreamServer
from gevent.pool import Pool
import gevent.monkey
gevent.monkey.patch_all()

from fyircd.user import User
from fyircd.message import Message


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
        self.users = {}
        self.users_by_nick = {}

        self.channels = {}
        self.services = []
        self.extensions = []
        self.host_cache = {}

        self.before_message_funcs = {}
        self.after_message_funcs = {}
        self.on_connect_funcs = {}
        self.on_disconnect_funcs = {}

        if config.get('motd'):
            with open(config['motd']) as f:
                self.motd = f.readlines()
        else:
            self.motd = [self.name]

    def handle(self, socket, address):
        user = User(socket, address, self)
        while True:
            try:
                line = user.socket_file.readline()
            except:
                break

            if not line:
                user.quit('Write error: Connection reset by peer')
                break
            else:
                print('<<<<<<<<< :: {0}'.format(line))
                user.update(line)
                raw, params = Message.from_string(line)
                message = Message(user, raw=raw, params=params)

        del self.users[socket]
        user.quit('Write error: Connection reset by peer')

    def update(self):
        _users = [user for user in self.users.values() if (time.time() - user.ping) > self.ping_timeout]
        for user in _users:
            user.quit('Ping timeout: {0}'.format(int(time.time() - user.ping)))

        half_timeout = self.ping_timeout / 2.0
        _users = [user for user in self.users if (time.time() - user.ping) > half_timeout]
        for user in _users:
            try:
                # send ping
                pass
            except socket.error:
                user.quit("Write error: Connection reset by peer")

    def signal_handler(self, signum, frame):
        self.logger.info('Stoping FyIRCd ... Byebye.')
        if self.server:
            self.server.close()

        sys.exit(0)

    def run(self):
        signal.signal(signal.SIGINT, self.signal_handler)

        self.pool = Pool(10000)

        self.server = StreamServer((self.host, self.port), self.handle, spawn=self.pool)

        self.logger.info('Starting FyIRCd on {0}:{1}'.format(self.host, self.port))

        self.server.serve_forever()
