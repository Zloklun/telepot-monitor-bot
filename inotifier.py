#!/usr/bin/python3

import pyinotify as pyi

import config
import misc


class InotifyEventHandler(pyi.ProcessEvent):
    def my_init(self, files=[], bot=None):
        self.bot = bot
        self.files = files
        config.log('Watched files: ',
                   files,
                   category='InotifyEventHandler::my_init')

    async def process_event(self, event, prefix):
        string = '[{}]: {}'.format(prefix, event.pathname)

        async def job():
            if self.bot:
                for chat_id in config.WHITELIST:
                    await self.bot.sendMessage(chat_id, text=string)
        if event.pathname in self.files:
            config.log('PROCESSED',
                       string,
                       category='InotifyEventHandler::process_event')
            return await job()
        else:
            config.log('NOT processed',
                       string,
                       category='InotifyEventHandler::process_event')
            return None

    def process_default(self, event):
        misc.sync_exec(self.process_event(event, 'Default event'))

    def process_IN_ATTRIB(self, event):
        misc.sync_exec(self.process_event(event, 'Attributes modified'))

    def process_IN_CREATE(self, event):
        misc.sync_exec(self.process_event(event, 'Created'))

    def process_IN_CLOSE_WRITE(self, event):
        misc.sync_exec(self.process_event(event, 'Wrote and closed'))

    def process_IN_DELETE(self, event):
        misc.sync_exec(self.process_event(event, 'Deleted'))

    def process_IN_MODIFY(self, event):
        misc.sync_exec(self.process_event(event, 'Modified'))

    def process_IN_MOVE_SELF(self, event):
        misc.sync_exec(self.process_event(event, 'Moved'))


async def inotify_start(loop, files, bot=None, event_mask=None):
    from os.path import dirname
    event_mask = event_mask or \
                      pyi.IN_MODIFY | pyi.IN_ATTRIB | pyi.IN_CLOSE_WRITE | \
                      pyi.IN_DELETE | pyi.IN_CREATE | pyi.IN_MOVE_SELF
    wm = pyi.WatchManager()
    watches = wm.add_watch(
            list(set(map(dirname, files))),
            event_mask)
    config.log(watches, category='INOTIFY')
    handler = InotifyEventHandler(files=files, bot=bot)
    pyi.AsyncioNotifier(wm, loop, default_proc_fun=handler)
