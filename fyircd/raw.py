# -*- coding: utf-8 -*-
import time

from fyircd.user import User
from fyircd.channel import Channel
from fyircd.ext import raw_callback


def _unknown(target, raw, params):
    pass


"""
    Errors
"""


def _331(target, attr):
    target.send('331 %s %s :No topic is set' % (target, attr))


def _401(target, attr):
    target.send('401 %s %s :No such nick/channel' % (target.nickname, attr))


def _403(target, attr):
    target.send('403 %s %s :No such nick/channel' % (target.nickname, attr))


def _404(target, attr):
    target.send('404 %s %s :Cannot send to channel' % (target.nickname, attr))


def _411(target):
    target.send('411 %s :No recipient given' % (target.nickname))


def _412(target):
    target.send('412 %s :No text to send' % target.nickname)


def _431(target):
    target.send('431 :No nickname given')


def _432(target, attr):
    target.send('432 * %s :Erroneous nickname' % attr)


def _433(target, attr):
    target.send('433 * %s :Nickname is already in use.' % attr)


def _442(target, attr):
    target.send('442 %s :You\'re not on that channel' % attr)


def _462(target):
    target.send('462 You may not reregister')


def _461(target, attr):
    nickname = target.nickname or '*'
    target.send('461 %s %s :Not enough parameters' % (nickname, attr))


def _481(target):
    target.send('481 %s :Permission Denied - You\'re not an IRC operator' % (target.nickname))


"""
    IRC Operator
"""


def kill(target, params):
    if len(params) == 0:
        _461(target, 'KILL')
    else:
        if 'O' in target.modes:
            try:
                if len(params) == 1: reason = 'Why not...'
                else: reason = params[1]

                user = User.by_nickname(params[0])
                user.quit_txt = '☠ /killed by %s (%s) ☠' % (target.nickname, reason)
                user.killed_by = target

                user.disconnect()
            except:
                _401(target, params[0])
        else:
            _481(target)


def oper(target, params):
    if params[1] == target.server.config['opers'][params[0]]:
        target.oper = True

        #target._write(':%s %s' %(target, target.modes.add('OW')))
        target.modes['O'] = 1
        target.modes['W'] = 1
        target.send_modes()
        target.send('381 %s :You are now an IRC Operator' % target.nickname)
        target.send('381 %s :With great power comes great responsibility' % target.nickname)
    else:
        target.send('464 %s :❤ Nice try! ❤' % target.nickname)


"""
    Server command
"""


def users(target, params):
    #todo max :target.send('265 %s %s %s :Current local users %s, max %s')
    target.send(
        '265 %s %s :Current local users %s' %
        (target.nickname, len(len(target.server.users)), len(target.server.users))
    )


def motd(target, params):
    _send_motd(target)


def admin(target, params):
    target.send('256 %s :Administrative info about %s' % (target.nickname, target.server.name))
    if target.config.get('admins'):
        i = 257
        for admin in target.config['admins']:
            target.send('%s %s :%s' % (i, target.nickname, target.server.config.admins[0]))
            i = i + 1


"""
    Greetings
"""


def _first(target):
    target.send('NOTICE * :*** Looking up your hostname...')
    target.send('NOTICE * :*** Checking ident..')
    target.send('NOTICE * :*** Received identd response')
    target.send('NOTICE * :*** Found your hostname')


def _welcome(target):
    if not target.greet:
        target.send('001 %s :Welcome to %s %s' % (target.nickname, target.server.name, target.nickname))
        target.send(
            '002 %s :Your host is "%s", running version %s-%s' %
            (target.nickname, target.server.name, target.server.name, target.server.version)
        )
        target.send('003 %s :This server was created on %s' % (target.nickname, target.server.created))
        target.send(
            '004 %s :%s %s %s %s' % (
                target.nickname, target.server.name, target.server.version, User.concat_modes(),
                Channel.concat_modes()
            )
        )

        options = 'CHANTYPES=# PREFIX=(qaohv)~&@%+ NICKLEN=50 CHANNELLEN=50 TOPICLEN=390 AWAYLEN=160'
        target.send(
            '005 %s :%s %s NETWORK=%s :Are supported by this server' %
            (target.nickname, target.nickname, options, target.server.name)
        )

        target.send(
            '251 %s :%s :There is %s users on %s' %
            (target.nickname, target.nickname, len(target.server.users), target.server.name)
        )
        target.send(
            '254 %s :%s :There is %s channels on %s' %
            (target.nickname, target.nickname, len(Channel.by_name), target.server.name)
        )

        _send_motd(target)

        target.greet = True
        target.send_modes()


def _send_motd(target):
    target.send('375 %s :- %s, message of the day -' % (target.nickname, target.server.name))

    for line in target.server.motd:
        target.send('372 %s :-     %s' % (target.nickname, line.replace("\n", "")))

    target.send('376 %s :End of /MOTD command' % target.nickname)


"""
    User command
"""


def ison(target, params):
    user_list = ''

    for tmp_user in params:
        if User.by_nickname(tmp_user):
            user_list += ' %s' % User.by_nickname(tmp_user).nickname

    target.send('303 %s :%s' % (target.nickname, user_list.strip()))


def ping(target, params):
    target.update_ping()
    target.send('PONG %s :%s' % (target.server.name, params[0]))


def pong(target, params):
    target.update_ping()


def quit(target, params):
    if target.disconnected == False:
        try:
            quit_msg = params[1]
        except:
            quit_msg = '×̯.×'

        target.quit(quit_msg)


def user(target, params):
    if len(params) != 4:
        target.disconnect('gtfo')
    else:
        if target.greet:
            _462(target)
        else:
            print(params)
            target.realname = params[3]
            target.username = params[0]

            if target.nickname:
                _welcome(target)


def userhost(target, params):
    if len(params) == 0:
        _461(target, 'USERHOST')
    else:
        user = User.by_nickname(params[0])
        if user:
            target.send('302 %s :%s=%s' % (target.nickname, user.nickname, user))
        else:
            target.send('302 %s :' % (target.nickname))


def away(target, params):
    try:
        target.away = params[0]
        target.send('306 %s :You have been marked as being away' % target.nickname)
    except:
        target.away = None
        target.send('305 %s :You are no longer marked as being away' % target.nickname)


def who(target, params):
    if len(params) == 0:
        _461(target, 'WHO')
    else:
        channel = Channel.by_id(params[0])
        if channel:
            for user in channel.users:
                target.send(
                    '352 %s %s %s %s %s H%s :0 %s' % (
                        target.nickname, channel, user.hostname, user.server.name, user.nickname,
                        channel.get_prefix_user(user, add=''), user.realname
                    )
                )

            target.send('315 %s %s :End of /WHO list.' % (target.nickname, channel))


def whois(target, params):
    if len(params) == 0:
        _461(target, 'WHOIS')
    else:
        user = User.by_nickname(params[0])
        if user:
            target.send(
                '311 %s %s %s %s * :%s' %
                (target.nickname, user.nickname, user.username, user.hostname, user.realname)
            )

            if len(user.channels) != 0:
                target.send(
                    '319 %s %s :%s' % (
                        target.nickname, user.nickname, ' '.join(
                            [str(channel.get_prefix_user(user) + str(channel)) for channel in user.channels]
                        )
                    )
                )

            if 'O' in target.modes:
                target.send(
                    '313 %s %s :✩✩✩ IRC operator, show some respect! ✩✩✩' % (target.nickname, user.nickname)
                )

            target.send(
                '317 %s %s %s %s :seconds idle, signon time' %
                (target.nickname, user.nickname, (int(time.time()) - user.idle), user.created)
            )

            target.send(
                '312 %s %s %s :%s' %
                (target.nickname, user.nickname, target.server.name, target.server.name)
            )

            target.send('318 %s %s End of /WHOIS list.' % (target.nickname, user.nickname))
        else:
            _401(target, params[0])


def nick(target, params):
    if User.by_nickname(params[0]) != False and User.by_nickname(params[0]) != target:
        _433(target, params[0])
    elif not User.re_nick.match(params[0]):
        _432(target, params[0])
    else:
        if target.greet:
            target.write_relatives(':%s NICK :%s' % (target, params[0]))
            target.rename(params[0])

        else:
            target.rename(params[0])


"""
    Channel command
"""


def _create_channel(name, user):
    if not Channel.re_name.match(name):
        return False

    if Channel.by_id(name) == False:
        channel = Channel(name, creator=user)

        return channel
    else:
        return Channel.by_id(name)


def _split_string_512(str):
    i = 0
    tmp = str.split(' ')
    result = []
    result.append('')

    for word in tmp:
        if (len(result[i] + word) > 512):
            result[i] = result[i].strip()
            i += 1
            result.append('')

        result[i] += word + ' '

    return result


def _join(target, chan):
    channel = _create_channel(chan, target)
    if channel:
        target.join(channel)
        target.send('329 %s %s %s' % (target.nickname, channel, channel.created))
        if channel.topic:
            target.send('332 %s %s %s' % (target.nickname, channel, channel.topic))
        else:
            target.send('331 %s %s %s' % (target.nickname, channel, ':No topic is set'))

        channel.send_modes(target)
        names(target, [chan])
    else:
        _403(target, chan)


def _part(target, chan):
    channel = Channel.by_id(name)
    if channel:
        target.part(channel)
    else:
        _403(target, chan)


def join(target, params):
    if '#' not in params[0]:
        _403(target, params[0])
    else:
        if ',' in params[0]:
            for tmp in params[0].split(','):
                _join(target, tmp)
        else:
            _join(target, params[0])


def part(target, params):
    if '#' not in params[0]:
        _403(target, params[0])
    else:
        if ',' in params[0]:
            for tmp in params[0].split(','):
                _part(target, tmp)
        else:
            _part(target, params[0])


def topic(target, params):
    if '#' in params[0] and len(params) == 2:

        channel = Channel.by_id(params[0])
        if channel and (
            (
                target.oper or target in channel.modes['o'] or target in channel.modes['a'] or
                target in channel.modes['q']
            ) or channel.modes['t'] == 0
        ):
            channel.topic = params[1]
            channel.write(':%s TOPIC %s:%s' % (target, channel, params[1]))


def mode(target, params):
    if '#' in params[0]:
        channel = Channel.by_id(params[0])
        if channel:
            if len(params) == 2:
                channel.send_modes(target)
            elif len(params) == 3:
                channel.add_modes(target, params)
        else:
            _401(target, params[0])


def names(target, params):
    channel = Channel.by_id(params[0])
    if channel:
        to_send = _split_string_512(channel.__str__users__())
        for message in to_send:
            target.send('353 %s = %s :%s' % (target.nickname, params[0], message.strip(' ')))
        target.send('366 %s %s :End of /NAMES list.' % (target.nickname, params[0]))
    else:
        _401(target, params[0])


"""
    Messages
"""


def notice(target, params):
    privmsg(target, params, 'NOTICE')


def privmsg(target, params, cmd='PRIVMSG'):
    if len(params) == 1:
        _412(target)
    elif len(params) == 0:
        _411(target)
    else:
        if raw_callback.get(cmd):
            params = raw_callback[cmd](params)

        if '#' in params[0]:
            channel = Channel.by_id(params[0])
            if channel:
                if channel.can_send(target):
                    channel.write(':%s %s %s :%s' % (target, cmd, params[0], params[1]), ignore_me=target)
                else:
                    _404(target, params[0])
            else:
                _401(target, params[0])
        else:
            try:
                user = User.by_nickname(params[0])
                if user.away:
                    target.send('301 %s %s :%s' % (target.nickname, user.nickname, user.away))
                user.write(':%s %s %s :%s' % (target, cmd, params[0], params[1]))
            except:
                _401(target, params[0])
