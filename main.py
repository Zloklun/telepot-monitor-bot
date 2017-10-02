#!/usr/bin/python3

import asyncio
import telepot
import telepot.aio

from os.path import join, dirname
from telepot.aio.loop import MessageLoop
from telepot.aio.delegate import pave_event_space, per_chat_id, create_open

token = open(join(dirname(__file__), 'TOKEN')).read().strip()
bot = telepot.aio.Bot(token)

whitelist = None
try:
    with open(join(dirname(__file__), 'whitelist_ids')) as f:
        whitelist = list(map(int, f.read().split()))
    print('Whitelist:', whitelist)
except IOError:
    print('Whitelist not found')


def random_number(msg):
    __doc__ = """Syntax: /random [start] [end]"""
    import random
    cmd = msg.split()
    if not cmd or cmd[0] != '/random':
        return 'Wrong command'
    elif len(cmd) == 1:
        return str(random.random())
    elif len(cmd) == 2:
        _, arg = cmd
        if arg == 'help':
            return __doc__
        try:
            arg = int(arg)
            return random.randint(1, arg)
        except ValueError:
            return 'Wrong command.\n' + __doc__
    elif len(cmd) == 3:
        try:
            _, a, b = cmd
            a = int(a)
            b = int(b)
            if a > b:
                return __doc__
            else:
                return random.randint(a, b)
        except ValueError:
            return __doc__
    else:
        return __doc__


async def handle_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)
    print(msg)

    if whitelist is not None and msg['from']['id'] not in whitelist:
        print('Unrecognized chat_id. Drop')
        await bot.sendMessage(chat_id, 'Not in whitelist')

    elif content_type == 'text':
        if msg['text'].startswith('/random'):
            await bot.sendMessage(chat_id, random_number(msg['text']))
        else:
            await bot.sendMessage(chat_id, msg['text'])


loop = asyncio.get_event_loop()
loop.create_task(MessageLoop(bot, handle_message).run_forever())

loop.run_forever()
