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
    return resolve_reverse(packed_ip)[1]
  except:
    return ip

def _hostname(reverse):
  reverse = reverse.strip('.')
  tmp = reverse.split('.', 2)
  return construct_sentence(word_count=4, slug=True) + '.' + tmp[2]

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