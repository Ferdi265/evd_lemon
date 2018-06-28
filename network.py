from evdaemon import *
from subprocess import Popen, DEVNULL, PIPE

class networkModule(Module):
    name = "network"
    def __init__(self):
        super().__init__()
        self._nmcli = None
        self.listen_private("nm_ready", self._nm_ready)

    def check_connectivity(self):
        if self._nmcli != None:
            return
        self._nmcli = Popen(["nmcli", "-t", "--fields", "TYPE,STATE", "d"], stdin = DEVNULL, stdout = PIPE)
        self._nm_data = b""
        self.register_file(self._nmcli.stdout, "nm_ready")

    def _nm_ready(self):
        data = self._nmcli.stdout.read()
        if data == b"":
            self.unregister_file(self._nmcli.stdout)
            self._nmcli.kill()
            self._nmcli = None
            self._nm_done()
        else:
            self._nm_data += data

    def _nm_done(self):
        lines = self._nm_data.decode().split("\n")[:-1]
        pairs = map(lambda l: l.split(":"), lines)
        state = {p[0]: p[1] for p in pairs}
        self.emit("network", "state", state)
