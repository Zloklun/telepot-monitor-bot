#!/usr/bin/python3
# -*- coding: utf-8 *-*

import asyncio as aio

from config import log


def default_callback(loadavg):
    log('loadavg: ', loadavg, category='LoadavgNotifier')


class LoadavgNotifier:
    def __init__(self, timeout, threshold=None, callback=None):
        """
        Initialise instance
        :param timeout: Timeout in seconds
        :param threshold: threshold value in format (1min, 5min, 15min)
        :param callback: function that calls when loadavg is higher than
            :threshold. Must accept float 3-tuple
        """
        from multiprocessing import cpu_count
        self.cpus = cpu_count()
        self.timeout = timeout  # in seconds

        # Reversing because we need it reversed
        self.threshold = list(threshold or (1, 1, 1))
        self.threshold.reverse()
        self.threshold = tuple(self.threshold)

        self.callback = callback or default_callback
        self.running = False
        log('Initialised', category='LoadavgNotifier')

    async def run(self):
        """
        Start main loop
        :return: None
        """
        self.running = True
        log('Started', category='LoadavgNotifier')
        while self.running:
            # Getting loadavg values
            t1, t5, t15, _, _ = open('/proc/loadavg').read().split()
            t1, t5, t15 = map(
                    lambda x: float(x) / self.cpus,
                    [t1, t5, t15]
            )
            if (t15, t5, t1) >= self.threshold:
                log('Emitted', category='LoadavgNotifier')
                await self.callback((t1, t5, t15))
            await aio.sleep(self.timeout)
        log('Stopped', category='LoadavgNotifier')

    def cancel(self):
        self.running = False
