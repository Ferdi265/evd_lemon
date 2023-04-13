import sys
import string
import json

from evdaemon import Module
from evdmodule_i3 import i3Module, i3ipcModule
from mic import micModule
from color import *

def scan_json_obj_naive(f):
    d = ""

    def chomp():
        nonlocal d
        c = f.read(1)
        if c == '':
            raise EOFError("unexpected end of object stream")
        d += c
        return c

    while chomp() in string.whitespace + "," + "[":
        d = ""

    assert d == "{", "non-object encountered"
    while chomp() != "}":
        pass

    return json.loads(d)

class barManagerModule(Module):
    name = "barManager"
    def __init__(self, skip_line):
        super().__init__()

        self.monitor_count = 1

        print(json.dumps({ "version": 1, "click_events": True }))
        print("[")
        sys.stdout.flush()
        if skip_line:
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

        if "mic" not in daemon.modules:
            daemon.register(micModule())

        self._wm = self.global_state.wm
        self._ipc = daemon.modules["i3ipc"]
        self._mod_mic = daemon.modules["mic"]

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
        if "name" in msg and msg["name"] == "mic":
            self._mod_mic.toggle_mic()
