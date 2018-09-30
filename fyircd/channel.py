# -*- coding: utf-8 -*-
"""
    fyircd.channel
    ~~~~~~~~~~~~~~~~
    :license: BSD, see LICENSE for more details.
"""
import time, logging
import regex as re

from fyircd.user import User
from fyircd.ext  import on_create_channel

class ChannelModes(object):
    mode_to_symbol = {'o': '@', 'v': '+', 'h': '%', 'q': '~', 'a': '&'}

    supported_modes = {
        # https://github.com/LukeB42/psyrcd/blob/master/psyrcd.py - Uppercase modes can only be set and removed by opers.
        'A': "Server administrators only.",
        #               'i':"Invite only.",
        'm': "Muted.",
        'r': 'Register with ChanServ',
        'n': "No messages allowed from users who are not in the channel.",
        'v': "Voiced. Cannot be muted.",
        'h': "Channel half-operators.",
        'o': "Channel operators.",
        'a': "Channel administrators.",
        'q': "Channel owners.",
        'b': "Channel bans.",
        'e': "Exceptions to channel bans.",
        'O': "Server operators only.",
        'l': "Limited amount of users.",
        # 'k':"Password protected.",
        's': "Secret. Hides channel from /list.",
        't': "Only operators may set the channel topic.",
        #            'z':"Only allow clients connected via SSL.",
    }

    def __init__(self, channel):
        self.channel = channel
        self.data = {
            'n': 1,
            't': 1,
            'l': 0,
            'm': 0,
            'r': 0,
            'v': [],
            'h': [],
            'o': [],
            'q': [],
            'a': [],
            'b': [],
            'e': []
        }

    @staticmethod
    def concat():
        return ''.join(ChannelModes.supported_modes.keys())

    def get_prefix(self, user, add=''):
        if user in self.data['q']:
            return add + ChannelModes.mode_to_symbol['q']
        if user in self.data['a']:
            return add + ChannelModes.mode_to_symbol['a']
        if user in self.data['o']:
            return add + ChannelModes.mode_to_symbol['o']
        if user in self.data['h']:
            return add + ChannelModes.mode_to_symbol['h']
        if user in self.data['v']:
            return add + ChannelModes.mode_to_symbol['v']
        return ''

    def allowed(self, user, mode):
        if user.oper:
            return True

        if mode == 'q' and (user in self.data['q']):
            return True
        if mode == 'a' and (user in self.data['q'] or user in self.data['a']):
            return True
        if mode == 'o' and (user in self.data['q'] or user in self.data['a'] or user in self.data['o']):
            return True
        if mode == 'h' and (user in self.data['q'] or user in self.data['a'] or user in self.data['o']):
            return True
        if mode == 'v' and (
            user in self.data['q'] or user in self.data['a'] or user in self.data['o'] or
            user in self.data['h']
        ):
            return True

        return False

    def add(self, user, params):
        data = list(params[1])
        add = False
        if data[0] == '+':
            add = True

        for i in range(1, len(data)):
            if data[i] in ['m', 'n', 's', 't', 'l', 'r']:
                try:
                    target = params[2]
                except:
                    target = None

                if not self.allowed(user, data[i]):
                    return -1  
                if self.data[data[i]] == 0:
                    if data[i] == 'l':
                        if len(params) == 4 and add:
                            self.data['l'] = int(params[3])
                            self.channel.write(
                                ':%s MODE %s %s%s %s' %
                                (user, self.channel.name, data[0], data[i], params[3])
                            )
                        elif add == False:
                            self.data['l'] = 0
                            self.channel.write(
                                ':%s MODE %s %s%s %s' % (user, self.channel.name, data[0], data[i], '')
                            )
                    else:
                        self.data[data[i]] = 1 if add else 0
                        self.channel.write(
                            ':%s MODE %s %s%s %s' % (user, self.channel.name, data[0], data[i], '')
                        )

            if data[i] in ['o', 'v', 'h', 'q', 'a']:
                target = User.by_nickname(params[2])
                if not target:
                    return -2
                else:
                    if self.allowed(user, data[i]):
                        if add:
                            if target not in self.data[data[i]]:
                                self.data[data[i]].append(target)
                                self.channel.write(
                                    ':%s MODE %s %s%s %s' %
                                    (user, self.channel.name, data[0], data[i], target.nickname)
                                )
                        else:
                            if target in self.data[data[i]]:
                                self.data[data[i]].remove(target)
                                self.channel.write(
                                    ':%s MODE %s %s%s %s' %
                                    (user, self.channel.name, data[0], data[i], target.nickname)
                                )
                    else:
                        return -1

    def send(self, user=None):
        if user:
            s = '+'
            l = ''
            for key, value in self.data.items():
                if value == 1:
                    s += key
                elif isinstance(value, str):
                    l += str(value)

            if len(s) > 1:
                user.send('324 %s %s %s %s' % (user.nickname, self.channel.name, s, l))
        else:
            pass

class Channel(object):
    by_name = {}
    re_name = re.compile(r"^[&#+!][^\x00\x07\x0a\x0d ,:]{0,50}$")

    @staticmethod
    def by_id(name):
        return Channel.by_name.get(name.lower()) or False

    def __init__(self, name, creator=None, **kwargs):
        self.name = name
        self.id = name.lower()
        self.users = set()
        self.topic = ''

        self.by_name[self.id] = self
        self.created = int(time.time())
        self.modes = ChannelModes(self)

        
        if creator and self.modes.data['r'] == 0:
            self.modes.data['o'].append(creator)
            self.modes.data['v'].append(creator)
            self.modes.data['h'].append(creator)
            self.modes.data['q'].append(creator)
            self.modes.data['a'].append(creator)



    def change_topic(self, user, topic):
        if self.modes.allowed(user, 'o'):
            self.topic = topic
            self.write(':%s TOPIC %s :%s' % (user, self.name, self.topic))

    def can_send(self, user):
        if self.modes.data['n'] == 1:
            if user in self.users:
                return True
            else:
                return False

        return True

    def can_join(self, user):
        if self.modes.data['l'] > 0 and len(self.users) + 1 > self.modes.data['l']:
            user.send('441 %s %s :Cannot join channel (+l)' % (user.nickname, self.name))
            return False
        # check bans.
        #user.send('474 %s %s :Cannot join channel (+b)' % (user.nickname, self.name))
        return True

    def join(self, user):
        user.relatives |= self.users
        user.relatives.discard(user)

        self.users.add(user)

        self.write(':%s JOIN %s' % (user, self.name))

        for cuser in self.users:
            cuser.relatives.add(user)

        if len(self.users) == 1:
            if self.id in on_create_channel:
                for cb in on_create_channel[self.id]:
                    cb(self)

    def kick(self, source, user, r=''):
        user.relatives ^= self.users

        self.write(':%s KICK %s %s :%s' % (source, self.name, user.nickname, r))

        self.users.discard(user)

        for cuser in self.users:
            cuser.relatives.discard(user)

        if len(self.users) == 0:
            self.delete()

    def part(self, user):
        user.relatives ^= self.users

        self.write(':%s PART %s' % (user, self.name))

        self.users.discard(user)

        for cuser in self.users:
            cuser.relatives.discard(user)

        if len(self.users) == 0:
            self.delete()

    def write(self, message, ignore_me=False):
        users_copy = self.users.copy()
        for cuser in users_copy:
            if ignore_me != cuser:
                cuser.write(message)

    def __str__users__(self):
        userlist = ''
        for user in self.users:
            userlist += ' ' + self.modes.get_prefix(user) + user.nickname
        return userlist

    def __str__(self):
        return '%s' % self.name