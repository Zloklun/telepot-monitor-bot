#!/usr/bin/python3

import asyncio as aio
import signal
import telepot.aio

from telepot.aio.loop import MessageLoop
from telepot.aio.delegate import pave_event_space, \
    per_from_id_in, \
    per_from_id, \
    create_open

import chatbot
import inotifier
import loadavg
import misc


token = open(misc.TOKEN_FILE).read().strip()
bot = telepot.aio.DelegatorBot(token, [
    pave_event_space()(
            per_from_id_in(misc.WHITELIST) if misc.WHITELIST
            else per_from_id(),
            create_open,
            chatbot.ChatBot,
            timeout=10
    )
])


def signal_handler(loop):
    """Handler for SIGTERM"""
    misc.log('Caught SIGTERM', category='SHUTDOWN')
    loop.remove_signal_handler(signal.SIGTERM)
    loop.remove_signal_handler(signal.SIGINT)
    task_msg.cancel()
    task_ino.cancel()
    task_lav.cancel()
    loop.stop()


loop = aio.get_event_loop()
loop.add_signal_handler(signal.SIGTERM, signal_handler, loop)
loop.add_signal_handler(signal.SIGINT, signal_handler, loop)

message_loop = MessageLoop(bot)
task_msg = loop.create_task(message_loop.run_forever())
task_ino = loop.create_task(
        inotifier.inotify_start(loop, [
            "/mnt/zram/test/test",
        ], bot)
)
task_lav = loop.create_task(loadavg.LoadavgNotifier(1, (5, 3, 1)).run())

loop.run_forever()
