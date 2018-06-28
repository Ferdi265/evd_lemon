#!/usr/bin/env python3
from evdaemon import *
from bar import barModule
from barmanager import barManagerModule

def main():
    daemon = Daemon()
    daemon.register(barModule())
    daemon.register(barManagerModule())
    daemon.run()

if __name__ == "__main__":
    main()
