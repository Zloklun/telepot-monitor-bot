#!/usr/bin/python3
# -*- coding: utf-8 *-*

from telepot.aio.helper import Monitor, UserHandler
from telepot import glance, is_event

import asyncio as aio

import misc
import loadavg
import inotifier


class AdminBot(Monitor):
    def __init__(self, seed_tuple, admins, *args, **kwargs):
        super(AdminBot, self).__init__(
                seed_tuple,
                capture=[[lambda msg: not is_event(msg)]]
        )
        self.admins = admins
        self.routes = {
            '/start': self.start,
            '/help': self.start,
            '/uptime': self.uptime,
        }
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
        content_type, chat_type, chat_id = glance(msg)
        for user_id, sender in ADMIN_SENDERS:
            if user_id == chat_id:
                break
        else:
            misc.log('Cannot reply to ' + chat_id, category='AdminBot')
            return

        if content_type != 'text':
            await self.sendMessage(
                    chat_id,
                    'Unsupported content_type ' + content_type
            )
            return
        if misc.WHITELIST and chat_id in misc.WHITELIST:
            await self.route_command(chat_id, msg['text'])
        else:
            await self.route_command(chat_id, 'You are not whitelisted')

    async def send_to_admins(self, message: str):
        """Sends message to all chats in whitelist"""
        if not ADMIN_SENDERS:
            misc.log('ADMIN_SENDERS is empty', category='ChatBot')
            return False
        for _, sender in ADMIN_SENDERS:
            await sender.sendMessage(message, parse_mode='Markdown')
            return True

    async def send_if_admin(self, chat_id, message: str):
        """Sends message to all chats in whitelist"""
        if not ADMIN_SENDERS:
            misc.log('ADMIN_SENDERS is empty', category='ChatBot')
            return False
        for user_id, sender in ADMIN_SENDERS:
            if user_id == chat_id:
                await sender.sendMessage(message, parse_mode='Markdown')
                return True
        else:
            misc.log(
                    '{} not in ADMIN_SENDERS'.format(chat_id),
                    category='ChatBot'
            )
            return False

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
