#!/usr/bin/python2.7

import os, os.path, time, sys, datetime
from datetime import datetime

fname1 = "/var/log/cron/mybackup01.log"
fname2 = "/var/log/cron/mybackup02.log"
fname3 = "/var/log/cron/mybackup03.log"

folders = [(fname1), (fname2), (fname3)]

for folder in folders:
    if os.path.isfile(folder) and os.access(folder, os.R_OK):
        now = datetime.now()
            modifiedtime = datetime.fromtimestamp(float(os.path.getmtime(folder))).strftime("%d %m %Y %H %M")

        print modifiedtime

            t = now.today().strftime("%d %m %Y %H %M")
        print t
        print folder + " File exists and is readable"

            if t != modifiedtime:
            print folder + " is not uptodate\n"
            sys.exit(1)
        else:
            print folder + " is uptodate\n"
    else:
            print folder + " Either file is missing or is not readable"
        sys.exit(2)
