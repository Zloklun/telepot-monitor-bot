zlobot
======

Simple bot for monitoring private server

Config files
================

* `TOKEN` — file that contains only bot token
* `admin_ids` — list of admins (those who receive system messages)
* `whitelist_ids` — list of whitelisted users (those who can chat with bot)

Available commands
==================

All commands support `help` as argument, e.g. `/uptime help`.

### Commands available for all

* `/help` — prints all commands available for current 
    user (including admin ones if user is in `admin_ids`).
* `/random [[start] end]` — returns random integer value from
    `[start; end]` if both arguments are presented and correct.
    If only `start` is presented, returns random integer from
    `[1; start]`.
    If both arguments are omitted, returns random float from
    `[0; 1)` (same as python's `random.random()`).
* `/start` — same as `/help`.

### Admin commands

* `/uptime [units]` — prints server uptime in given `units`.
    Units must be one of `s` (seconds), `m` (minutes), 
    `h` (hours), `d` (days) and `w` (weeks). `units` value
    defaults to `d`.
* `/fail2ban` — executes `fail2ban-client` with some arguments:
    * `/fail2ban status [jail]` is same as `fail2ban-client status [jail]`:
        prints status of a given jail if presented (includes
        watched logfiles and banned ips); otherwise prints
        current fail2ban status;
    * `/fail2ban ban <ip> <jail>` is same as
        `fail2ban-client set <jail> banip <ip>`;
    * `/fail2ban unban <ip> <jail>` is same as
        `fail2ban-client set <jail> unbanip <ip>`;
    * `/fail2ban checkip <ip>` — prints whether given ip is banned.
* `/apt` — executes some APT commands:
    * `/apt upgradables` — returns list of upgradable packages
        in format: «**name** : __oldver__ → __newver__»
        (some kind of `apt list --upgradable`)
    * `apt versions <package1> [<package2> [<package3> …]]` — returns
        all available versions of given packages.
