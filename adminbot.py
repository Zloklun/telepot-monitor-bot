#!/usr/bin/python3
# -*- coding: utf-8 *-*

from telepot.aio.helper import Monitor, UserHandler
from telepot import glance, is_event

import misc


# List with tuples (admin_id, sender)
ADMIN_SENDERS = []


class AdminSender(UserHandler):
    """AdminSender: a class that sends messages to admin"""
    def __init__(self, seed_tuple, *args, **kwargs):
        super(AdminSender, self).__init__(seed_tuple, *args, **kwargs)
        self.admins = misc.ADMINS_LIST or set()
        misc.log('__init__', category='AdminSender')
        global ADMIN_SENDERS
        ADMIN_SENDERS.append((self.user_id, self.sender))

    def __del__(self):
        misc.log('__del__', category='AdminSender')
        ADMIN_SENDERS.remove((self.user_id, self.sender))
        sup = super(AdminSender, self)
        if hasattr(sup, '__del__'):
            sup.__del__()

    async def on_chat_message(self, msg):
        """It does not handle chat message"""
        pass

    def on__idle(self, event):
        """Don't close on timeout"""
        pass


class AdminBot(Monitor):
    def __init__(self, seed_tuple, admins, *args, **kwargs):
        super(AdminBot, self).__init__(
                seed_tuple,
                capture=[[lambda msg: not is_event(msg)]]
        )
        self.admins = admins
        self.routes = {
            '/start': self.start,
            '/help': self.start,
            '/uptime': self.uptime,
        }
        misc.log('__init__', category='AdminBot')

    async def on_chat_message(self, msg):
        """Handles chat message"""
        content_type, chat_type, chat_id = glance(msg)
        for user_id, sender in ADMIN_SENDERS:
            if user_id == chat_id:
                break
        else:
            misc.log('Cannot reply to ' + chat_id, category='AdminBot')
            return

        if content_type != 'text':
            await self.sendMessage(
                    chat_id,
                    'Unsupported content_type ' + content_type
            )
            return
        if misc.WHITELIST and chat_id in misc.WHITELIST:
            await self.route_command(chat_id, msg['text'])
        else:
            await self.route_command(chat_id, 'You are not whitelisted')

    async def send_to_admins(self, message: str):
        """Sends message to all chats in whitelist"""
        if not ADMIN_SENDERS:
            misc.log('ADMIN_SENDERS is empty', category='ChatBot')
            return False
        for _, sender in ADMIN_SENDERS:
            await sender.sendMessage(message, parse_mode='Markdown')
            return True

    async def send_if_admin(self, chat_id, message: str):
        """Sends message to all chats in whitelist"""
        if not ADMIN_SENDERS:
            misc.log('ADMIN_SENDERS is empty', category='ChatBot')
            return False
        for user_id, sender in ADMIN_SENDERS:
            if user_id == chat_id:
                await sender.sendMessage(message, parse_mode='Markdown')
                return True
        else:
            misc.log(
                    '{} not in ADMIN_SENDERS'.format(chat_id),
                    category='ChatBot'
            )
            return False

    async def route_command(self, chat_id, message: str):
        """Routes command to appropriate function"""
        cmd, *args = message.split()
        assert isinstance(cmd, str)
        cmd = cmd.lower()
        if cmd in self.routes.keys():
            await self.send_if_admin(
                    chat_id,
                    self.routes[cmd](cmd, *args),
            )
        else:
            await self.send_if_admin(chat_id, 'Wrong command')
            await self.route_command('/help')

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

    def start(self, cmd, *args):
        return 'Available admin commands are:\n' \
               ' /uptime \[units]          Prints uptime\n'

