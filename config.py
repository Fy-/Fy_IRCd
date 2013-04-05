# -*- coding: utf-8 -*-
class Misc(object):
  debug  = True

class Server(object):
  port   = 8002
  ip     = '0.0.0.0'
  name   = 'FyIRCd.com'
  vers   = '0.1a'
  motd   = None

with open('./var/motd.txt') as f:
  Server.motd = f.readlines()

class Security(object):
  secret = '\xfd\x8d\x15\xd3\x805\xf9M\xaf\xc0\x89@\xb2\xa6\xad\xcf9\x9e`#\x80\x8f\xf2\xa2'
  
