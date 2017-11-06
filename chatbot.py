#!/usr/bin/python3
# -*- coding: utf-8 *-*

from telepot import glance
from telepot.aio.helper import UserHandler
from telepot.exception import IdleTerminate

import config

# List with tuples (admin_id, sender)
ADMIN_SENDERS = []


def random_number(cmd, *args):
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


def uptime(cmd, *args):
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


def fail2ban(cmd, *args):
    """Fail2Ban commands"""
    pass


class ChatBot(UserHandler):
    """Bot that handles non-admin commands"""
    def __init__(self, seed_tuple, exclude=None, *args, **kwargs):
        super(ChatBot, self).__init__(seed_tuple, *args, **kwargs)
        config.log('__init__', category='ChatBot')
        self.exclude = exclude or set()
        self.routes = {
            '/start': self.start,
            '/help': self.start,
            '/random': random_number,
        }
        self.admin_routes = {
            '/uptime': uptime,
            '/fail2ban': fail2ban,
        }
        if self.user_is_admin():
            ADMIN_SENDERS.append((self.user_id, self.sender))

    def __del__(self):
        config.log('__del__', category='AdminSender')
        ADMIN_SENDERS.remove((self.user_id, self.sender))
        sup = super(ChatBot, self)
        if hasattr(sup, '__del__'):
            sup.__del__()

    def on__idle(self, event):
        """Closes instance by timeout if user is not admin"""
        if self.user_is_admin():
            pass
        else:
            raise IdleTerminate(event['_idle']['seconds'])

    def user_is_admin(self):
        """:returns True if current user is admin"""
        return self.user_id in config.ADMINS_LIST

    async def on_chat_message(self, msg):
        """Handles chat message"""
        content_type = glance(msg)[0]
        config.log(
                '{}{} ({}): {}'.format(
                        '!' if self.user_is_admin() else ' ',
                        self.user_id,
                        content_type,
                        msg['text'],
                ),
                category='ChatBot'
        )
        if msg['from']['id'] in self.exclude:
            self.sender.sendMessage('You are blacklisted')
        elif content_type != 'text':
            self.sender.sendMessage(content_type + 's not supported')
        else:
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
        elif cmd in self.admin_routes.keys():
            if self.user_is_admin():
                await self.sender.sendMessage(
                        self.admin_routes[cmd](cmd, *args),
                        parse_mode='Markdown'
                )
            else:
                await self.sender.sendMessage('Not an admin')
        else:
            await self.sender.sendMessage('Wrong command')
            await self.route_command('/help')

    def start(self, cmd, *args):
        user_cmds = ' /random \[start] \[end]    Prints random number\n'
        if self.user_is_admin():
            admin_cmds = ' /uptime \[units]          Prints uptime\n'
        else:
            admin_cmds = ''

        return 'Available user commands are:\n' + user_cmds + admin_cmds

    async def send_if_admin(self, message: str):
        """Sends message to all chats in whitelist"""
        if not self.user_is_admin():
            return False
        await self.sender.sendMessage(message, parse_mode='Markdown')
        return True
