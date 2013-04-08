# -*- coding: utf-8 -*-
from models import User, Channel
from tools import _lower
from plugins.core import raw_callback

import raw_error, raw_init, raw_utils
import config, time

"""
  (RFC 1459) 
  // To do

lusers
  :verne.freenode.net 251 zaeeaaez :There are 183 users and 73909 invisible on 31 servers
  :verne.freenode.net 252 zaeeaaez 34 :IRC Operators online
  :verne.freenode.net 253 zaeeaaez 3 :unknown connection(s)
  :verne.freenode.net 254 zaeeaaez 45734 :channels formed
  :verne.freenode.net 255 zaeeaaez :I have 3907 clients and 1 servers
  :verne.freenode.net 265 zaeeaaez 3907 6745 :Current local users 3907, max 6745
  :verne.freenode.net 266 zaeeaaez 74092 88716 :Current global users 74092, max 88716
  :verne.freenode.net 250 zaeeaaez :Highest connection count: 6746 (6745 clients) (1091004 connections received)

info
  :verne.freenode.net 371 zaeeaaez :IRC --
  :verne.freenode.net 371 zaeeaaez :Based on the original code written by Jarkko Oikarinen
  :verne.freenode.net 371 zaeeaaez :Copyright 1988, 1989, 1990, 1991 University of Oulu, Computing Center
  :verne.freenode.net 374 zaeeaaez :End of /INFO list.

namex
  names with @,+,etc...

uhnames
  names but str_user

time
:verne.freenode.net 391 zaeeaaez verne.freenode.net :Sunday April 7 2013 -- 20:36:15 -04:00

stats, version

"""

"""
  IRC Operator
"""
def kill(target, params):
  if len(params) == 0:
    raw_error._461(target, 'KILL')
  else:
    if target.modes.has('O'):
      try:
        if len(params) == 1: reason = 'no reason'
        else: reason = params[1]

        user = User.by_nickname(params[0])
        user.status['quit_txt']  = '☠ /kill by %s (%s)' % (target.nickname, reason)
        user.status['kill_form'] = target
        user.save()
        user.disconnect()
      except:
        raw_error._401(target, params[0])
    else:
      raw_error._481(target)

def oper(target, params):
  try:
    if params[1] == config.User.opers[params[0]]:
      target.oper = True
      
      target.write(':%s %s' %(target, target.modes.add('OW')))
      target.send('381 %s :You are now an IRC Operator' % target.nickname)
      target.send('381 %s :With great power comes great responsibility' % target.nickname)
  except:
    target.send('464 %s :Nice try ❤')

"""
  Server command
"""
def users(target, params):
  #todo max :target.send('265 %s %s %s :Current local users %s, max %s')
  target.send('265 %s %s :Current local users %s' % (target.nickname, len(User.all()), len(User.all())))

def motd(target, params):
  raw_init._send_motd(target)

def admin(target, params):
  target.send('256 %s :Administrative info about %s' % (target.nickname, config.Server.name))
  target.send('257 %s :%s' % (target.nickname, config.Misc.admins[0]))
  target.send('258 %s :%s' % (target.nickname, config.Misc.admins[1]))
  target.send('259 %s :%s' % (target.nickname, config.Misc.admins[2]))

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
    raw_error._461(target, 'USERHOST')
  else:
    user = User.by_nickname(params[0])
    if user:
      target.send('302 %s :%s=%s' % (target.nickname, user.nickname, user))
    else:
      target.send('302 %s :' % (target.nickname))

def away(target, params):
  try:
    target.away = params[0]
    target.send('306 %s :You have been marked as being away' % target.nickname)
  except:
    target.away = None
    target.send('305 %s :You are no longer marked as being away' % target.nickname)

  target.save()

def whois(target, params):
  if len(params) == 0:
    raw_error._461(target, 'WHOIS')
  else:
    user = User.by_nickname(params[0])
    if user:
      target.send('311 %s %s %s %s * :%s' % 
        (target.nickname, user.nickname, user.username, user.hostname, user.realname))


      if len(user.channels) != 0:
        target.send('319 %s %s :%s' % 
          (target.nickname, user.nickname, ' '.join([str(channel) for channel in user.channels])))

      if user.modes.has('O'):
        target.send('313 %s %s :✩✩✩ IRC operator, show some respect! ✩✩✩' %
          (target.nickname, user.nickname))

      target.send('317 %s %s %s %s :seconds idle, signon time' % 
        (target.nickname, user.nickname, (int(time.time())-user.idle), user.created))

      target.send('312 %s %s %s :%s' % 
        (target.nickname, user.nickname, config.Server.name, config.Server.name))
      
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
