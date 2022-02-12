"""
MIT License

Copyright (c) 2022 Eduardo Rodrigues

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import gc
import json
import os
import pathlib
from datetime import datetime
from typing import Any

import aiohttp
import disnake  # type: ignore
import firebase_admin  # type: ignore
from disnake.ext import commands
from disnake.ext.commands import Bot  # type: ignore
from firebase_admin import credentials  # type: ignore

from Utils import Database, Firebase  # type: ignore
from Utils.pomice import NodePool

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "Utils/Archives/auth.json"

# Init Firebase
firebase_admin.initialize_app(
    credentials.ApplicationDefault(), {'projectId': 'mta-sa-iz-server'}
)  # type: ignore

intents = disnake.Intents.all()

path = pathlib.Path('Cogs')

with open("Utils/Archives/emojis.json") as emojis:
    _emoji = json.loads(emojis.read())


class AuroraClass(Bot):
    def __init__(self, *args: Any, **kwargs: Any):
        async def prefix(bot: commands.Bot, message: disnake.Message):
            db = Database(bot)
            prefixx = await db.get_prefix(message)  # type: ignore
            return commands.when_mentioned_or(prefixx)(
                bot, message
            )  # type: ignore

        kwargs['command_prefix'] = prefix
        kwargs['intents'] = intents
        kwargs['help_command'] = None
        kwargs['case_insensitive'] = True
        super().__init__(*args, **kwargs)  # type: ignore
        self.load_extension("jishaku")
        self.utils = {
            "uptime": datetime.now(),
            "commands": 0,
            "emoji": _emoji,
            "api_key": os.getenv("API_KEY")
        }
        self.owner_id: int = 416606375498481686
        self.db: Database = Database(self)
        self.fdb = Firebase(self)
        self.reload = True
        self.pomice = NodePool()

        gc.enable()

    @staticmethod
    def emoji(emoji: str):
        return _emoji[emoji]

    async def load_cogs(self):
        for f in path.rglob('*.py'):
            with open(f, 'rb') as of:
                for l in of.read().decode().splitlines():
                    if l.startswith('def setup(bot: AuroraClass)'):
                        f = str(f).replace("/", ".")
                        try:
                            self.load_extension(f[:-3])
                        except Exception as e:
                            print(e)

    async def on_ready(self):
        self.session: aiohttp.ClientSession = self.http._HTTPClient__session  # type: ignore

    async def run_bot(self):
        try:
            self.pool = await Database(self).initialize_pool()
            await self.load_cogs()
            await super().start(os.environ['DISCORD_TOKEN'], reconnect=True)
        except:
            await self.close()
            raise
