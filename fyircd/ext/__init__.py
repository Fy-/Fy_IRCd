# -*- coding: utf-8 -*-
import logging, importlib

logger = logging.getLogger('fyircd')
raw_callback = {}


def load_plugin(name):
    importlib.import_module("plugins.%s" % name)
    try:
        mod = importlib.import_module("ext.%s" % name)
        logger.info('[ext] Loading: ' + mod._on_load())
    except:
        logger.error('Can not import "ext.%s"' % name)


def add_raw_callback(raw, cb):
    raw_callback[raw] = cb
