#!/usr/bin/python3
# -*- coding: utf-8 *-*

from telepot.aio.helper import UserHandler
from telepot.exception import IdleTerminate

import misc

# List with tuples (admin_id, sender)
ADMIN_SENDERS = []


class ChatBot(UserHandler):
    """Bot that handles non-admin commands"""
    def __init__(self, seed_tuple, exclude=None, *args, **kwargs):
        super(ChatBot, self).__init__(seed_tuple, *args, **kwargs)
        misc.log('__init__', category='ChatBot')
        self.exclude = exclude or set()
        self.routes = {
            '/start': self.start,
            '/help': self.start,
            '/random': self.random_number,
        }
        if self.user_id in misc.ADMINS_LIST:
            self.routes.update({
                '/uptime': self.uptime,
            })
            global ADMIN_SENDERS
            ADMIN_SENDERS.append((self.user_id, self.sender))

    def __del__(self):
        misc.log('__del__', category='AdminSender')
        global ADMIN_SENDERS
        ADMIN_SENDERS.remove((self.user_id, self.sender))
        sup = super(ChatBot, self)
        if hasattr(sup, '__del__'):
            sup.__del__()


    def on__idle(self, event):
        """Don't close on timeout"""
        if self.user_id in misc.ADMINS_LIST:
            pass
        else:
            raise IdleTerminate(event['_idle']['seconds'])

    async def on_chat_message(self, msg):
        """Handles chat message"""
        misc.log(msg['text'], category='ChatBot')
        if msg['from']['id'] in self.exclude:
            self.sender.sendMessage('You are blacklisted')
            return
        await self.route_command(msg['text'])

    async def route_command(self, message: str):
        """Routes command to appropriate function"""
        cmd, *args = message.split()
        assert isinstance(cmd, str)
        cmd = cmd.lower()
        if cmd in self.routes.keys():
            await self.sender.sendMessage(
                    self.routes[cmd](cmd, *args),
                    parse_mode='Markdown'
            )
        else:
            await self.sender.sendMessage('Wrong command')
            await self.route_command('/help')

    def start(self, cmd, *args):
        user_cmds = ' /random \[start] \[end]    Prints random number\n'
        if self.user_id in misc.ADMINS_LIST:
            admin_cmds = ' /uptime \[units]          Prints uptime\n'
        else:
            admin_cmds = ''

        return 'Available user commands are:\n' + user_cmds + admin_cmds


    def random_number(self, cmd, *args):
        """Returns random number"""
        usage = 'Usage: *{}* \[start] \[end]'.format(cmd)
        import random
        if len(args) == 0:
            return str(random.random())
        elif len(args) == 1:
            arg = args[0]
            if arg == 'help':
                return usage
            try:
                arg = int(arg)
                return random.randint(1, arg)
            except ValueError:
                return 'Wrong command.\n' + usage
        elif len(args) == 2:
            try:
                a, b = args
                a = int(float(a))
                b = int(float(b))
                if a > b:
                    return usage
                else:
                    return random.randint(a, b)
            except ValueError:
                return usage
        else:
            return usage

    def uptime(self, cmd, *args):
        """Uptime info"""
        usage = 'Usage: {} \[units]\n' \
                'Supported units are ' \
                'sec, min, hour, days and weeks ' \
                '(only first letter considered)'.format(cmd)
        if not args:
            args = ['d']
        if args and args[0][0].lower() in 'smhdw' and args[0] != 'help':
            seconds = float(open('/proc/uptime').read().split()[0])
            unit = args[0][0].lower()
            full_units = {
                's': 'seconds',
                'm': 'minutes',
                'h': 'hours',
                'd': 'days',
                'w': 'weeks',
            }
            if unit == 's':
                value = seconds
            elif unit == 'm':
                value = seconds / 60
            elif unit == 'h':
                value = seconds / 3600
            elif unit == 'd':
                value = seconds / 3600 / 24
            elif unit == 'w':
                value = seconds / 3600 / 24 / 7
            else:
                return usage
            return '*Uptime*: {:.3f} {}'.format(value, full_units[unit])
        return usage
