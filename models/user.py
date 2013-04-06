# -*- coding: utf-8 -*-
from models import BaseModel, Error
from models import Client
from tools import _lower

class User(BaseModel):
  nickname_to_user = {}

  def __init__(self, chash, socket):
    self.chash    = chash
    self.channels = []

    self._socket  = socket
    self.nickname = None
    self.ip       = None
    self.reverse  = None
    self.hostname = None
    self.username = None
    self.realname = None
    self.welcome  = False

    self.mode = UserMode()
    self.away = False

  @staticmethod
  def _update_nickname_to_user(old, new, hash):
    try:
      del User.nickname_to_user[_lower(old)]
    except:
      pass
      
    User.nickname_to_user[_lower(new)] = hash

  @staticmethod
  def by_nickname(nickname):
    try:
      return User.get(User.nickname_to_user[_lower(nickname)])
    except:
      return False

  def send_all(self, raw):
    if len(self.channels) == 0:
      self.get_client().msg(raw)
    else:
      for channel in self.channels:
        channel.send(raw)

  def get_client(self):
    return Client.get(self._socket)

  def get_key(self):
    return self.chash

  def rename(self, new_name):
    User._update_nickname_to_user(self.nickname, new_name, self.get_key())
    self.nickname = new_name
    self.save()

  def join(self, channel):
    if channel not in self.channels:
      self.channels.append(channel)
      channel.join(self)

  def part(self, channel):
    if channel in self.channels:
      self.channels.remove(channel)
      channel.part(self)

  def quit(self):
    del User.nickname_to_user[_lower(self.nickname)]

    for channel in self.channels:
      channel.part(self)

    self.delete()

  def _set_key(self, new_key):
    self.chash = new_key

  def __str__(self):
    return '%s!%s@%s' % (self.nickname, self.username, self.hostname)

class UserMode(object):
  a = False # away
  i = False # invisible
  w = False # wallops
  r = False # restricted
  O = False # operator
  o = False # local operator
  n = False # notices