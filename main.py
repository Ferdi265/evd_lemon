#!/usr/bin/env python3
import sys
from evdaemon import *
from bar import barModule
from barmanager import barManagerModule

def main(sockbin):
    daemon = Daemon()
    daemon.register(barModule(sockbin))
    daemon.register(barManagerModule())
    daemon.run()

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 0:
        sockbin = "i3"
    elif len(args) == 1:
        sockbin = args[0]
    else:
        print("usage: main.py [i3_socketpath_binary]")
        sys.exit(1)
    main(sockbin)
