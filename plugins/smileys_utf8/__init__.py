# -*- coding: utf-8 -*-
from plugins.core import add_raw_callback
from . import smiley

add_raw_callback('PRIVMSG', smiley.add)

def _on_load():
  return 'smileys_utf8 v0.1 by Fy- <m@fy.to>'