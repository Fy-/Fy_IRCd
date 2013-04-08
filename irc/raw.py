# -*- coding: utf-8 -*-
from models import User, Channel
from tools import _lower
from plugins.core import raw_callback

import raw_error, raw_init, raw_utils
import config, time

"""
  (RFC 1459) // To do 
"""
def admin(target, params):
  target.send('256 %s :Administrative info about %s' % (target.nickname, config.Server.name))
  target.send('257 %s :%s' % (target.nickname, config.Misc.informations[0]))
  target.send('258 %s :%s' % (target.nickname, config.Misc.informations[1]))
  target.send('259 %s :%s' % (target.nickname, config.Misc.informations[2]))

def away(target, params):
  try:
    target.away = params[0]
    target.send('306 %s :You have been marked as being away' % target.nickname)
  except:
    target.away = None
    target.send('305 %s :You are no longer marked as being away' % target.nickname)

  target.save()

"""
  Channel command
"""
def _unknown(target, raw, params):
  pass

def _join(target, chan):
  channel = raw_utils._create_channel(chan)
  if channel:
    target.join(channel)
    #target.send(channel.modes.get())
    names(target, [chan])
  else:
    raw_error._403(target, chan)

def _part(target, chan):
  channel = Channel.get(_lower(chan))
  if channel:
    target.part(channel)
  else:
    raw_error._403(target, chan)

def join(target, params):
  if '#' not in params[0]:
    raw_error._403(target, params[0])
  else:
    if ',' in params[0]:
      for tmp in params[0].split(','):
        _join(target, tmp)
    else:
      _join(target, params[0])

def part(target, params):
  if '#' not in params[0]:
    raw_error._403(target, params[0])
  else:
    if ',' in params[0]:
      for tmp in params[0].split(','):
        _part(target, tmp)
    else:
      _part(target, params[0])

def mode(target, params):
  if '#' in params[0]:
    channel = Channel.get(_lower(params[0]))
    if channel:
      target.send(channel.modes.get())
    else:
      raw_error._401(target, params[0])

def names(target, params):
  channel = Channel.get(_lower(params[0]))
  if channel:
    to_send = raw_utils._split_string_512(channel.userlist_str())
    for message in to_send:
      target.send('353 %s = %s :%s' % (target.nickname, params[0], message.strip(' ')))
    target.send('366 %s %s :End of /NAMES list.' % (target.nickname, params[0]))
  else:
    raw_error._401(target, params[0])

def notice(target, params):
  privmsg(target, params, 'NOTICE') 

def privmsg(target, params, cmd='PRIVMSG'):
  if len(params) == 1:
    raw_error._412(target)
  elif len(params) == 0:
    raw_error._411(target)
  else:
    if raw_callback.get(cmd):
      params = raw_callback[cmd](params)

    if '#' in params[0]:
      channel = Channel.get(_lower(params[0]))
      if channel:
        if channel.can_send(target):
          channel.write(':%s %s %s :%s' % (target, cmd, params[0], params[1]), ignore_me=target)
        else:
          raw_error._404(target, params[0])
      else:
        raw_error._401(target, params[0])
    else:
      try:
        user   = User.by_nickname(params[0])
        if user.away:
          target.send('301 %s %s :%s' % (target.nickname, user.nickname, user.away))
        user.write(':%s %s %s :%s' % (target, cmd, params[0], params[1]))
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

  target.send('303 %s :%s' % (target.nickname, user_list.strip()))

def ping(target, params):
  target.update_aliveness()
  target.send('PONG %s :%s' % (config.Server.name, params[0]))

def pong(target, params):
  target.update_aliveness()

def quit(target, params):
  try: target.status['quit_txt'] = params[1]
  except: target.status['quit_txt'] = '×̯×'
  target.save()
  target.disconnect(False)

def user(target, params):
  if len(params) != 4:
    target.disconnect('gtfo')
  else:
    if target.status['welcomed']:
      raw_error._462()
    else:
      target.realname = params[3]
      target.username = params[0]
      word_count, target.reverse = raw_utils._reverse(target.socket['IP'])
      target.hostname = raw_utils._hostname(word_count, target.reverse)
      target.save()

      if target.nickname:
        raw_init._welcome(target)

def userhost(target, params):
  if len(params) == 0:
    raw_error._461(target, params[0])
  else:
    user = User.by_nickname(params[0])
    if user:
      target.send('302 %s :%s=%s' % (target.nickname, user.nickname, user))
    else:
      target.send('302 %s :' % (target.nickname))

def whois(target, params):
  if len(params) == 0:
    raw_error._461(target, params[0])
  else:
    user = User.by_nickname(params[0])
    if user:
      target.send('311 %s %s ~%s %s * :%s' % (target.nickname, user.nickname, user.username, user.hostname, user.realname))
      target.send('318 %s %s End of /WHOIS list.' % (target.nickname, user.nickname))
    else:
      raw_error._401(target, params[0])

def nick(target, params): 
  if User.by_nickname(params[0]) != False and User.by_nickname(params[0]) != target:
    raw_error._433(target, params[0])
  elif not config.User.re_nick.match(params[0]):
    raw_error._432(target, params[0])
  else:
    if target.status['welcomed']:
      target.write_relatives(':%s NICK :%s' % (target, params[0]))
      target.rename(params[0])
      target.save()
    else:
      target.rename(params[0])
      target.save()
      if target.hostname:
        raw_init._welcome(target)
