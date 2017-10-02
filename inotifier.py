#!/usr/bin/python3

import asyncio as aio
import pyinotify as pyi

import config
import misc


class InotifyEventHandler(pyi.ProcessEvent):
    def my_init(self, loop=None, bot=None):
        self.loop = loop if loop else aio.get_event_loop()
        self.bot = bot

    async def process_event(self, event, event_name):
        string = '{} at {}'.format(event_name, event.pathname)
        config.log(string, category='INOTIFY')

        async def job():
            if self.bot:
                for chat_id in config.WHITELIST:
                    await self.bot.sendMessage(chat_id, text=string)
        return await job()

    def process_default(self, event):
        misc.sync_exec(self.process_event(event, 'Default event'))

    def process_IN_ATTRIB(self, event):
        misc.sync_exec(self.process_event(event, 'IN_ATTRIB'))

    def process_IN_CREATE(self, event):
        misc.sync_exec(self.process_event(event, 'IN_CREATE'))

    def process_IN_CLOSE_WRITE(self, event):
        misc.sync_exec(self.process_event(event, 'IN_CLOSE_WRITE'))

    def process_IN_DELETE(self, event):
        misc.sync_exec(self.process_event(event, 'IN_DELETE'))

    def process_IN_MODIFY(self, event):
        misc.sync_exec(self.process_event(event, 'IN_MODIFY'))


async def inotify_start(loop, files, bot=None, event_mask=None):
    event_mask = event_mask or \
                      pyi.IN_MODIFY | pyi.IN_ATTRIB | pyi.IN_CLOSE_WRITE | \
                      pyi.IN_DELETE | pyi.IN_CREATE
    wm = pyi.WatchManager()
    wm.add_watch(files, event_mask)
    handler = InotifyEventHandler(loop=loop, bot=bot)
    pyi.AsyncioNotifier(wm, loop, default_proc_fun=handler)
