# -*- coding: utf-8 -*-
from models import Client
from irc import Message
from gevent import socket 
import tools

class Sockets(object):
  @staticmethod
  def close(client):
    tools.log.info('Client disconnected %s' % client)

    if client.get_user():
     client.get_user().quit()
    try:
      client.socket.shutdown(socket.SHUT_WR) 
    except:
      tools.log.info('Client %s already disconnected' % client)
    client.socket.close()
    client.delete()
    client.save()

  @staticmethod
  def handle(socket, address):
    client = Client(socket, address)
    client.save()

    sfile  = socket.makefile('rw')
    tools.log.info('New client %s' % Client.by_socket(socket, address))

    while True:
      line = sfile.readline()

      if not line:
        break
      else:
        raw, params = Message.from_string(line)
        message = Message(Client.by_socket(socket, address), raw=raw, params=params)
    
    Sockets.close(Client.by_socket(socket, address))
