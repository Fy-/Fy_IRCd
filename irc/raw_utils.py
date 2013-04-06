# -*- coding: utf-8 -*-
from models import User, Channel
from tools import _lower
from libs.markov import construct_sentence
import hashlib, config, gevent, socket

def _reverse(ip):
  packed_ip = socket.inet_aton(ip)
  try:
    return gevent.dns.resolve_reverse(packed_ip)
  except:
    return ip

def _hostname(reverse):
  reverse = reverse.strip('.')
  tmp = reverse.split('.', 2)

  print tmp
  return construct_sentence(slug=True) + '.' + tmp[2]

def _create_user(target):
  chash = hashlib.sha224(str(target.socket_file)).hexdigest() 
  if target.get_user() == None:
    user = User(chash, target.socket)
    target.set_user(user)
    user.save()

  user = target.get_user()
  return user

def _create_channel(name):
  if not config.Channel.re_name.match(name):
    return False

  if Channel.get(_lower(name)) == False:
    channel = Channel(name)
    channel.save()
    return channel
  else:
    return Channel.get(_lower(name))

def _split_string_512(str):
  i = 0
  tmp = str.split(' ')
  result    = []
  result.append('')

  for word in tmp:
    if (len(result[i] + word) > 512):
      result[i] = result[i].strip()
      i += 1
      result.append('')

    result[i] += word+ ' '

  return result 