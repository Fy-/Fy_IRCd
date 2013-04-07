# -*- coding: utf-8 -*-
from models import User
from irc import Message
import tools, time, gevent

    
class Sockets(object):
  @staticmethod
  def is_alive(user):
    while 42:
      if user.status['dropped'] == True:
        user.disconnect()
        break

      try:
        user.is_alive()
      except:
        break
      
      gevent.sleep(10)

  @staticmethod
  def close(user):
    tools.log.info('Client disconnected %s' % client)

    if user:
      user.quit()
    try:
      user.socket['socket'].shutdown(socket.SHUT_WR) 
    except:
      tools.log.info('Client %s already disconnected' % client)

    user.socket['socket'].close()
    user.delete()

  @staticmethod
  def handle(socket, address):
    user = User(socket, address)
    user.save()

    tools.log.info('New client %s' % user)
    gevent.Greenlet.spawn(Sockets.is_alive, user)

    while 42:
      line = user.socket['file'].readline()

      if not line:
        break
      else:
        raw, params = Message.from_string(line)
        message = Message(user, raw=raw, params=params)
      
    Sockets.close(user)
