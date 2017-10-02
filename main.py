#!/usr/bin/python3

import asyncio
import config
import signal
import telepot
import telepot.aio

from telepot.aio.loop import MessageLoop
from telepot.aio.delegate import pave_event_space, \
    per_chat_id_in, \
    per_chat_id, \
    create_open


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

    async def on_chat_message(self, msg):
        """Handles chat message"""
        content_type, chat_type, chat_id = telepot.glance(msg)
        log(content_type, chat_type, chat_id)
        log(msg)

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


whitelist = None
try:
    with open(config.WHITELIST_FILE) as f:
        whitelist = list(map(int, f.read().split()))
    log('Whitelist:', whitelist)
except IOError:
    log('Whitelist not found. Filtering is off')

token = open(config.TOKEN_FILE).read().strip()
bot = telepot.aio.DelegatorBot(token, [
        pave_event_space()(
                per_chat_id_in(whitelist) if whitelist else per_chat_id(),
                create_open,
                ChatBot,
                timeout=60 * 60
        )
])


def signal_handler(loop):
    """Handler for SIGTERM"""
    log('Caught SIGTERM', category='SHUTDOWN')
    loop.remove_signal_handler(signal.SIGTERM)
    loop.remove_signal_handler(signal.SIGINT)
    task.cancel()
    loop.stop()


loop = asyncio.get_event_loop()
message_loop = MessageLoop(bot)
task = loop.create_task(message_loop.run_forever())
loop.add_signal_handler(signal.SIGTERM, signal_handler, loop)
loop.add_signal_handler(signal.SIGINT, signal_handler, loop)
loop.run_forever()
