# -*- coding: utf-8 -*-
import raw, tools

class Message(object):
  def __init__(self, target, raw, params):
    self.raw      = raw.lower()
    self.params   = params
    self.target   = target

    self.handle()

  def handle(self):
    if hasattr(raw, self.raw):
      getattr(raw, self.raw)(self.target, self.params)
    else:
      raw._unknown(self.target, self.raw, self.params)

  @staticmethod
  def from_string(str):
    tools.log.debug(' <<< ' + str.replace('\n', ''))
    if len(str) > 512:
      raise Error('Max message size: 512 characters')

    raw  = str
    last = None

    if ':' in str:
      tmp  = str.split(':', 1)
      raw  = tmp[0]
      last = tmp[1]
    
    result = raw.split(' ')
    if last is not None: 
      result.append(last)

    tmp = result[0]
    del result[0]

    # redo c'est moche.
    new_result = []
    for r in result:
      r = r.replace("\n", '')
      r = r.replace("\r", '')
      if r != '':
        new_result.append(r)

    return (tmp, new_result)