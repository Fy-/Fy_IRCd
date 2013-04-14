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
      
      gevent.sleep(5)

  @staticmethod
  def close(socket):
    tools.log.debug('Client disconnected: %s' % User.get(socket))

    User.get(socket).quit()
    
    try: socket.close()
    except: pass

  @staticmethod
  def handle(socket, address):
    user = User(socket, address)
    user.save()

    tools.log.debug('New client: %s' % user)
    gevent.Greenlet.spawn(Sockets.is_alive, socket)

    while True:
      user = User.get(socket)

      try: line = user.socket['file'].readline()
      except: break
      
      if not line or user.status['shutdown'] == True:
        break
      else:
        user.update_idle(line)
        raw, params = Message.from_string(line)
        message = Message(user, raw=raw, params=params)

    Sockets.close(socket)