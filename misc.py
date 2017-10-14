import asyncio as aio

from os.path import join, dirname


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


WHITELIST = None
try:
    with open(WHITELIST_FILE) as f:
        WHITELIST = list(map(int, f.read().split()))
        log('Whitelist:', WHITELIST)
except IOError:
    log('Whitelist not found. Filtering is off')


ADMINS_LIST = None
try:
    with open(ADMINS_FILE) as f:
        ADMINS_LIST = list(map(int, f.read().split()))
        log('Whitelist:', ADMINS_LIST)
except IOError:
    log('Admins list have not found. No admins supported')

