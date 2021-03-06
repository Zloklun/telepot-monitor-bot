#!/usr/bin/python3
# -*- coding: utf-8 *-*

from telepot import glance
from telepot.aio.helper import UserHandler
from telepot.exception import IdleTerminate

from subprocess import Popen, PIPE, DEVNULL

import config

# List with tuples (admin_id, sender)
ADMIN_SENDERS = []


def random_number(cmd: str, *args: [str]) -> str:
    """Returns random number"""
    usage = 'Usage: *{}* \[start] \[end]'.format(cmd)
    import random
    if len(args) == 0:
        return str(random.random())
    elif len(args) == 1:
        arg = args[0]
        if arg == 'help':
            return usage
        try:
            arg = int(arg)
            return random.randint(1, arg)
        except ValueError:
            return 'Wrong command.\n' + usage
    elif len(args) == 2:
        try:
            a, b = args
            a = int(float(a))
            b = int(float(b))
            if a > b:
                return usage
            else:
                return random.randint(a, b)
        except ValueError:
            return usage
    else:
        return usage


def uptime(cmd: str, *args: [str]) -> str:
    """Uptime info"""
    usage = 'Usage: {} \[units]\n' \
            'Supported units are ' \
            'sec, min, hour, days and weeks ' \
            '(only first letter considered)'.format(cmd)
    if not args:
        args = ['d']
    if args and args[0][0].lower() in 'smhdw' and args[0] != 'help':
        seconds = float(open('/proc/uptime').read().split()[0])
        unit = args[0][0].lower()
        full_units = {
            's': 'seconds',
            'm': 'minutes',
            'h': 'hours',
            'd': 'days',
            'w': 'weeks',
        }
        if unit == 's':
            value = seconds
        elif unit == 'm':
            value = seconds / 60
        elif unit == 'h':
            value = seconds / 3600
        elif unit == 'd':
            value = seconds / 3600 / 24
        elif unit == 'w':
            value = seconds / 3600 / 24 / 7
        else:
            return usage
        return '*Uptime*: {:.3f} {}'.format(value, full_units[unit])
    return usage


def fail2ban(cmd: str, *args: [str]) -> str:
    usage = 'Usage: {} \[command]\n' \
            'Supported commands are:\n' \
            '  status  — returns current fail2ban status\n' \
            '  status <jail> — returns current status of a given jail\n' \
            '  ban <ip> <jail> — bans ip in given jail\n' \
            '  unban <ip> <jail> — bans ip in given jail\n' \
            '  checkip <ip> — prints whether given ip is banned\n' \
            ''.format(cmd)
    binary, _ = Popen('which fail2ban-client',
                      shell=True,
                      stdout=PIPE,
                      stderr=DEVNULL).communicate()
    if binary:
        binary = binary.decode().strip()
    else:
        return 'fail2ban-client does _not_ exist'
    if not args or args[0] == 'help':
        return usage

    if args[0].startswith('s'):
        if len(args) > 2:
            return usage
        jail = args[1] if len(args) == 2 else None
        if jail:
            out, err = Popen([binary, 'status', jail],
                             shell=False,
                             stdout=PIPE,
                             stderr=PIPE).communicate()
            lines = out.decode().splitlines(keepends=False)
            cur_ban_count = lines[-3][len('   |- Currently banned: '):]
            addresses = lines[-1][len('   `- Banned IP list:   '):]\
                .replace(' ', ', ')
            result = 'Jail: *{}*\n' \
                     'Currently banned: *{}*\n' \
                     'Banned: {}' \
                     ''.format(jail, cur_ban_count, addresses)
        else:
            out, err = Popen([binary, 'status'],
                             shell=False,
                             stdout=PIPE,
                             stderr=PIPE).communicate()
            result = ''
            if out:
                jails = []
                for line in out.decode().splitlines(keepends=False):
                    if 'Jail list:' in line:
                        jails = line.split()[3:]
                result += 'Jails ({}): {}'.format(len(jails), ' '.join(jails))

        if err:
            result += '\nstderr: *{}*'.format(err.decode().strip())
        return result

    elif args[0].startswith('b'):
        if len(args) != 3:
            return usage
        ip, jail = args[1], args[2]
        out, err = Popen([binary, 'set', jail, 'banip', ip],
                         shell=False,
                         stdout=PIPE,
                         stderr=PIPE).communicate()
        result = ''
        if out:
            result += 'stdout: *{}*'.format(out.decode().strip())
        if err:
            result += '\nstderr: *{}*'.format(err.decode().strip())
        return result

    elif args[0].startswith('u'):
        if len(args) != 3:
            return usage
        ip, jail = args[1], args[2]
        out, err = Popen([binary, 'set', jail, 'unbanip', ip],
                         shell=False,
                         stdout=PIPE,
                         stderr=PIPE).communicate()
        result = ''
        if out:
            result += 'stdout: *{}*'.format(out.decode().strip())
        if err:
            result += '\nstderr: *{}*'.format(err.decode().strip())
        return result

    elif args[0].startswith('c'):
        if len(args) != 2:
            return usage
        ip = args[1]
        jails = []  # Names of active jails
        for line in fail2ban('fail2ban', 'status').splitlines(keepends=False):
            if 'Jail list:' in line:
                jails = line.split()[4:]  # Skip '`-', 'Jail', and 'list:'
        jails = tuple(map(lambda s: s[:-1] if s.endswith(',') else s, jails))
        config.log('Jails are ', jails, category='fail2ban checkip')
        for jail in jails:
            if ip in fail2ban('fail2ban', 'status', jail):
                return '{} *is* banned by _{}_ jail'.format(ip, jail)
        return '{} is *not* banned'.format(ip)

    else:
        return usage


def apt(cmd: str, *args: [str]):
    usage = 'Usage: {} \[command]\n'\
            'Supported commands are:\n' \
            '  upgradable — list of upgradable packages\n' \
            '  versions <package1> [<package2> [<package3> …]] — list of '\
            'available <package>s versions\n'\
            ''.format(cmd)
    if not args:
        return usage

    import apt

    if args[0].startswith('u'):
        cache = apt.Cache()
        cache.open()
        result = ''
        for pkg in cache:
            if not pkg.is_upgradable:
                continue
            cur_ver = None
            for version in pkg.versions:
                if version.is_installed:
                    cur_ver = version.version
                    break
            next_ver = pkg.candidate.version
            result += '*{}*: {} → {}\n'.format(pkg.shortname, cur_ver, next_ver)
        cache.close()
        if result:
            return 'Upgradable packages:\n' + result
        return 'All packages are up-to-date'

    if args[0].startswith('v'):
        if len(args) == 1:
            return usage

        cache = apt.Cache()
        cache.open()
        result = ''
        for name in args[1:]:
            pkg_name = name.replace('*', '').replace('_', '').replace('`', '')
            if pkg_name not in cache:
                result += 'Package *{}* not found\n\n'.format(pkg_name)
                continue
            result += 'Package *{}*:\n'.format(pkg_name)
            package = cache[pkg_name]
            for version in package.versions:
                s = ('ii' if version.is_installed else '').ljust(3)
                result += s + version.version + '\n'
            result += '\n'
        return result

    else:
        return usage


class ChatBot(UserHandler):
    """Bot that handles non-admin commands"""
    def __init__(self, seed_tuple, exclude=None, *args, **kwargs):
        super(ChatBot, self).__init__(seed_tuple, *args, **kwargs)
        config.log('__init__', category='ChatBot')
        self.exclude = exclude or set()
        self.routes = {
            '/start': self.start,
            '/help': self.start,
            '/random': random_number,
        }
        self.admin_routes = {
            '/uptime': uptime,
            '/fail2ban': fail2ban,
            '/apt': apt,
        }
        if self.user_is_admin():
            ADMIN_SENDERS.append((self.user_id, self.sender))

    def __del__(self):
        config.log('__del__', category='AdminSender')
        ADMIN_SENDERS.remove((self.user_id, self.sender))
        sup = super(ChatBot, self)
        if hasattr(sup, '__del__'):
            sup.__del__()

    def on__idle(self, event):
        """Closes instance by timeout if user is not admin"""
        if self.user_is_admin():
            pass
        else:
            raise IdleTerminate(event['_idle']['seconds'])

    def user_is_admin(self) -> bool:
        """:returns True if current user is admin"""
        return self.user_id in config.ADMINS_LIST

    async def on_chat_message(self, msg) -> None:
        """Handles chat message"""
        content_type = glance(msg)[0]
        config.log(
                '{}{} ({}): {}'.format(
                        '!' if self.user_is_admin() else ' ',
                        self.user_id,
                        content_type,
                        msg['text'],
                ),
                category='ChatBot'
        )
        if msg['from']['id'] in self.exclude:
            self.sender.sendMessage('You are blacklisted')
        elif content_type != 'text':
            self.sender.sendMessage(content_type + 's not supported')
        else:
            await self.route_command(msg['text'])

    async def route_command(self, message: str) -> None:
        """Routes command to appropriate function"""
        cmd, *args = message.split()
        assert isinstance(cmd, str)
        cmd = cmd.lower()
        if cmd in self.routes.keys():
            await self.sender.sendMessage(
                    self.routes[cmd](cmd, *args),
                    parse_mode='Markdown'
            )
        elif cmd in self.admin_routes.keys():
            if self.user_is_admin():
                await self.sender.sendMessage(
                        self.admin_routes[cmd](cmd, *args),
                        parse_mode='Markdown'
                )
            else:
                await self.sender.sendMessage('Not an admin')
        else:
            await self.sender.sendMessage('Wrong command')
            await self.route_command('/help')

    def start(self, cmd: str, *args: [str]) -> str:
        user_cmds = '/random \[start] \[end]  Prints random number\n'
        if self.user_is_admin():
            admin_cmds = '\nAvailable admin commands:\n'\
                         '/uptime \[units]         Prints uptime\n' \
                         '/fail2ban \[command]     Executes fail2ban commands\n'\
                         '/apt \[command]          APT commands\n'
        else:
            admin_cmds = ''

        return 'Available user commands:\n' + user_cmds + admin_cmds

    async def send_if_admin(self, message: str) -> None:
        """Sends message to all chats in whitelist"""
        if not self.user_is_admin():
            return
        await self.sender.sendMessage(message, parse_mode='Markdown')
