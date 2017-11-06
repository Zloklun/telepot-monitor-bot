#!/usr/bin/python3

import pyinotify as pyi

import config


class InotifyEvent(pyi.ProcessEvent):
    def my_init(self, files=None, callback=None):
        self.callback = callback
        self.files = files or []
        config.log('Watched files:',
                   files,
                   category='InotifyEvent')

    async def process_event(self, event, prefix):
        if not self.callback:
            config.log('No callback', category='InotifyEvent')
            return

        async def job():
            text = 'Inotify\nFile *{}*\n{}'.format(event.pathname, prefix)
            await self.callback(text)

        if event.pathname in self.files:
            config.log('[{}]: {}'.format(prefix, event.pathname),
                       category='InotifyEvent')
            return await job()

    def process_default(self, event):
        config.sync_exec(self.process_event(event, 'Default event'))

    def process_IN_ATTRIB(self, event):
        config.sync_exec(self.process_event(event, 'Attributes modified'))

    def process_IN_CREATE(self, event):
        config.sync_exec(self.process_event(event, 'Created'))

    def process_IN_CLOSE_WRITE(self, event):
        config.sync_exec(self.process_event(event, 'Wrote and closed'))

    def process_IN_DELETE(self, event):
        config.sync_exec(self.process_event(event, 'Deleted'))

    def process_IN_MODIFY(self, event):
        config.sync_exec(self.process_event(event, 'Modified'))

    def process_IN_MOVE_SELF(self, event):
        config.sync_exec(self.process_event(event, 'Moved'))


async def inotify_start(loop, files, callback=None, event_mask=None):
    from os.path import dirname, isdir
    files = tuple(set(map(
            lambda x: x if isdir(x) else dirname(x),
            files
    )))
    if event_mask is None:
        event_mask = pyi.IN_MODIFY | pyi.IN_ATTRIB | pyi.IN_CLOSE_WRITE | \
                     pyi.IN_DELETE | pyi.IN_CREATE | pyi.IN_MOVE_SELF

    wm = pyi.WatchManager()
    watches = wm.add_watch(files, event_mask,
                           rec=True, do_glob=True, auto_add=True)
    config.log(watches, category='inotify_start')

    handler = InotifyEvent(files=files, callback=callback)
    pyi.AsyncioNotifier(
            watch_manager=wm,
            loop=loop,
            default_proc_fun=handler
    )

