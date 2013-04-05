# -*- coding: utf-8 -*-
from models import User, Channel
import config, time

def _welcome(target):
  user   = target.get_user()

  if not user.welcome:
    target.send('001 %s :Welcome to %s %s' % (user.nickname, config.Server.name, user.nickname))
    target.send('002 %s :Your host is "%s", running version %s-%s' % (user.nickname, config.Server.name, config.Server.name, config.Server.vers))
    target.send('005 %s :%s NICKLEN=32 CHANNELLEN=50 TOPICLEN=390 :are supported by this server' % (user.nickname, user.nickname))
    target.send('251 %s :%s :There is %s users on %s' % (user.nickname, user.nickname, len(User.all()), config.Server.name))
    target.send('254 %s :%s :There is %s channels on %s' % (user.nickname, user.nickname, len(Channel.all()), config.Server.name))

    _send_motd(target, user)

    target.msg('PING :%s' % config.Server.name)

    user.welcome  = True
    user.save()

def _send_motd(target, user):
  target.send('375 %s :- %s, message of the day -' % (user.nickname, config.Server.name))

  for line in config.Server.motd:
    target.send('372 %s :-     %s' % (user.nickname, line.replace("\n", "")))
  
  target.send('376 %s :End of /MOTD command' % user.nickname)