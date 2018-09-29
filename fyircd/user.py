# -*- coding: utf-8 -*-
import time, logging
import regex as re
import socket as pysocket
import gevent


class User(object):
    re_nick = re.compile(r"^[][\`_^{|}A-Za-z][][\`_^{|}A-Za-z0-9]{0,50}$")
    by_nick = {}

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
        'Z': "SSL connection."
    }

    def __init__(self, socket, address, server):
        print('*** New user: {1} / {0}'.format(socket, address[0]))
        self.server = server
        self.logger = logging.getLogger('fyircd')

        self.ip = address[0]
        self.socket = socket
        self.socket_file = socket.makefile('rw', encoding='utf-8')

        self.recv_buffer = ""
        self.send_buffer = ""

        self.modes = {'x': 1}
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
        self.server.users[socket] = self

        if self.ip in self.server.host_cache:
            self.hostname = self.server.host_cache[self.ip]
        else:
            try:
                self.hostname = pysocket.gethostbyaddr(self.ip)[0]
            except:
                self.hostname = self.ip

            self.server.host_cache[self.ip] = self.hostname

    @staticmethod
    def concat_modes():
        return ''.join(User.supported_modes.keys())

    def send_modes(self):
        s = '+'
        for key, value in self.modes.items():
            if value == 1:
                s += key

        if len(s) > 1:
            self._write('MODE %s %s' % (self.nickname, s))

    def rename(self, new_name):
        User.update_nickname(self.nickname, new_name, self)
        self.nickname = new_name

    def update(self, line):
        if 'PONG :' not in line:
            self.idle = int(time.time())

    def update_ping(self):
        self.ping = int(time.time())

    def is_ready(self):
        return self.greet

    @staticmethod
    def by_nickname(nick):
        if nick.lower() in User.by_nick:
            return User.by_nick[nick.lower()]
        return False

    def update_nickname(old, new, user):
        User.by_nick[new.lower()] = user

        if old:
            del User.by_nick[old.lower()]

    def quit(self, msg=''):
        if not self.nickname:
            return self.disconnect(quit=False)

        self.quit_txt = msg
        self._write('QUIT: Closing Link: %s' % self.quit_txt)

        if self.killed_by:
            self.write_relatives(':%s KILL %s :%s' % (self.killed_by, self.nickname, self.quit_txt), True)
        else:
            self.write_relatives(':%s QUIT :%s' % (self, self.quit_txt), True)

        for channel in self.channels:
            channel.users.discard(self)

        relatives_copy = self.relatives.copy()
        for cuser in relatives_copy:
            cuser.relatives.discard(self)
        del relatives_copy
        del User.by_nick[self.nickname.lower()]
        del self.server.users[self.socket]

    def disconnect(self, msg='', quit=True):
        if not self.disconnected:
            if quit:
                self.quit(msg or self.quit_txt)

            self.socket.shutdown(gevent.socket.SHUT_WR)
            self.disconnected = True

    def join(self, channel):
        self.channels.add(channel)
        channel.join(self)

    def part(self, channel):
        self.channels.discard(channel)
        channel.part(self)

    def send(self, data):
        self._write(':%s %s' % (self.server.name, data))

    def _write(self, data):
        self.socket_file.write('{0}\r\n'.format(data))
        self.socket_file.flush()
        print('>>>>>>>>>', '{0}\r\n'.format(data))

    def write_relatives(self, data, ignore_me=False):
        relatives_copy = self.relatives.copy()
        for relative in relatives_copy:
            relative._write(data)

        del relatives_copy
        if not ignore_me:
            self._write(data)

    def send_relatives(self, data, ignore_me=False):
        for relative in self.relatives:
            relative.send(data)

        if not ignore_me:
            self.send(data)

    def get_key(self):
        return self.socket

    def __str__(self):
        if self.nickname:
            return '%s!%s@%s' % (self.nickname, self.username, self.hostname)
        else:
            return self.ip