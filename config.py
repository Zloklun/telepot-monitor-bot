#!/usr/bin/python3

from os.path import join, dirname

DEBUG = True
TOKEN_FILE = join(dirname(__file__), 'TOKEN')
WHITELIST_FILE = join(dirname(__file__), 'whitelist_ids')


def log(*args, **kwargs):
    """Placeholder for log()"""
    pass


if DEBUG:
    from sys import stderr

    def log(*args, **kwargs):
        """Print debug messages"""
        if 'category' in kwargs:
            tag = '[{}]'.format(kwargs['category']) if kwargs['category'] else ''
            del kwargs['category']
            print(tag, *args, file=stderr)
        else:
            print(*args, file=stderr)

WHITELIST = None
try:
    with open(WHITELIST_FILE) as f:
        WHITELIST = list(map(int, f.read().split()))
        log('Whitelist:', WHITELIST)
except IOError:
    log('Whitelist not found. Filtering is off')
