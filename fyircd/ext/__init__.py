# -*- coding: utf-8 -*-
"""
	fyircd.ext
	~~~~~~~~~~~~~~~~
	This is mostly temporary, I need to add more callbacks.
	:license: BSD, see LICENSE for more details.
"""
import logging, importlib

logger = logging.getLogger('fyircd')
fake_users = []
user_privmsg_callback = {}
chan_privmsg_callback = {}
when_server_ready = []
on_join_channel = {}
on_create_channel = {}


def load_ext(name):
    mod = importlib.import_module("fyircd.ext.%s" % name)
    try:
        mod = importlib.import_module("fyircd.ext.%s" % name)
        logger.info('[ext] Loading: ' + mod._on_load())
    except:
        logger.error('Can not import "fyircd.ext.%s"' % name)


def add_fake_user(data):
    fake_users.append(data)


def on_server_ready(cb):
    when_server_ready.append(cb)


def on_join(channel, cb):
    if channel not in on_join_channel:
        on_join_channel = []
    on_join_channel.append(cb)


def on_create_chan(channel, cb):
    if channel not in on_create_channel:
        on_create_channel[channel] = []
    on_create_channel[channel].append(cb)


def add_user_privmsg_callback(name, cb):
    if name not in user_privmsg_callback:
        user_privmsg_callback[name] = []
    user_privmsg_callback[name].append(cb)


def add_chan_privmsg_callback(name, cb):
    if name not in chan_privmsg_callback:
        chan_privmsg_callback[name] = []

    chan_privmsg_callback[name].append(cb)