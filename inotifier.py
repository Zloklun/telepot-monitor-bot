#!/usr/bin/python3

import pyinotify as pyi

import misc


class InotifyEventHandler(pyi.ProcessEvent):
    def my_init(self, files=[], bot=None):
        self.bot = bot
        self.files = files
        misc.log('Watched files:',
                 files,
                 category='InotifyEventHandler::my_init')

    async def process_event(self, event, prefix):
        async def job():
            if self.bot:
                text = 'Inotify\nFile *{}*\n{}'.format(event.pathname, prefix)
                for chat_id in misc.WHITELIST:
                    await self.bot.sendMessage(chat_id,
                                               text=text,
                                               parse_mode="Markdown")

        if event.pathname in self.files:
            misc.log('[{}]: {}'.format(prefix, event.pathname),
                     category='InotifyEventHandler::process_event')
            return await job()

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
    misc.log(watches, category='INOTIFY')
    handler = InotifyEventHandler(files=files, bot=bot)
    pyi.AsyncioNotifier(wm, loop, default_proc_fun=handler)
