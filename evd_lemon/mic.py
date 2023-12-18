from evdaemon import Module
from subprocess import run, Popen, DEVNULL, PIPE

class micModule(Module):
    name = "mic"
    def __init__(self):
        super().__init__()
        self._pavol = None
        self.listen_private("pavol_ready", self._pavol_ready)

    def check_mic(self):
        if self._pavol != None:
            return
        self._pavol = Popen(["pavol", "micget"], stdin = DEVNULL, stdout = PIPE)
        self._pavol_data = b""
        self.register_file(self._pavol.stdout, "pavol_ready")

    def toggle_mic(self):
        run(["pavol", "micmute", "-quiet"], stdin = DEVNULL, stdout = DEVNULL)
        self.check_mic()

    def _pavol_ready(self):
        data = self._pavol.stdout.read()
        if data == b"":
            self.unregister_file(self._pavol.stdout)
            self._pavol.kill()
            self._pavol = None
            self._pavol_done()
        else:
            self._pavol_data += data

    def _pavol_done(self):
        line = self._pavol_data.decode().split("\n")[0]

        state = {
            "level": None,
            "muted": False
        }

        level_str, mute_str, _ = (line + "%%").split("%", 2)

        try:
            state["level"] = int(line.split("%")[0], 10)
        except ValueError:
            pass

        state["muted"] = "MUTED" in mute_str
        self.emit("mic", "state", state)
