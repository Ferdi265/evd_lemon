#!/usr/bin/env python3
import sys
from argparse import ArgumentParser
from evdaemon import *
from bar import barModule
from barmanager import barManagerModule

def parse():
    parser = ArgumentParser(
        "evd_lemon",
        description = "A python-based i3/sway status-line program"
    )

    parser.add_argument("wm", help = "which window manager to run on (i3 / sway)")

    args = parser.parse_args()
    main(args)

def main(args):
    if args.wm == "i3":
        sockbin = "i3"
        skip_line = False
    elif args.wm == "sway":
        sockbin = "sway"
        skip_line = True
    else:
        print("error: invalid window manager argument: '{}'".format(args.wm), file = sys.stderr)
        sys.exit(1)

    daemon = Daemon()
    daemon.register(barModule(sockbin))
    daemon.register(barManagerModule(skip_line))
    daemon.run()

if __name__ == "__main__":
    parse()
