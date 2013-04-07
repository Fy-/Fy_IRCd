# -*- coding: utf-8 -*-
def _331(target, attr):
  target.send('331 %s %s :No topic is set' % (target, attr))

def _401(target, attr):
  target.send('401 %s %s :No such nick/channel' % (target.nickname, attr))

def _403(target, attr):
  target.send('403 %s %s :No such nick/channel' % (target.nickname, attr))

def _404(target, attr):
  target.send('404 %s %s :Cannot send to channel' % (target.nickname, attr)) 

def _411(target):
  target.send('411 %s :No recipient given' % (target.nickname))

def _412(target):
  target.send('412 %s :No text to send' % target.nickname)

def _431(target):
  target.send('431 :No nickname given')

def _432(target, attr):
  target.send('432 * %s :Erroneous nickname' % attr)

def _433(target, attr):
  target.send('433 * %s :Nickname is already in use.' % attr)

def _442(target, attr):
  target.send('442 %s :You\'re not on that channel' % attr)

def _462(target):
  target.send('462 You may not reregister')

def _461(target, attr):
  nickname = target.nickname or '*'
  target.send('461 %s %s :Not enough parameters' % (nickname, attr))