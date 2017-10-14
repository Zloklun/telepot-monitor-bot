#!/usr/bin/python3

import asyncio as aio
import signal
import telepot.aio

from telepot.aio.loop import MessageLoop
from telepot.aio.delegate import pave_event_space, \
    per_application, \
    create_open

import adminbot
import inotifier
import loadavg
import misc


class BotManager:
    def __init__(self, loop=None):
        self.loop = loop or aio.get_event_loop()
        self.token = open(misc.TOKEN_FILE).read().strip()
        self.bot = telepot.aio.DelegatorBot(self.token, [
            pave_event_space()(
                    per_application(),
                    create_open,
                    adminbot.AdminBot,
                    timeout=10
            )
        ])
        self.message_loop = MessageLoop(self.bot)
        self.tasks = []

    async def run_forever(self):
        self.tasks.append(self.loop.create_task(
                self.message_loop.run_forever()
        ))
        self.tasks.append(self.loop.create_task(
                loadavg.LoadavgNotifier(
                        timeout=1,
                        threshold=(0.5, 0.5, 0.5),
                        callback=self.bot.send_to_whitelist,
                ).run()
        ))
        self.tasks.append(self.loop.create_task(
                inotifier.inotify_start(self.loop, [
                    "/var/log/auth.log",
                ], callback=self.bot.send_to_whitelist)
        ))

    def cancel(self):
        for task in self.tasks:
            task.cancel()


def signal_handler(event_loop):
    """Handler for SIGTERM"""
    misc.log('Caught SIGTERM', category='SHUTDOWN')
    event_loop.remove_signal_handler(signal.SIGTERM)
    event_loop.remove_signal_handler(signal.SIGINT)
    event_loop.stop()


loop = aio.get_event_loop()
loop.add_signal_handler(signal.SIGTERM, signal_handler, loop)
loop.add_signal_handler(signal.SIGINT, signal_handler, loop)

bm = BotManager(loop)
loop.create_task(bm.run_forever())
loop.run_forever()
