# -*- coding: utf-8 -*-
import re

class Misc(object):
  debug  = True

class Channel(object):
  re_name = re.compile(r"^[&#+!][^\x00\x07\x0a\x0d ,:]{0,50}$")

class User(object):
  re_nick = re.compile(r"^[][\`_^{|}A-Za-z][][\`_^{|}A-Za-z0-9]{0,50}$")

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
  
