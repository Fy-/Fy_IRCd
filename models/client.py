# -*- coding: utf-8 -*-
from models import BaseModel, Error
from gevent import socket 
import config, gevent, tools, time

class Client(BaseModel):
  def __init__(self, socket, address, **kwargs):
    self.socket       = socket
    self.address      = address
    self.socket_file  = socket.makefile('rw')
    self._user        = None
    self.dropped      = False

    self.sent_ping    = False
    self.timestamp    = None

  def update_aliveness(self, timestamp):
    if int(timestamp) == int(self.timestamp):
      self.timestamp = int(time.time())
      self.sent_ping = False

    self.save()

  def check_aliveness(self):
    now = int(time.time())
    
    if self.timestamp:
      if self.timestamp + 180 < now:
        self.disconnect()

      if self.timestamp + 5 < now:
        if self.sent_ping == False:
          self.msg('PING :%s' % self.timestamp)
          self.sent_ping = True 

    else:
      self.timestamp = now
      self.sent_ping = True
      self.msg('PING :%s' % now)
    self.save()

  def write(self, to_send):
    tools.log.debug(' >>> ' + to_send)
    try:
      self.socket_file.write(to_send+'\r\n')
      self.socket_file.flush()
    except:
      self.dropped = True

  def msg(self, msg):
    self.write(msg)

  def send(self, message):
    self.write(':%s %s' % (config.Server.name, message))

  def set_user(self, user):
    self._user = user
    self.save()
    self._user.save()

  def get_user(self):
    return self._user

  def get_key(self):
    return self.socket

  def disconnect(self):
    self.socket.shutdown(socket.SHUT_WR) 

  def __iter__(self):
    return iter([self])

  @staticmethod
  def by_socket(socket, address):
    return Client.get(socket)