#!/usr/bin/python3

import asyncio
import config
import signal
import telepot
import telepot.aio

from telepot.aio.loop import MessageLoop
from telepot.aio.delegate import pave_event_space, per_chat_id, create_open


def log(*args, **kwargs):
    """Placeholder for log()"""
    pass


if config.DEBUG:
    from sys import stderr

    def log(*args, **kwargs):
        """Print debug messages"""
        category = kwargs.get('category', None)
        tag = '[{}] '.format(category) if category else ''
        print(tag, *args, file=stderr)


class ChatBot(telepot.aio.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(ChatBot, self).__init__(*args, **kwargs)
        self.routes = {
            '/random': self.random_number,
        }
        self.whitelist = None
        try:
            with open(config.WHITELIST_FILE) as f:
                whitelist = list(map(int, f.read().split()))
            log('Whitelist:', whitelist)
        except IOError:
            log('Whitelist not found. Filtering is off')

    async def on_chat_message(self, msg):
        """Handles chat message"""
        content_type, chat_type, chat_id = telepot.glance(msg)
        log(content_type, chat_type, chat_id)
        log(msg)

        if not self.is_whitelisted(msg['from']['id']):
            log('Unrecognized chat_id. Drop')
            await self.sender.sendMessage(chat_id, 'Not in whitelist')
            return

        if content_type == 'text':
            if msg['text'].startswith('/'):
                await self.route_command(msg['text'])
        else:
            await self.sender.sendMessage('Unsupported content_type')

    async def route_command(self, message: str):
        """Routes command to appropriate function"""
        cmd, *args = message.split()
        assert isinstance(cmd, str)
        cmd = cmd.lower()
        if cmd in self.routes.keys():
            await self.sender.sendMessage(self.routes[cmd](cmd, *args))

    def is_whitelisted(self, chat_id) -> bool:
        """Checks if chat_id is whitelisted"""
        if self.whitelist is None:
            return True
        return chat_id in self.whitelist

    def random_number(self, cmd, *args):
        """Returns random number"""
        usage = """Syntax: {} [start] [end]""".format(cmd)
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
                a = int(a)
                b = int(b)
                if a > b:
                    return usage
                else:
                    return random.randint(a, b)
            except ValueError:
                return usage
        else:
            return usage


token = open(config.TOKEN_FILE).read().strip()
bot = telepot.aio.DelegatorBot(token, [
        pave_event_space()(
                per_chat_id(), create_open, ChatBot, timeout=60 * 60
        )
])


def sigterm(loop):
    """Handler for SIGTERM"""
    loop.remove_signal_handler(signal.SIGTERM)
    if not loop.is_closed():
        loop.close()


loop = asyncio.get_event_loop()
loop.create_task(MessageLoop(bot).run_forever())
loop.add_signal_handler(signal.SIGTERM, sigterm, loop)
try:
    loop.run_forever()
except:
    if not loop.is_closed():
        loop.close()
