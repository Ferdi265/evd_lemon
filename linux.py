from evdaemon import *
from subprocess import Popen, DEVNULL, PIPE
import os.path

class linuxModule(Module):
    name = "linux"
    def __init__(self):
        super().__init__()
        self._uname = None
        self.listen_private("uname_ready", self._uname_ready)

    def check_linux(self):
        if self._uname != None:
            return
        self._uname = Popen(["uname", "-r"], stdin = DEVNULL, stdout = PIPE)
        self._uname_data = b""
        self.register_file(self._uname.stdout, "uname_ready")

    def _uname_ready(self):
        data = self._uname.stdout.read()
        if data == b"":
            self.unregister_file(self._uname.stdout)
            self._uname.kill()
            self._uname = None
            self._uname_done()
        else:
            self._uname_data += data

    def _uname_done(self):
        version = self._uname_data.decode()[:-1]
        updated = not os.path.exists("/usr/lib/modules/" + version + "/vmlinuz")
        self.emit("linux", "updated", updated)
