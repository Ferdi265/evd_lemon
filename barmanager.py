from evdaemon import *
from evdmodule_i3 import i3Module, i3ipcModule
from color import *

from subprocess import Popen, DEVNULL, PIPE

class barManagerModule(Module):
    name = "barManager"
    def __init__(self):
        super().__init__()

        self.bar = Popen([
            "lemonbar",
            "-a", "21",
            "-f", "DejaVu Sans:bold:size=10",
            "-f", "Font Awesome 5 Free:style=Regular:size=10",
            "-f", "Font Awesome 5 Free:style=Solid",
            "-f", "Font Awesome 5 Brands",
            "-B", SLIGHTDARK,
            "-F", LIGHT
        ], stdin = PIPE, stdout = PIPE, stderr = DEVNULL)
        self.register_file(self.bar.stdout, "bar_action")

        self.listen("wm", "monitors", self._monitors)
        self.listen("bar", "line", self._bar)
        self.listen_private("bar_action", self._bar_action)

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

    def _monitors(self):
        print("[WARN][barManager]", "monitors:", "not yet implemented")

    def _bar(self, line):
        self.bar.stdin.write(line.encode() + b"\n")
        self.bar.stdin.flush()

    def _bar_action(self):
        line = self.bar.stdout.readline().decode()[:-1]
        cmd = line[0]
        num = line[1:]
        if cmd == "s":
            self._ipc.send_cmd("command", "workspace {}".format(num))
        elif cmd == "m":
            self._ipc.send_cmd("command", "move container to workspace {}".format(num))
        elif cmd == "k":
            self._ipc.send_cmd("command", "kill")
