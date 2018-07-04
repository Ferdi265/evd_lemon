from evdaemon import *
from evdmodule_i3 import *
from network import networkModule
from battery import batteryModule
from time import time
from datetime import datetime
from color import *

RESET = "-"
CENTER = "%{c}"
LEFT = "%{l}"
RIGHT = "%{r}"

FG = lambda c: "%{F" + c + "}"
BG = lambda c: "%{B" + c + "}"

def CLICK(name, button = None):
    return "%{A" + (str(button) if button != None else "") + ":" + name + ":}"

CLICKEND = "%{A}"

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
        self.close_part = BG(RED) + FG(DARK) + CLICK("k") + " \uf00d " + CLICKEND + FG(RESET) + BG(RESET)

        self.listen("wm", "workspaces", self._workspaces)
        self.listen("wm", "mode", self._mode)
        self.listen("wm", "title", self._title)
        self.listen("network", "state", self._network)
        self.listen("battery", "state", self._battery)

    def register_daemon(self, daemon):
        super().register_daemon(daemon)

        if "wm" not in daemon.modules:
            daemon.register(i3Module())
        
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
        self.date_part = "{:%Y-%m-%d %H:%M:%S}".format(dt_now)
        self.update_bar()
        
        dt_last_sec = datetime(dt_now.year, dt_now.month, dt_now.day, dt_now.hour, dt_now.minute, dt_now.second)
        next_sec = dt_last_sec.timestamp() + 1
        now = time()
        self.timeout(next_sec - now, self._check_clock)

    def update_bar(self):
        bar_line = (
            CENTER + self.title_part +
            LEFT + self.workspace_part + self.mode_part +
            RIGHT + self.network_part + " " + self.battery_part + " " + self.date_part + " " + self.close_part
        )
        self.emit("bar", "line", bar_line)

    def _workspace_markup(self, color, num):
        return color + CLICK("s" + str(num)) + CLICK("m" + str(num), 3) + " \uf111 " + CLICKEND + CLICKEND + BG(RESET) + FG(RESET)

    def _workspaces(self):
        workspace_part = ""

        nextnum = 0
        for workspace in sorted(self._wm.workspaces.values(), key = lambda w: w.num):
            while nextnum < workspace.num:
                workspace_part += self._workspace_markup(FG(SLIGHTDARK), nextnum)
                nextnum += 1

            color = FG(DARK)
            if workspace.urgent:
                color += BG(RED)
            elif workspace.focused:
                color += BG(GREEN)
            elif workspace.visible:
                color += BG(BLUE)
            else:
                color = ""
            workspace_part += self._workspace_markup(color, workspace.num)
            nextnum = workspace.num + 1

        # add at least one clickable empty workspace
        workspace_part += self._workspace_markup(FG(SLIGHTDARK), nextnum)

        self.workspace_part = workspace_part
        self.update_bar()
    
    def _mode(self):
        if self._wm.mode == None:
            self.mode_part = ""
        else:
            self.mode_part = BG(GREEN) + FG(DARK) + " " + self._wm.mode + " mode " + BG(RESET) + FG(RESET)
        self.update_bar()
    
    def _title(self):
        self.title_part = self._wm.title.replace("%", "%%")
        self.update_bar()

    def _network(self, state):
        color = BG(GREEN) + FG(DARK)
        reset = BG(RESET) + FG(RESET)
        if state["ethernet"] == "connected":
            icon = " \uf0ac "
        elif state["wifi"] == "connected":
            icon = " \uf1eb "
        else:
            color = ""
            icon = ""
            
        self.network_part = color + icon + reset
        self.update_bar()

    def _battery(self, bat):
        color = FG(DARK)
        reset = FG(RESET) + BG(RESET)

        modifier = ""
        if bat["plugged"]:
            modifier = " \uf0e7"

        if bat["level"] == 100:
            color += BG(BLUE)
            icon = "\uf240"
        elif bat["level"] > 80:
            color += BG(GREEN)
            icon = "\uf240"
        elif bat["level"] > 60:
            color += BG(GREEN)
            icon = "\uf241"
        elif bat["level"] > 40:
            color += BG(GREEN)
            icon = "\uf242"
        elif bat["level"] > 20:
            color += BG(YELLOW)
            icon = "\uf243"
        else:
            color += BG(RED)
            icon = "\uf244"

        self.battery_part = color + " " + icon + modifier + " " + reset
        self.update_bar()

