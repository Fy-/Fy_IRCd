# -*- coding: utf-8 -*-
from models import User
from irc import Message
import tools, time, gevent

    
class Sockets(object):
  @staticmethod
  def is_alive(socket):
    while User.get(socket):
      try: User.get(socket).is_alive()
      except: break
      
      gevent.sleep(10)

  @staticmethod
  def close(socket):
    tools.log.info('Client disconnected: %s' % User.get(socket))

    User.get(socket).quit()
    User.get(socket).delete()

    socket.close()

  @staticmethod
  def handle(socket, address):
    user = User(socket, address)
    user.save()

    tools.log.info('New client: %s' % user)
    gevent.Greenlet.spawn(Sockets.is_alive, socket)

    while True:
      user = User.get(socket)
      user.idle = int(time.time())
      user.save()
      print int(time.time()), user.idle
      try: line = user.socket['file'].readline()
      except: break
      
      if not line:
        break
      else:
        raw, params = Message.from_string(line)
        message = Message(user, raw=raw, params=params)

    Sockets.close(socket)