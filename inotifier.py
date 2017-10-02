#!/usr/bin/python3

import asyncio as aio
import pyinotify as pyi

from config import WHITELIST_FILE


class InotifyEventHandler(pyi.ProcessEvent):
    def my_init(self, loop=None):
        self.loop = loop if loop else aio.get_event_loop()

    def process_IN_ACCESS(self, event):
        print("ACCESS event:", event.pathname)

    def process_IN_ATTRIB(self, event):
        print("ATTRIB event:", event.pathname)

    def process_IN_CLOSE_NOWRITE(self, event):
        print("CLOSE_NOWRITE event:", event.pathname)

    def process_IN_CLOSE_WRITE(self, event):
        print("CLOSE_WRITE event:", event.pathname)

    def process_IN_CREATE(self, event):
        print("CREATE event:", event.pathname)

    def process_IN_DELETE(self, event):
        print("DELETE event:", event.pathname)

    def process_IN_MODIFY(self, event):
        print("MODIFY event:", event.pathname)

    def process_IN_OPEN(self, event):
        print("OPEN event:", event.pathname)


async def inotify_start(loop, files, event_mask=None):
    files = files or [WHITELIST_FILE]
    event_mask = event_mask or \
                      pyi.IN_MODIFY | pyi.IN_ATTRIB | pyi.IN_CLOSE_WRITE
    wm = pyi.WatchManager()
    wm.add_watch(files, event_mask)
    handler = InotifyEventHandler(loop=loop)
    pyi.AsyncioNotifier(wm, loop, default_proc_fun=handler)
