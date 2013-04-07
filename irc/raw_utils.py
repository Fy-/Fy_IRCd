# -*- coding: utf-8 -*-
from models import User, Channel
from tools import _lower
from libs.markov import construct_sentence
from gevent.dns import resolve_reverse
from socket import inet_aton
import config, socket

def _reverse(ip):
  packed_ip = inet_aton(ip)
  try:
    return (3, resolve_reverse(packed_ip)[1])
  except:
    return (4, '0.0.FyIRCd.com')

def _hostname(word_count, reverse):
  if User.ip_to_reverse.get(reverse):
    return User.ip_to_reverse[reverse]

  result   = reverse.strip('.').split('.', 2)
  sentence = construct_sentence(word_count=word_count, slug=True)

  User.ip_to_reverse[reverse] = sentence + '.' + result[2]
  return User.ip_to_reverse[reverse]

def _create_channel(name):
  if not config.Channel.re_name.match(name):
    return False

  if Channel.get(_lower(name)) == False:
    channel = Channel(name)
    channel.modes.add('n')
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