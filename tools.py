# -*- coding: utf-8 -*-
import logging, sys, string

def _lower(s):
  # https://github.com/jrosdahl/miniircd/blob/master/miniircd
  _alpha = "abcdefghijklmnopqrstuvwxyz"
  _ircstring_translation = string.maketrans(string.upper(_alpha) + "[]\\^", _alpha + "{}|~")

  return string.translate(s, _ircstring_translation)

def logs():
  logger  = logging.getLogger('FyIRCd')
  hl = logging.StreamHandler(sys.stdout)
  fm = logging.Formatter('[%(asctime)s] %(name)s (%(levelname)s): %(message)s')
  hl.setFormatter(fm)
  logger.addHandler(hl)

  logger.setLevel(logging.DEBUG)

  return logger

log = logs()
