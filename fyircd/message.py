# -*- coding: utf-8 -*-
"""
    fyircd.message
    ~~~~~~~~~~~~~~~~
    Parse IRC
    :license: BSD, see LICENSE for more details.
"""
import fyircd.raw as raw


class Message(object):
    def __init__(self, target, raw, params):
        self.raw = raw.lower()
        self.params = params
        self.target = target

        self.handle()

    #: check if a command is handle and then call the function after parsing parameters.
    #: don't forget IRC is a realy shitty protcol.
    def handle(self):
        if hasattr(raw, self.raw):
            if self.raw != 'user' and self.raw != 'nick':
                if self.target.is_ready():
                    getattr(raw, self.raw)(self.target, self.params)
            else:
                getattr(raw, self.raw)(self.target, self.params)

        else:
            raw._unknown(self.target, self.raw, self.params)

    #: parse a line
    @staticmethod
    def from_string(line):
        if len(line) <= 512:
            line = line.strip(' \t\n\r')

            x = line.split(' ', 1)
            command = x[0].upper()

            if len(x) == 1:
                args = []
            else:
                if ':' in x[1]:
                    y = x[1].split(':', 1)
                    args = y[0].strip(' ').split(' ')
                    if len(args) == 1 and len(args[0]) == 0:
                        args = []
                    args.append(y[1])
                else:
                    args = x[1].split(' ')

            return (command, args)