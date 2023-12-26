from evdaemon import Module
from subprocess import Popen, DEVNULL, PIPE
import socket

class batteryModule(Module):
    name = "battery"
    def __init__(self):
        super().__init__()
        self._upower = None
        self.listen_private("upower_ready", self._upower_ready)

        if socket.gethostname() == "momo":
            self._charge_max = 80
            self._battery_path = "/org/freedesktop/UPower/devices/battery_BAT1"
        else:
            self._charge_max = 100
            self._battery_path = "/org/freedesktop/UPower/devices/battery_BAT0"


    def check_battery(self):
        if self._upower != None:
            return

        self._upower = Popen(["upower", "-i", self._battery_path], stdin = DEVNULL, stdout = PIPE)
        self._upower_data = b""
        self.register_file(self._upower.stdout, "upower_ready")

    def _upower_ready(self):
        data = self._upower.stdout.read()
        if data == b"":
            self.unregister_file(self._upower.stdout)
            self._upower.kill()
            self._upower = None
            self._upower_done()
        else:
            self._upower_data += data

    def _upower_done(self):
        lines = self._upower_data.decode().split("\n")[:-1]
        pairs = map(lambda l: l.split(": ", 1), lines)

        state = {
            "level": None,
            "plugged": False
        }

        for pair in pairs:
            if len(pair) != 2:
                continue

            key, value = pair
            key = key.strip()
            value = value.strip()

            if key == "state":
                state["plugged"] = value == "charging" or value == "fully-charged"
            elif key == "percentage":
                try:
                    state["level"] = int(value[:-1], 10)
                except ValueError:
                    pass

        if state["level"] is not None:
            state["level"] = int(state["level"] * 100 / self._charge_max)

        self.emit("battery", "state", state)
