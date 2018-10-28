from evdaemon import *
from evdmodule_i3 import *
from network import networkModule
from battery import batteryModule
from time import time
from datetime import datetime
from color import *

def FONTAWESOME(s):
    return '<span font="Font Awesome 5 Free">' + s + '</span>'

class barModule(Module):
    name = "bar"
    def __init__(self):
        super().__init__()

        self.workspace_part = ""
        self.mode_part = ""
        self.title_part = ""
        self.network_part = ""
        self.battery_part = ""
        self.date_part = ""

        self.close_part = {
            "name": "close",
            "full_text": " " + FONTAWESOME("\uf00d") + " ",
            "markup": "pango",
            "color": DARK,
            "background": RED
        }

        self.listen("wm", "title", self._title)
        self.listen("network", "state", self._network)
        self.listen("battery", "state", self._battery)

    def register_daemon(self, daemon):
        super().register_daemon(daemon)

        if "wm" not in daemon.modules:
            daemon.register(i3Module(events = ["window", "workspace", "shutdown"]))

        if "network" not in daemon.modules:
            daemon.register(networkModule())

        if "battery" not in daemon.modules:
            daemon.register(batteryModule())

        self._wm = self.global_state.wm
        self._net = daemon.modules["network"]
        self._bat = daemon.modules["battery"]
        self._check_periodic()
        self._check_clock()

    def unregister_daemon(self, daemon):
        super().unregister_daemon(daemon)
        self._wm = None
        self._net = None
        self._bat = None

    def _check_periodic(self, time_diff = 0):
        self._net.check_connectivity()
        self._bat.check_battery()
        self.timeout(5, self._check_periodic)

    def _check_clock(self, time_diff = 0):
        now = time()
        dt_now = datetime.fromtimestamp(now)
        self.date_part = {
            "name": "date",
            "full_text": "{:%Y-%m-%d %H:%M:%S}".format(dt_now),
            "align": "center"
        }
        self.update_bar()

        dt_last_sec = datetime(dt_now.year, dt_now.month, dt_now.day, dt_now.hour, dt_now.minute, dt_now.second)
        next_sec = dt_last_sec.timestamp() + 1
        now = time()
        self.timeout(next_sec - now, self._check_clock)

    def update_bar(self):
        bar_line = [
            self.title_part,
            self.network_part,
            self.battery_part,
            self.date_part,
            self.close_part
        ]
        self.emit("bar", "line", bar_line)

    def _title(self):
        self.title_part = {
            "name": "title",
            "full_text": self._wm.title
        }
        self.update_bar()

    def _network(self, state):
        bg = GREEN
        fg = DARK

        icon = None
        if "ethernet" in state and state["ethernet"] == "connected":
            icon = " " + FONTAWESOME("\uf0ac") + " "
        elif "wifi" in state and state["wifi"] == "connected":
            icon = " " + FONTAWESOME("\uf1eb") + " "

        if icon == None:
            self.network_part = None
        else:
            self.network_part = {
                "name": "network",
                "full_text": icon,
                "markup": "pango",
                "align": "center",
                "color": DARK,
                "background": GREEN
            }

        self.update_bar()

    def _battery(self, bat):
        bg = None
        fg = DARK

        modifier = " "
        if bat["plugged"]:
            modifier = " " + FONTAWESOME("\uf0e7") + " "
        if bat["level"] == 100:
            bg = BLUE
            icon = " " + FONTAWESOME("\uf240")
        elif bat["level"] > 80:
            bg = GREEN
            icon = " " + FONTAWESOME("\uf240")
        elif bat["level"] > 60:
            bg = GREEN
            icon = " " + FONTAWESOME("\uf241")
        elif bat["level"] > 40:
            bg = GREEN
            icon = " " + FONTAWESOME("\uf242")
        elif bat["level"] > 20:
            bg = YELLOW
            icon = " " + FONTAWESOME("\uf243")
        else:
            bg = RED
            icon = " " + FONTAWESOME("\uf244")

        self.battery_part = {
            "name": "battery",
            "full_text": icon + modifier,
            "markup": "pango",
            "align": "center",
            "color": DARK
        }

        if bg != None:
            self.battery_part["background"] = bg

        self.update_bar()
