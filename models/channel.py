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
    return mode in self.current

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
    self.users = set()
    self.modes = ChannelMode(self)

  def can_send(self, user):
    if self.modes.has('n'):
      if user in self.users:
        return True
      else:
        return False

    return True

  def join(self, user):
    self.users.add(user)
    self.save()

    user.relatives |= self.users
    user.save()

    self.write(':%s JOIN %s' % (user, self.name))

    for cuser in self.users:
      cuser.relatives.add(user)
      cuser.save()

  def part(self, user):
    user.relatives ^= self.users
    user.save()

    self.write(':%s PART %s' % (user, self.name))

    self.users.discard(user)
    self.save()
    
    for cuser in self.users:
      cuser.relatives.discard(user)
      cuser.save()

    if len(self.users) == 0:
      self.delete()

  def write(self, message, ignore_me=False):
    for cuser in self.users:
      if ignore_me != cuser:
        cuser.write(message)

  def userlist_str(self):
    userlist = ''
    for user in self.users:
      userlist += ' ' + user.nickname
    return userlist
    
  def get_key(self):
    return _lower(self.id)

  def _set_key(self, new_key):
    self.id = _lower(new_key)

  def __str__(self):
    return '%s' % self.name