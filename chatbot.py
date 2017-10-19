#!/usr/bin/python3
# -*- coding: utf-8 *-*

from telepot.aio.helper import ChatHandler

import misc


class ChatBot(ChatHandler):
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
        misc.log(self.router.routing_table, category='ChatBot')

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
        return 'Available user commands are:\n' \
               ' /random \[start] \[end]    Prints random number\n'

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
