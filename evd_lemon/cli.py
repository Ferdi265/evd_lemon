#!/usr/bin/env python3
import sys
from argparse import ArgumentParser
from evdaemon import Daemon
from .barmanager import barManagerModule
from .bar import barModule

def parse_args():
    parser = ArgumentParser(
        "evd_lemon",
        description = "A python-based i3/sway status-line program"
    )

    parser.add_argument("wm", help = "which window manager to run on (i3 / sway)")

    return parser.parse_args()

def main():
    args = parse_args()

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
    main()
