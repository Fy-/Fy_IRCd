# -*- coding: utf-8 -*-
import logging, sys

def logs():
  logger  = logging.getLogger('FyIRCd')
  hl = logging.StreamHandler(sys.stdout)
  fm = logging.Formatter('[%(asctime)s] %(name)s (%(levelname)s): %(message)s')
  hl.setFormatter(fm)
  logger.addHandler(hl)

  logger.setLevel(logging.DEBUG)

  return logger

log = logs()