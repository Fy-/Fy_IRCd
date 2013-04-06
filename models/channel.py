# -*- coding: utf-8 -*-
from models import BaseModel, Error
from tools import _lower
import config

class ChannelMode(object):
  modes     = 'nt'
  allow_var = 't'

  def __init__(self, channel):
    self.channel = channel
    self.current = []
    self.var     = {}

  def has(self, mode):
    return mode in current

  def add(self, mode, var=None):
    if mode in ChannelMode.modes:
      self.current.append(mode)
      return 'MODE %s +%s' % (self.channel.name, mode)

  def get(self):
    modes = ''
    for mode in self.current:
      modes += mode

    if modes:
      return 'MODE %s +%s' % (self.channel.name, mode)
    return False
      

class Channel(BaseModel):
  def __init__(self, name, **kwargs):
    self.name  = name
    self.id    = _lower(name)
    self.users = []
    self.modes = ChannelMode(self)

  def send(self, message):
    self.msg(':%s %s' % (config.Server.name, message))

  def msg(self, message):
    for cuser in self.users:
      cuser.get_client().msg(message)

  def userlist_str(self):
    userlist = ''
    for user in self.users:
      userlist += ' ' + user.nickname
    return userlist

  def join(self, user):
    self.users.append(user)
    self.save()

    for cuser in self.users:
      cuser.get_client().msg(':%s JOIN %s' % (user, self.name))

  def part(self, user):
    for cuser in self.users:
      cuser.get_client().msg(':%s PART %s' % (user, self.name))

    self.users.remove(user)
    self.save()

    if len(self.users) == 0:
      self.delete()

  def get_key(self):
    return _lower(self.id)

  def _set_key(self, new_key):
    self.id = _lower(new_key)

  def __str__(self):
    return '%s' % self.name