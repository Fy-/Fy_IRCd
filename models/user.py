# -*- coding: utf-8 -*-
from gevent import socket 
from models import BaseModel, Error
from tools import _lower

import config, gevent, tools, time

class User(BaseModel):
  nickname_to_user = {}
  ip_to_reverse    = {}

  def __init__(self, socket, address):
    self.socket = {
      'socket' : socket,
      'file'   : socket.makefile(),
      'IP'     : address[0]
    }

    self.status  =  {
      'sent_ping'   : False,
      'last_ping'   : False,
      'welcomed'    : False,
      'quit_txt'    : ''
    }

    self.channels   = set()
    self.relatives  = set()
    self.nickname   = None
    self.reverse    = None
    self.username   = None
    self.realname   = None
    self.hostname   = None

  def rename(self, new_name):
    User._update_nickname_to_user(self.nickname, new_name, self.get_key())
    self.nickname = new_name
    self.save()

  def join(self, channel):
    self.channels.add(channel)
    channel.join(self)

  def part(self, channel):
    self.channels.discard(channel)
    channel.part(self)

  def quit(self):
    self.write_relatives(':%s QUIT :%s' % (self, self.status['quit_txt']), True) 

    for channel in self.channels:
      channel.users.discard(self)
      channel.save()

    for cuser in self.relatives:
      if cuser != self:
        cuser.relatives.discard(self)
        cuser.save()

    if self.nickname:
      del User.nickname_to_user[_lower(self.nickname)]

  def update_aliveness(self):
    self.status['last_ping'] = int(time.time())
    self.status['sent_ping'] = False
    self.save()

  def is_alive(self):
    now = int(time.time())

    if self.status['last_ping']:
      if (self.status['last_ping'] + 30) < now:
        self.status['quit_txt'] = 'Ping timeout: %s seconds' % (now - self.status['last_ping'])
        self.save()
        self.disconnect(self.status['quit_txt'])
      if (self.status['last_ping'] + 15) < now:
        if not self.status['sent_ping']:
          self.write('PING :%s' % self.status['last_ping'])
          self.status['sent_ping'] = True 
          self.save()        
    else:
      self.status['last_ping'] = now
      self.status['sent_ping'] = True
      self.write('PING :%s' % self.status['last_ping'])
      self.save()

  def write(self, data):
    self._write(data)

  def send(self, data):
    self._write(':%s %s' % (config.Server.name, data))

  def write_relatives(self, data, ignore_me=False):
    for relative in self.relatives:
      relative.write(data)

    if not ignore_me:
      self.write(data)

  def send_relatives(self, data, ignore_me=False):
    for relative in self.relatives:
      relative.send(data)

    if not ignore_me:
      self.send(data)

  def disconnect(self, error=False):
    self.write('ERROR: ❤ %s ❤' % (self.status['quit_txt'] or error))
    try :self.socket['socket'].shutdown(gevent.socket.SHUT_WR)
    except: pass

  def get_key(self):
    return self.socket['socket']

  @staticmethod
  def by_nickname(nickname):
    try:
      return User.get(User.nickname_to_user[_lower(nickname)])
    except:
      return False

  def _set_key(self, socket):
    self.socket['socket'] = socket
    self.socket['file']   = socket.makefile('rw')

  def _write(self, data):
    tools.log.debug('%s >>> %s' % (self, data))
    try:
      self.socket['file'].write('%s\r\n' % data)
      self.socket['file'].flush()
    except:
      pass

  @staticmethod
  def _update_nickname_to_user(old, new, socket):
    if old:
      del User.nickname_to_user[_lower(old)]
    User.nickname_to_user[_lower(new)] = socket

  def __str__(self):
    if self.nickname:
      return '%s!%s@%s' % (self.nickname, self.username, self.hostname)
    else: 
      return self.socket['IP']

  def __iter__(self):
    return iter([self])