# evd-lemon

`evd-lemon` is a Sway and i3 status command using my evdaemon library. This
project was originally created for use with lemonbar, but I have since stopped
using it.

The whole code is quite legacy, but still works, and I will likely replace it
with a real Python `async` implementation soon.

## Installation

- Install using `pipx install .` or `pipx install --editable .`

## Dependencies

- [`evdaemon`](https://github.com/Ferdi265/evdaemon), my poll-based Python
  async event system, from before I knew `asyncio`
