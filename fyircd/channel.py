# -*- coding: utf-8 -*-
import time, logging
import regex as re

from fyircd.user import User

class Channel(object):
    by_name = {}
    re_name = re.compile(r"^[&#+!][^\x00\x07\x0a\x0d ,:]{0,50}$")

    mode_to_symbol = {'o': '@', 'v': '+', 'h': '%', 'q': '~', 'a': '&'}

    supported_modes = {
        # https://github.com/LukeB42/psyrcd/blob/master/psyrcd.py - Uppercase modes can only be set and removed by opers.
        'A': "Server administrators only.",
        #               'i':"Invite only.",
        'm': "Muted.",
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

    def __init__(self, name, creator=None, **kwargs):
        self.name = name
        self.id = name.lower()
        self.users = set()
        self.topic = ''
        self.modes = {
            'n': 1,
            't': 1,
            'l': 0,
            'm': 0,
            'v': [],
            'h': [],
            'o': [],
            'q': [],
            'a': [],
            'b': [],
            'e': []
        }

        self.by_name[self.id] = self
        self.created = int(time.time())

        if creator:
            self.modes['o'].append(creator)
            self.modes['v'].append(creator)
            self.modes['h'].append(creator)
            self.modes['q'].append(creator)
            self.modes['a'].append(creator)

    @staticmethod
    def concat_modes():
        return ''.join(Channel.supported_modes.keys())

    def get_prefix_user(self, user, add=''):
        if user in self.modes['q']:
            return add + Channel.mode_to_symbol['q']
        if user in self.modes['a']:
            return add + Channel.mode_to_symbol['a']
        if user in self.modes['o']:
            return add + Channel.mode_to_symbol['o']
        if user in self.modes['h']:
            return add + Channel.mode_to_symbol['h']
        if user in self.modes['v']:
            return add + Channel.mode_to_symbol['v']
        return ''

    def allow_to_change_mode(self, user, mode):
        if user.oper:
            return True

        if mode == 'q' and (user in self.modes['q']):
            return True
        if mode == 'a' and (user in self.modes['q'] or user in self.modes['a']):
            return True
        if mode == 'o' and (user in self.modes['q'] or user in self.modes['a']  or user in self.modes['o']):
            return True
        if mode == 'h' and (user in self.modes['q'] or user in self.modes['a']  or user in self.modes['o']):
            return True
        if mode == 'v' and (user in self.modes['q'] or user in self.modes['a']  or user in self.modes['o']   or user in self.modes['h']):
            return True

        return False

    def add_modes(self, user, params):

        data = list(params[1])
        add = False
        if data[0] == '+':
            add = True


        for i in range(1, len(data)):
            if data[i] in ['m', 'n', 's', 't', 'l']:
                target = params[2]

                if user.oper == False or (
                    user not in self.modes['o'] and user not in self.modes['q'] and
                    user not in self.modes['a']
                ):
                    return -1  # not allowed
                if self.modes[data[i]] == 0:
                    if data[i] == 'l':
                        if len(params) == 4 and add:
                            self.modes['l'] = int(params[3])
                            self.write(':%s MODE %s %s%s %s' % (user, self.name, data[0], data[i], params[3]))
                        elif add == False:
                            self.modes['l'] = 0
                            self.write(':%s MODE %s %s%s %s' % (user, self.name, data[0], data[i],''))
                    else:
                        self.modes[data[i]] = 1 if add else 0
                        self.write(':%s MODE %s %s%s %s' % (user, self.name, data[0], data[i],''))

            if data[i] in ['o', 'v', 'h', 'q', 'a']:
                target = User.by_nickname(params[2])

                if self.allow_to_change_mode(user, data[i]):
                    if add:
                        if target not in self.modes[data[i]]:
                            self.modes[data[i]].append(target)
                            self.write(':%s MODE %s %s%s %s' % (user, self.name, data[0], data[i], target.nickname))
                    else:
                        if target in self.modes[data[i]]:
                            self.modes[data[i]].remove(target)
                            self.write(':%s MODE %s %s%s %s' % (user, self.name, data[0], data[i], target.nickname))
                else:
                    return -1



    def send_modes(self, user=None):
        if user:
            s = '+'
            l = ''
            for key, value in self.modes.items():
                if value == 1:
                    s += key
                elif isinstance(value, str):
                    l += str(value)

            if len(s) > 1:
                user.send('324 %s %s %s %s' % (user.nickname, self.name, s, l))


    @staticmethod
    def by_id(name):
        return Channel.by_name.get(name.lower()) or False

    def can_send(self, user):
        if self.modes['n'] == 1:
            if user in self.users:
                return True
            else:
                return False

        return True

    def can_join(self, user):
        if self.modes['l'] > 0 and len(self.users) + 1 > self.modes['l']:
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

    def part(self, user):
        user.relatives ^= self.users

        self.write(':%s PART %s' % (user, self.name))

        self.users.discard(user)

        for cuser in self.users:
            cuser.relatives.discard(user)

        if len(self.users) == 0:
            self.delete()

    def write(self, message, ignore_me=False):
        for cuser in self.users:
            if ignore_me != cuser:
                cuser._write(message)

    def __str__users__(self):
        userlist = ''
        for user in self.users:
            userlist += ' ' + self.get_prefix_user(user) + user.nickname
        return userlist

    def __str__(self):
        return '%s' % self.name