# -*- coding: utf-8 -*-
from models import User, Channel
import config, time

def _welcome(target):
  if not target.status['welcomed']:
    target.send('001 %s :Welcome to %s %s' % (target.nickname, config.Server.name, target.nickname))
    target.send('002 %s :Your host is "%s", running version %s-%s' % (target.nickname, config.Server.name, config.Server.name, config.Server.vers))
    target.send('005 %s :%s NICKLEN=50 CHANNELLEN=50 TOPICLEN=390 :are supported by this server' % (target.nickname, target.nickname))
    target.send('251 %s :%s :There is %s users on %s' % (target.nickname, target.nickname, len(User.all()), config.Server.name))
    target.send('254 %s :%s :There is %s channels on %s' % (target.nickname, target.nickname, len(Channel.all()), config.Server.name))

    _send_motd(target)

    target.status['welcomed'] = True
    target.save()

def _send_motd(target):
  target.send('375 %s :- %s, message of the day -' % (target.nickname, config.Server.name))

  for line in config.Server.motd:
    target.send('372 %s :-     %s' % (target.nickname, line.replace("\n", "")))
  
  target.send('376 %s :End of /MOTD command' % target.nickname)