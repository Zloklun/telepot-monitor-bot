#!/usr/bin/python3
# -*- coding: utf-8 *-*

from telepot.aio.helper import Monitor

import misc
import loadavg
import inotifier

from chatbot import ADMIN_SENDERS


class AdminMonitor(Monitor):
    def __init__(self, seed_tuple, admins, *args, **kwargs):
        super(AdminMonitor, self).__init__(seed_tuple, capture=[[lambda msg: False]])
        import asyncio as aio
        loop = aio.get_event_loop()
        loop.create_task(
                loadavg.LoadavgNotifier(
                        5,
                        callback=self.loadavg_notify
                ).run()
        )
        loop.create_task(
                inotifier.inotify_start(
                        loop,
                        ['/mnt/zram/test'],
                        callback=self.send_to_admins
                )
        )
        misc.log('__init__', category='AdminMonitor')

    async def on_chat_message(self, msg):
        """Handles chat message"""
        pass

    async def send_to_admins(self, message: str):
        """Sends message to all admins"""
        if not ADMIN_SENDERS:
            misc.log('ADMIN_SENDERS is empty', category='ChatBot')
            return False
        for _, sender in ADMIN_SENDERS:
            await sender.sendMessage(message, parse_mode='Markdown')
            return True

    async def loadavg_notify(self, loadavg):
        await self.send_to_admins('*High loadavg value*:\n' + str(loadavg))
