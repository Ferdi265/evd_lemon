from evdaemon import Module
from subprocess import Popen, DEVNULL, PIPE
import os.path

class bluetoothModule(Module):
    name = "bluetooth"
    def __init__(self):
        super().__init__()
        self._bluetoothctl = None
        self.listen_private("bluetoothctl_ready", self._bluetoothctl_ready)

    def check_bluetooth(self):
        if self._bluetoothctl != None:
            return
        self._bluetoothctl = Popen(["bluetoothctl", "show"], stdin = DEVNULL, stdout = PIPE)
        self._bluetoothctl_data = b""
        self.register_file(self._bluetoothctl.stdout, "bluetoothctl_ready")

    def _bluetoothctl_ready(self):
        data = self._bluetoothctl.stdout.read()
        if data == b"":
            self.unregister_file(self._bluetoothctl.stdout)
            self._bluetoothctl.kill()
            self._bluetoothctl = None
            self._bluetoothctl_done()
        else:
            self._bluetoothctl_data += data

    def _bluetoothctl_done(self):
        lines = self._bluetoothctl_data.decode().split("\n")[:-1]
        pairs = map(lambda l: l.split(": ", 1), lines)

        for pair in pairs:
            if len(pair) != 2:
                continue

            key, value = pair
            key = key.strip()
            value = value.strip()

            if key == "Powered":
                self.emit("bluetooth", "state", value == "yes")
                return

        self.emit("bluetooth", "state", False)
