# -*- coding: utf-8 -*-
import re, datetime

class Misc(object):
  debug   = True
  
  created = datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p")

  admins  = [
    'Server de test de FyIRd.com',
    'https://github.com/Fy-/FyIRCd',
    'm@fy.to'
  ]

class Channel(object):
  # Allowed in channel names
  re_name = re.compile(r"^[&#+!][^\x00\x07\x0a\x0d ,:]{0,50}$")

class User(object):
  # Allowed in nicks
  re_nick = re.compile(r"^[][\`_^{|}A-Za-z][][\`_^{|}A-Za-z0-9]{0,50}$")

  # IRC Administrators
  opers   = {
    'fy'  : 'operpwd',
    'para': 'parapwd'
  }

class Server(object):
  port   = 6667
  #ip     = '178.32.42.40'
  ip     = '0.0.0.0'
  name   = 'FyIRCd.com'
  vers   = '0.1-dev'
  motd   = None

class Security(object):
  secret = '\xfd\x8d\x15\xd3\x805\xf9M\xaf\xc0\x89@\xb2\xa6\xad\xcf9\x9e`#\x80\x8f\xf2\xa2'
  
with open('./var/motd.txt') as f:
  Server.motd = f.readlines()
