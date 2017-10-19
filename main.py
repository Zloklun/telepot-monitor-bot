#!/usr/bin/python3
# -*- coding: utf-8 *-*


import asyncio as aio
import signal
import telepot.aio

from telepot.aio.loop import MessageLoop
from telepot.aio.delegate import pave_event_space, \
    per_from_id_in, \
    per_application, \
    create_open

import adminbot
import chatbot
import misc


class BotManager(telepot.aio.DelegatorBot):
    def __init__(self, whitelist=None, admins_list=None):
        self.token = open(misc.TOKEN_FILE).read().strip()
        self.admins = admins_list
        self.whitelist = whitelist
        self._seen = set()
        super(BotManager, self).__init__(self.token, [
            pave_event_space()(
                    per_from_id_in(self.whitelist),
                    create_open,
                    chatbot.ChatBot,
                    None,
                    timeout=10 * 60
            ),
            (
                per_application(),
                create_open(adminbot.AdminBot, self.admins)
            ),
        ])


def signal_handler(event_loop):
    """Handler for SIGTERM"""
    misc.log('Caught SIGTERM', category='SHUTDOWN')
    event_loop.remove_signal_handler(signal.SIGTERM)
    event_loop.remove_signal_handler(signal.SIGINT)
    event_loop.stop()


loop = aio.get_event_loop()
loop.add_signal_handler(signal.SIGTERM, signal_handler, loop)
loop.add_signal_handler(signal.SIGINT, signal_handler, loop)

bm = BotManager(
        whitelist=misc.WHITELIST,
        admins_list=misc.ADMINS_LIST)
loop.create_task(MessageLoop(bm).run_forever())
loop.run_forever()
