#!/usr/bin/python3
# -*- coding: utf-8 *-*

from telepot.aio.helper import Monitor, UserHandler
from telepot import glance, is_event

import asyncio as aio

import misc
import loadavg
import inotifier

from chatbot import ADMIN_SENDERS


class AdminBot(Monitor):
    def __init__(self, seed_tuple, admins, *args, **kwargs):
        super(AdminBot, self).__init__(
                seed_tuple,
                capture=[[lambda msg: not is_event(msg)]]
        )
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
        misc.log('__init__', category='AdminBot')

    def on__idle(self):
        pass

    async def on_chat_message(self, msg):
        """Handles chat message"""
        pass

    async def send_to_admins(self, message: str):
        """Sends message to all chats in whitelist"""
        if not ADMIN_SENDERS:
            misc.log('ADMIN_SENDERS is empty', category='ChatBot')
            return False
        for _, sender in ADMIN_SENDERS:
            await sender.sendMessage(message, parse_mode='Markdown')
            return True

    async def route_command(self, chat_id, message: str):
        """Routes command to appropriate function"""
        cmd, *args = message.split()
        assert isinstance(cmd, str)
        cmd = cmd.lower()
        if cmd in self.routes.keys():
            await self.send_if_admin(
                    chat_id,
                    self.routes[cmd](cmd, *args),
            )
        else:
            await self.send_if_admin(chat_id, 'Wrong command')
            await self.route_command('/help')

    async def loadavg_notify(self, loadavg):
        await self.send_to_admins('*High loadavg value*:\n' + str(loadavg))
