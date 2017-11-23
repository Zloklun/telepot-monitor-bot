### Version 1.1.0 (_23 Nov 2017_)
New release.
1. Adde pyinotify and apt as dependencies
2. Added admin-only-commands filtering
3. Added `/apt` commands
4. Added `/fail2ban` commands
5. Moved handlers into separate functions
6. File `misc.py` renamed to `config.py`
7. Small changes


### Version 1.0.1 (_19 Oct 2017_)
Bugfix
1. Fixed ignoring empty whitelist

#### Version 1.0.0 (_19 Oct 2017_)
Initial version. Features:
1. `/proc/loadavg` monitoring;
2. monitoring files and directories with pyinotify;
3. whitelisting;
4. notifying all admins;
5. available commands:
    * `/uptime` — shows uptime (admins only),
    * `/random` — shows random numbers (for all),
    * `/help` — shows help message for all available commands (for all),
    * `/start` — same as `/help`.
