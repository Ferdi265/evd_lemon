from evdaemon import *
from evdmodule_i3 import i3Module, i3ipcModule
from color import *

from subprocess import Popen, DEVNULL, PIPE

class barManagerModule(Module):
    name = "barManager"
    def __init__(self):
        super().__init__()

        self.bar = self.spawn_bar()
        self.monitor_count = 1

        self.listen("wm", "monitors", self._monitors)
        self.listen("bar", "line", self._bar)
        self.listen_private("bar_action", self._bar_action)

    def spawn_bar(self):
        bar = Popen([
            "lemonbar",
            "-a", "21",
            "-f", "DejaVu Sans:bold:size=10",
            "-f", "Font Awesome 5 Free:style=Regular:size=10",
            "-f", "Font Awesome 5 Free:style=Solid",
            "-f", "Font Awesome 5 Brands",
            "-B", SLIGHTDARK,
            "-F", LIGHT
        ], stdin = PIPE, stdout = PIPE, stderr = DEVNULL)
        self.register_file(bar.stdout, "bar_action")
        return bar

    def respawn_bar(self):
        self.unregister_file(self.bar.stdout)
        self.bar.kill()
        self.bar = self.spawn_bar()

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
        print("[WARN][barManager]", "monitors:", "not yet fully implemented")
        active = list(filter(lambda m: m.active, self._wm.monitors.values()))
        monitor_count = len(active)
        if monitor_count != self.monitor_count:
            # monitor count changed, need to respawn bar
            self.respawn_bar()
            self.monitor_count = monitor_count

    def _bar(self, line):
        multimon_line = ""
        for i in range(self.monitor_count):
            multimon_line += "%{{S{}}}".format(i) + line

        self.bar.stdin.write(multimon_line.encode() + b"\n")
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
