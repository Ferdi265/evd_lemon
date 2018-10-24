import sys
import string
import json

from evdaemon import *
from evdmodule_i3 import i3Module, i3ipcModule
from color import *

from subprocess import Popen, DEVNULL, PIPE

def scan_json_obj_naive(f):
    d = ""

    def chomp():
        nonlocal d
        c = f.read(1)
        d += c
        return c

    while chomp() in string.whitespace + ",":
        d = ""

    assert d == "{", "non-object encountered"
    while chomp() != "}":
        pass

    return json.loads(d)

class barManagerModule(Module):
    name = "barManager"
    def __init__(self):
        super().__init__()

        self.monitor_count = 1

        print(json.dumps({ "version": 1, "click_events": True }))
        print("[")
        sys.stdout.flush()
        sys.stdin.readline()

        self.listen("bar", "line", self._bar)
        self.listen_private("bar_action", self._bar_action)
        self.register_file(sys.stdin.buffer, "bar_action")

    def register_daemon(self, daemon):
        super().register_daemon(daemon)

        if "wm" not in daemon.modules:
            daemon.register(i3Module())

        if "i3ipc" not in daemon.modules:
            daemon.register(i3ipcModule())

        self._wm = self.global_state.wm
        self._ipc = daemon.modules["i3ipc"]

    def unregister_daemon(self, daemon):
        super().unregister_daemon(daemon)

        self._wm = None
        self._ipc = None

    def _bar(self, blocks):
        print(json.dumps(blocks) + ",")
        sys.stdout.flush()

    def _bar_action(self):
        msg = scan_json_obj_naive(sys.stdin)
        if "name" in msg and msg["name"] == "close":
            self._ipc.send_cmd("command", "kill")
