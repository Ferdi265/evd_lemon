from evdaemon import Module
from evdmodule_i3 import i3Module, i3ipcModule
from linux import linuxModule
from bluetooth import bluetoothModule
from mic import micModule
from network import networkModule
from battery import batteryModule
from time import time
from datetime import datetime
from color import *

def FONTAWESOME(s):
    return '<span font="Font Awesome 6 Free">' + s + '</span>'

class barModule(Module):
    name = "bar"
    def __init__(self, socketpath_binary = "i3"):
        super().__init__()

        self._socketpath_binary = socketpath_binary
        self.workspace_part = { "name": "workspace", "full_text": "" }
        self.mode_part = { "name": "mode", "full_text": "" }
        self.title_part = { "name": "title", "full_text": "" }
        self.linux_part = { "name": "linux", "full_text": "" }
        self.bluetooth_part = { "name": "bluetooth", "full_text": "" }
        self.mic_part = { "name": "mic", "full_text": "" }
        self.network_part = { "name": "network", "full_text": "" }
        self.battery_part = { "name": "battery", "full_text": "" }
        self.date_part = { "name": "date", "full_text": "" }

        self.close_part = {
            "name": "close",
            "full_text": " " + FONTAWESOME("\uf00d") + " ",
            "markup": "pango",
            "color": DARK,
            "background": RED
        }

        self.listen("linux", "updated", self._linux)
        self.listen("bluetooth", "state", self._bluetooth)
        self.listen("wm", "title", self._title)
        self.listen("mic", "state", self._mic)
        self.listen("network", "state", self._network)
        self.listen("battery", "state", self._battery)

    def register_daemon(self, daemon):
        super().register_daemon(daemon)

        if "wm" not in daemon.modules:
            daemon.register(i3ipcModule(socketpath_binary = self._socketpath_binary))
            daemon.register(i3Module(events = ["window", "workspace", "shutdown"]))

        if "linux" not in daemon.modules:
            daemon.register(linuxModule())

        if "bluetooth" not in daemon.modules:
            daemon.register(bluetoothModule())

        if "mic" not in daemon.modules:
            daemon.register(micModule())

        if "network" not in daemon.modules:
            daemon.register(networkModule())

        if "battery" not in daemon.modules:
            daemon.register(batteryModule())

        self._mod_wm = self.global_state.wm
        self._mod_linux = daemon.modules["linux"]
        self._mod_bluetooth = daemon.modules["bluetooth"]
        self._mod_mic = daemon.modules["mic"]
        self._mod_net = daemon.modules["network"]
        self._mod_bat = daemon.modules["battery"]
        self._check_periodic()
        self._check_clock()

    def unregister_daemon(self, daemon):
        super().unregister_daemon(daemon)
        self._mod_wm = None
        self._mod_linux = None
        self._mod_bluetooth = None
        self._mod_net = None
        self._mod_bat = None

    def _check_periodic(self, _ = 0):
        self._mod_linux.check_linux()
        self._mod_bluetooth.check_bluetooth()
        self._mod_mic.check_mic()
        self._mod_net.check_connectivity()
        self._mod_bat.check_battery()
        self.timeout(5, self._check_periodic)

    def _check_clock(self, _ = 0):
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
            self.linux_part,
            self.bluetooth_part,
            self.mic_part,
            self.network_part,
            self.battery_part,
            self.date_part,
            self.close_part
        ]
        self.emit("bar", "line", bar_line)

    def _title(self):
        self.title_part = {
            "name": "title",
            "full_text": self._mod_wm.title
        }
        self.update_bar()

    def _linux(self, updated):
        if updated:
            icon = " " + FONTAWESOME("\uf17c \uf021") + " "
            self.linux_part = {
                "name": "linux",
                "full_text": icon,
                "markup": "pango",
                "align": "center",
                "color": DARK,
                "background": YELLOW
            }
        else:
            self.linux_part = { "name": "linux", "full_text": "" }

        self.update_bar()

    def _bluetooth(self, running):
        if running:
            icon = " " + FONTAWESOME("\uf293") + " "
            self.bluetooth_part = {
                "name": "bluetooth",
                "full_text": icon,
                "markup": "pango",
                "align": "center",
                "color": DARK,
                "background": GREEN
            }
        else:
            self.bluetooth_part = { "name": "bluetooth", "full_text": "" }

        self.update_bar()

    def _mic(self, state):
        bg = GREEN
        fg = DARK

        icon = None
        if "muted" in state:
            icon = " " + FONTAWESOME("\uf131" if state["muted"] else " \uf130 ") + " "

        self.mic_part = {
            "name": "mic",
            "full_text": icon,
            "markup": "pango",
            "align": "center",
            "color": fg,
            "background": bg
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
                "color": fg,
                "background": bg
            }

        self.update_bar()

    def _battery(self, bat):
        bg = None
        fg = DARK

        strlevel = str(bat["level"])
        modifier = " "

        if bat["plugged"]:
            modifier = " " + FONTAWESOME("\uf0e7") + " "

        if bat["level"] is None:
            bg = YELLOW
            icon = " " + FONTAWESOME("\uf244") + " "
            strlevel = "?"
        elif bat["level"] >= 90:
            bg = BLUE
            icon = " " + FONTAWESOME("\uf240")
        elif bat["level"] >= 75:
            bg = GREEN
            icon = " " + FONTAWESOME("\uf241")
        elif bat["level"] >= 50:
            bg = GREEN
            icon = " " + FONTAWESOME("\uf242")
        elif bat["level"] >= 25:
            bg = GREEN
            icon = " " + FONTAWESOME("\uf243")
        elif bat["level"] >= 10:
            bg = YELLOW
            icon = " " + FONTAWESOME("\uf244")
        else:
            bg = RED
            icon = " " + FONTAWESOME("\uf244")

        self.battery_part = {
            "name": "battery",
            "full_text": " " + strlevel + "%" + icon + modifier,
            "markup": "pango",
            "align": "center",
            "color": fg
        }

        if bg != None:
            self.battery_part["background"] = bg

        self.update_bar()
