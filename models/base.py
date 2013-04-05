# -*- coding: utf-8 -*-
from models import Error

class BaseModel(object):
  objects = {}

  @classmethod
  def get(cls, key):
    if not cls.exists(key):
      return False
    return BaseModel.objects[cls][key]

  @classmethod
  def all(cls):
    if not cls in BaseModel.objects:
      BaseModel.objects[cls] = {}
    return BaseModel.objects[cls].values()

  @classmethod
  def exists(cls, key):
    return cls in BaseModel.objects and key in BaseModel.objects[cls]

  @classmethod
  def property_exists(cls, key, value):
    if cls in BaseModel.objects:
      for obj in BaseModel.objects[cls]:
        if cls.get(obj).__getattribute__(key) == value:
          return cls.get(obj)
    return False
    
  def save(self):
    if self.__class__.exists(self.get_key()) and self.__class__.get(self.get_key()) is not self:
      raise Error(self.__class__.__name__ + ' with key ' + str(self.get_key()) + ' already exists, not the saved object')
    if not self.__class__ in BaseModel.objects:
      BaseModel.objects[self.__class__] = {}
    BaseModel.objects[self.__class__][self.get_key()] = self

  def delete(self):
    del BaseModel.objects[self.__class__][self.get_key()]

  def set_key(self, new_key):
    if self.__class__.exists(new_key):
      raise Error(self.__class__.__name__ + ' with key ' + str(new_key) + ' already exists')
    if self.get_key == new_key:
      pass
    del BaseModel.objects[self.__class__][self.get_key()]
    old_key = self.get_key()
    self._set_key(new_key)
    if self.get_key() != new_key:
      raise 'subclass was expected to change key from ' + str(old_key) + ' to ' + str(new_key) + ', but key is now ' + str(self.get_key())
    self.save()

  def get_key(self):
    raise NotImplementedError

  def _set_key(self, new_key):
    raise NotImplementedError
