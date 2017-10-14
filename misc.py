#!/usr/bin/python3
# -*- coding: utf-8 *-*

import asyncio as aio

from os.path import join, dirname
from telepot.aio.delegate import exception

def sync_exec(coro):
    aio.ensure_future(coro)


DEBUG = True
DIR = dirname(__file__)
TOKEN_FILE = join(DIR, 'TOKEN')
WHITELIST_FILE = join(DIR, 'whitelist_ids')
ADMINS_FILE = join(DIR, 'admin_ids')


def log(*args, **kwargs):
    """Placeholder for log()"""
    pass


if DEBUG:
    from sys import stderr

    def log(*args, **kwargs):
        """Print debug messages"""
        if 'category' in kwargs:
            if kwargs['category']:
                tag = '[{}]'.format(kwargs['category'])
                del kwargs['category']
                print(tag, *args, file=stderr)
            else:
                print(*args, file=stderr)
            del kwargs['category']
        else:
            print(*args, file=stderr)


# Filling whitelist
WHITELIST = None
try:
    with open(WHITELIST_FILE) as f:
        WHITELIST = list(map(int, f.read().split()))
        log('Whitelist:', WHITELIST)
except IOError:
    log('Whitelist not found. Filtering is off')


# Filling admin list
ADMINS_LIST = None
try:
    with open(ADMINS_FILE) as f:
        ADMINS_LIST = list(map(int, f.read().split()))
        log('Whitelist:', ADMINS_LIST)
except IOError:
    log('Admins list have not found. No admins supported')


# Some seeder functions

def _wrap_none(fn):
    """
    Stolen from telepot.aio.delegate.py
    :param fn: function to wrap
    :return: wrapped function
    """
    def w(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except (KeyError, exception.BadFlavor):
            return None
    return w


def per_admin():
    """
    :return:
        a seeder function that returns the from id only if the from id is in
        the ``ADMINS_LIST``. If ADMINS_LIST is None, returns None.
    """
    if ADMINS_LIST is not None:
        return None
    else:
        return _wrap_none(lambda msg:
                          msg['from']['id']
                          if msg['from']['id'] in ADMINS_LIST
                          else None)
