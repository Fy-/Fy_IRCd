# -*- coding: utf-8 -*-
from models import BaseModel, Error
from tools import _lower

class Channel(BaseModel):
  def __init__(self, name, **kwargs):
    self.name  = name
    self.users = []

  def send(self, raw):
    for cuser in self.users:
      cuser.get_client().msg(raw)

  def join(self, user):
    self.users.append(user)
    self.save()

    for cuser in self.users:
      cuser.get_client().msg(':%s JOIN %s' % (user, self.name))

  def part(self, user):
    self.users.remove(user)
    self.save()

    for cuser in self.users:
      cuser.get_client().msg(':%s PART %s' % (user, self.name))

  def get_key(self):
    return _lower(self.name)

  def _set_key(self, new_key):
    self.name = new_key

  def __str__(self):
    return '%s' % self.name

class ChannelMode(object):
  n = False
  t = False