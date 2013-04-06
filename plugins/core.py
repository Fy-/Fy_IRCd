# -*- coding: utf-8 -*-
import tools, importlib

raw_callback = {}

def load_plugin(name):
  importlib.import_module("plugins.%s" % name)
  try:
    mod = importlib.import_module("plugins.%s" % name)
    tools.log.info('[Plugin] Loading: ' + mod._on_load())
  except:
    tools.log.error('Can not import "plugins.%s"' % name)

def add_raw_callback(raw, cb):
  raw_callback[raw] = cb