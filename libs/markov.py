# -*- coding:utf-8 -*-
from __future__ import with_statement
from unidecode import unidecode

import random, os, re

def create_chain(file_paths):
  markov_chain = {}
  word1 = "\n"
  word2 = "\n"
  for path in file_paths:
    with open(path) as file:
      for line in file:
        for current_word in line.split():
          if current_word != "":
            markov_chain.setdefault((word1, word2), []).append(current_word)
            word1 = word2
            word2 = current_word
  return markov_chain

def construct_sentence(word_count=5, slug=False):
  markov_chain = create_chain(["./var/markov/pg6527.txt"])
  
  generated_sentence = ""
  word_tuple = random.choice(markov_chain.keys())
  w1 = word_tuple[0]
  w2 = word_tuple[1]
  
  for i in xrange(word_count):
    #"total count" is a special key used to track word frequency.
    newword = random.choice(markov_chain[(w1, w2)])
    generated_sentence = generated_sentence + " " + newword
    w1 = w2
    w2 = newword
    
  if slug:
    return slugify(generated_sentence)
  return generated_sentence

def specials(s):
  s = s.replace(':', '')
  s = s.replace(';', '')
  s = s.replace('!', '')
  s = s.replace('?', '')

  return s

def rep_accent(input_str):
  nkfd_form = unicodedata.normalize('NFKD', unicode(input_str, 'utf8'))
  return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])

def slugify(text, delim=u'.'):
  _punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

  """Generates an ASCII-only slug."""
  result = []
  for word in _punct_re.split(text.lower()):
      result.extend(word.split())
  return specials(unicode(delim.join(result)))  

