#!/usr/bin/python3
# -*- coding: utf-8 *-*

from telepot.aio.helper import ChatHandler
from telepot import glance

import misc


class ChatBot(ChatHandler):
    """Bot that handles non-admin commands"""
    def __init__(self, seed_tuple, exclude=None, *args, **kwargs):
        super(ChatBot, self).__init__(seed_tuple, *args, **kwargs)
        self.exclude = exclude or set()

    async def on_chat_message(self, msg):
        """Handles chat message"""
        misc.log(msg['text'], category='ChatBot')
        if msg['from']['id'] in self.exclude:
            return

        await self.sender.sendMessage('ChatBot says: ' + msg['text'])

