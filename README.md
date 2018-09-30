FyIRCd
======

One day maybe FyIRCd will be a full-featured IRC server, for now it's just a playground. (Dev server home.fy.to:6667)

# Install & Run FyIRCd
1. git clone https://github.com/Fy-/FyIRCd.git
2. pip install -r requirements.txt
3. py run.py

# Services: fyircd.ext.avengers
Just a start - need to refactor the code.
https://github.com/Fy-/Fy_IRCd/tree/master/fyircd/ext/avengers
```
  OperServ (Loki)
  /oper <user> <pass>
  /msg loki initdb
  
  NickServ
  /msg nickserv register <pass> <mail>
  /msg nickserv identify <pass>
  /msg nickserv help
  
  ChanServ
  /msg chanserv register <channel>
  /msg chanserv assign <channel> <bot_name>
  /msg chanserv help
  
  bot_list = [
    'Deadpool', 'BlackWindow', 'Domino', 'Thor', 'IronMan', 'TheWasp', 'Hulk', 'TheCaptain', 'Hawkeye',
    'ScarletWitch', 'BackPanther', 'Mantis', 'She-Hulk', 'DoctorStrange', 'Spider-Man', 'Vision',
    'WarMachine', 'Logan'
  ] In the start I wanted to add quote for each from comics and MCU.
```

# Unique features
Extensions are not active with the new version, please be patient.

__1. Best hostnames ever:__ Using markov chains and "GNU/Linux: Guide to Installation and Usage"
```
  @when.you.boot.debian.a.FyIRCd.com
  @certain.precautions.are.taken.the.FyIRCd.com
  @cd.it.may.report.installation.FyIRCd.com
  @hardware.user.applications.that.ask.free.fr
  @now.change.to.the.source.free.fr
```
__2. Server side smileys:__
```
 ':(': '😒', ':)': '😊', ':D': '😃', '>.<'  : '😆', '^^': '😄', ':|': '😐', ':p': '😋', '=)': '㋡', '<3': '❤', ':x': '☠', '(note)'  : '♫', '(mail)'  : '✉', '(star)'  : '✩', '(valid)' : '✔', '(flower)': '❀', '(plane)' : '✈', '(copy)'  : '©', '(tel)'   : '☎', 'x.x'  : '٩(×̯×)۶', 'o.o'  : 'Ꙩ_Ꙩ', '<3.<3' : '❤‿❤'
```


