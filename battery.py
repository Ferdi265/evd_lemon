from evdaemon import *
from subprocess import Popen, DEVNULL, PIPE

class batteryModule(Module):
    name = "battery"
    def __init__(self):
        super().__init__()
        self._acpi = None
        self.listen_private("acpi_ready", self._acpi_ready)

    def check_battery(self):
        if self._acpi != None:
            return
        self._acpi = Popen(["acpi", "-ab"], stdin = DEVNULL, stdout = PIPE)
        self._acpi_data = b""
        self.register_file(self._acpi.stdout, "acpi_ready")

    def _acpi_ready(self):
        data = self._acpi.stdout.read()
        if data == b"":
            self.unregister_file(self._acpi.stdout)
            self._acpi.kill()
            self._acpi = None
            self._acpi_done()
        else:
            self._acpi_data += data

    def _acpi_done(self):
        lines = self._acpi_data.decode().split("\n")[:-1]
        pairs = map(lambda l: l.split(": ", 1), lines)

        state = {
            "level": None,
            "plugged": False
        }

        for pair in pairs:
            if pair[0] == "Battery 0":
                parts = pair[1].split(", ")
                status, percent, *rest = parts
                state["level"] = int(percent[:-1], 10)
            elif pair[0] == "Adapter 0":
                if pair[1] == "on-line":
                    state["plugged"] = True

        self.emit("battery", "state", state)
