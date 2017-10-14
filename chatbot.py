#!/usr/bin/python3
# -*- coding: utf-8 *-*

from telepot.aio.helper import ChatHandler
from telepot import glance

import misc


class ChatBot(ChatHandler):
    """Bot that handles non-admin commands"""
    def __init(self, *args, **kwargs):
        super(ChatBot, self).__init__(*args, **kwargs)

    async def on_chat_message(self, msg):
        """Handles chat message"""
        _, _, chat_id = glance(msg)
        await self.sendMessage(chat_id, msg['text'])

