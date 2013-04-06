# -*- coding: utf-8 -*-
def add(params):
  emos = {
    ':('      : '😒',
    ':)'      : '😊',
    ':D'      : '😃',
    '>.<'     : '😆',
    '^^'      : '😄',
    ':|'      : '😐',
    ':p'      : '😋',
    '=)'      : '㋡',
    '<3'      : '❤',
    '#'       : '♯',
    ':x'      : '☠',
    '(note)'  : '♫',
    '(mail)'  : '✉',
    '(star)'  : '✩',
    '(valid)' : '✔',
    '(flower)': '❀',
    '(plane)' : '✈',
    '(copy)'  : '©',
    '(tel)'   : '☎',
    'x.x'     : '٩(×̯×)۶',
    'o.o'     : 'Ꙩ_Ꙩ',
    '<3<3'    : '❤‿❤'
  }

  for smiley in emos:
    params[1] = params[1].replace(smiley, emos[smiley])

  return params