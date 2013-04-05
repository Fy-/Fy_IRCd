# -*- coding: utf-8 -*-
from models import Client, User, Channel
import raw_error,raw_init,raw_utils
import config, time

"""
  Channel command
"""
def _unknown(target, raw, params):
  pass

def join(target, params):
  # Multiple join?
  if '#' not in params[0]:
    raw_error._403(target, params[0])
  else:
    if ',' in params[0]:
      for tmp in params[0].split(','):
        channel = raw_utils._create_channel(tmp)
        target.get_user().join(channel)
        names(target, [tmp])
    else:
      tmp = params[0]
      channel = raw_utils._create_channel(tmp)
      target.get_user().join(channel)
      names(target, [tmp])     

def part(target, params):
  if '#' not in params[0]:
    raw_error._403(target, params[0])
  else:
    if ',' in params[0]:
      for tmp in params[0].split(','):
        channel = raw_utils._create_channel(tmp)
        if channel:
          target.get_user().part(channel)
    else:
      tmp = params[0]
      channel = raw_utils._create_channel(tmp)
      if channel:
        target.get_user().part(channel)

def names(target, params):
  if Channel.get(params[0]) != False:
    channel = Channel.get(params[0])
    user_list = ''
    for user in channel.users:
      user_list += ' ' + user.nickname

    to_send = raw_utils._split_string_512(user_list)
    for message in to_send:
      target.send('353 %s = %s :%s' % (target.get_user().nickname, params[0], message.strip(' ')))
    target.send('366 %s %s :End of /NAMES list.' % (target.get_user().nickname, params[0]))

def privmsg(target, params):
  if len(params) == 1:
    raw_error._412(target)
  elif len(params) == 0:
    raw_error._411(target)
  else:
    if '#' in params[0]:
      if Channel.get(params[0]) != False:
        channel = Channel.get(params[0])
        for user in channel.users:
          if user != target.get_user():
            user.get_client().msg(':%s PRIVMSG %s :%s' % (target.get_user(), params[0], params[1]))
      else:
        raw_error._401(target, params[0])
    else:
      try:
        source = target.get_user()
        to     = User.by_nickname(params[0]).get_client()
        client = User.by_nickname(params[0]).get_client()
        client.msg(':%s PRIVMSG %s :%s' % (source, params[0], params[1]))
      except:
        raw_error._401(target, params[0])
"""
  User command
"""
def ison(target, params):
  user_list = ''

  for tmp_user in params:
    if User.by_nickname(tmp_user):
      user_list += ' %s' % User.by_nickname(tmp_user).nickname

  target.send('303 %s :%s' % (target.get_user().nickname, user_list.strip()))

def ping(target, params):
  target.send('PONG %s :%s' % (config.Server.name, params[0]))

def pong(target, params):
  pass

def quit(target, params):
  target.disconnect()
  target.save()

def user(target, params):
  user = raw_utils._create_user(target)

  if user.welcome:
    raw_error._462()
  else:
    user.hostname = target.address[0]
    user.realname = params[3]
    user.username = params[0]
    user.save()

    if user.nickname:
      raw_init._welcome(target)

def userhost(target, params):
  if len(params) == 0:
    raw_error._461(target, params[0])
  else:
    user = User.by_nickname(params[0])
    if user:
      target.send('302 %s :%s=%s' % (target.get_user().nickname, user.nickname, user))
    else:
      target.send('302 %s :' % (target.get_user().nickname))

def whois(target, params):
  if len(params) == 0:
    raw_error._461(target, params[0])
  else:
    user = User.by_nickname(params[0])
    if user:
      target.send('311 %s %s ~%s %s * :%s' % (target.get_user().nickname, user.nickname, user.username, user.hostname, user.realname))
      target.send('318 %s %s End of /WHOIS list.' % (target.get_user().nickname, user.nickname))
    else:
      raw_error._401(target, params[0])


def nick(target, params): 
  user = raw_utils._create_user(target)

  if User.by_nickname(params[0]) != False:
    raw_error._433(target, params[0])
  else:
    if user.welcome:
      user.send_all(':%s NICK :%s' % (user, params[0]))
      user.rename(params[0])
      user.save()
    else:
      user.rename(params[0])
      user.save()
      if user.hostname:
        raw_init._welcome(target)
