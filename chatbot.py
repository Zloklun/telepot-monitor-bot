#!/usr/bin/python3

from telepot.aio.helper import ChatHandler
from telepot import glance

import misc


class ChatBot(ChatHandler):
    def __init__(self, *args, **kwargs):
        super(ChatBot, self).__init__(*args, **kwargs)
        self.routes = {
            '/start': self.start,
            '/help': self.start,
            '/random': self.random_number,
            '/uptime': self.uptime,
        }

    async def on_chat_message(self, msg):
        """Handles chat message"""
        content_type, chat_type, chat_id = glance(msg)
        misc.log(content_type, chat_type, chat_id)
        misc.log(msg)

        if content_type == 'text':
            await self.route_command(msg['text'])
        else:
            await self.sender.sendMessage('Unsupported content_type ' +
                                          content_type)

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
        return 'Available commands are:\n' \
               ' /random \[start] \[end]    Prints random number\n' \
               ' /uptime \[units]          Prints uptime\n'

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
