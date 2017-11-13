#!/usr/bin/python3
# -*- coding: utf-8 *-*

from telepot.aio.helper import Monitor

import config
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
                        ['/var/log/auth.log'],
                        callback=self.send_to_admins
                )
        )
        config.log('__init__', category='AdminMonitor')

    async def on_chat_message(self, msg: str):
        """Handles chat message"""
        pass

    async def send_to_admins(self, message: str) -> None:
        """Sends message to all admins"""
        for _, sender in ADMIN_SENDERS:
            await sender.sendMessage(message, parse_mode='Markdown')
        if not ADMIN_SENDERS:
            config.log('ADMIN_SENDERS is empty', category='ChatBot')

    async def loadavg_notify(self, loadavg: (float, float, float)) -> None:
        await self.send_to_admins('*High loadavg value*:\n' + str(loadavg))
