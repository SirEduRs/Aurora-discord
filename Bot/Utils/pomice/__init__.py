"""
Pomice
~~~~~~
The modern Lavalink wrapper designed for discord.py.
:copyright: 2021, cloudwithax
:license: GPL-3.0
"""

import disnake

if not disnake.__version__.startswith("2"):

    class DiscordPyOutdated(Exception):
        pass

    raise DiscordPyOutdated(
        "You need the 'disnake' library to use this library"
    )

__version__ = "1.1.7"
__title__ = "pomice"
__author__ = "cloudwithax"

from .enums import SearchType
from .events import *
from .exceptions import *
from .filters import *
from .objects import *
from .player import Player
from .pool import *
