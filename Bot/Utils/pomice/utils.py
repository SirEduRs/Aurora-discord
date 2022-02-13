import random
import socket
import time
from itertools import zip_longest
from timeit import default_timer as timer
from typing import Any, Dict, Optional

__all__ = ["ExponentialBackoff", "NodeStats"]


class ExponentialBackoff:
    """
    The MIT License (MIT)
    Copyright (c) 2015-present Rapptz
    Permission is hereby granted, free of charge, to any person obtaining a
    copy of this software and associated documentation files (the "Software"),
    to deal in the Software without restriction, including without limitation
    the rights to use, copy, modify, merge, publish, distribute, sublicense,
    and/or sell copies of the Software, and to permit persons to whom the
    Software is furnished to do so, subject to the following conditions:
    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
    OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
    DEALINGS IN THE SOFTWARE.
    """
    def __init__(self, base: int = 1, *, integral: bool = False) -> None:

        self._base = base

        self._exp = 0
        self._max = 10
        self._reset_time = base * 2**11
        self._last_invocation = time.monotonic()

        rand = random.Random()
        rand.seed()

        self._randfunc = rand.randrange if integral else rand.uniform

    def delay(self) -> float:

        invocation = time.monotonic()
        interval = invocation - self._last_invocation
        self._last_invocation = invocation

        if interval > self._reset_time:
            self._exp = 0

        self._exp = min(self._exp + 1, self._max)
        return self._randfunc(0, self._base * 2**self._exp)  # type: ignore


class NodeStats:
    """The base class for the node stats object.
       Gives critical information on the node, which is updated every minute.
    """
    def __init__(self, data: Dict[Any, Any]) -> None:

        memory = data.get("memory")
        self.used = memory.get("used")  # type: ignore
        self.free = memory.get("free")  # type: ignore
        self.reservable = memory.get("reservable")  # type: ignore
        self.allocated = memory.get("allocated")  # type: ignore

        cpu: Dict[Any, Any] = data.get("cpu")  # type: ignore
        self.cpu_cores = cpu.get("cores")
        self.cpu_system_load = cpu.get("systemLoad")
        self.cpu_process_load = cpu.get("lavalinkLoad")

        self.players_active = data.get("playingPlayers")
        self.players_total = data.get("players")
        self.uptime = data.get("uptime")

    def __repr__(self) -> str:
        return f"<Pomice.NodeStats total_players={self.players_total!r} playing_active={self.players_active!r}>"


class Ping:
    # Thanks to https://github.com/zhengxiaowai/tcping for the nice ping impl
    def __init__(self, host: str, port: int, timeout: float = 5) -> None:
        self.timer = self.Timer()

        self._successed = 0
        self._failed = 0
        self._conn_time = None
        self._host = host
        self._port = port
        self._timeout = timeout

    class Socket(object):
        def __init__(self, family: Any, type_: Any, timeout: float) -> None:
            s = socket.socket(family, type_)
            s.settimeout(timeout)
            self._s = s

        def connect(self, host: str, port: int) -> None:
            self._s.connect((host, port))

        def shutdown(self) -> None:
            self._s.shutdown(socket.SHUT_RD)

        def close(self) -> None:
            self._s.close()

    class Timer(object):
        def __init__(self) -> None:
            self._start: float = 0
            self._stop: float = 0

        def start(self) -> None:
            self._start = timer()

        def stop(self) -> None:
            self._stop = timer()

        def cost(self, funcs: Any, args: Any) -> Any:
            self.start()
            for func, arg in zip_longest(funcs, args):
                if arg:
                    func(*arg)
                else:
                    func()

            self.stop()
            return self._stop - self._start

    def _create_socket(self, family: Any, type_: Any) -> Any:
        return self.Socket(family, type_, self._timeout)

    def get_ping(self) -> Any:
        s = self._create_socket(socket.AF_INET, socket.SOCK_STREAM)

        cost_time = self.timer.cost(
            (s.connect, s.shutdown), ((self._host, self._port), None)
        )
        s_runtime = 1000 * (cost_time)

        return s_runtime
