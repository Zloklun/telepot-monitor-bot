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
        category = kwargs.get('category', None)
        tag = '[{}] '.format(category) if category else ''
        print(tag, *args, file=stderr)

