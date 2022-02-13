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

from asyncio import Queue, queues
from contextlib import suppress
from datetime import timedelta
from typing import Any

from disnake import Colour, Embed, HTTPException, Member, Message
from disnake.ext import commands
from humanize import precisedelta

from .pomice import Track
from .pomice.player import Player as PomicePlayer


class PlayerMusic(PomicePlayer):
    """Custom pomice Player class."""
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

        self.queue = Queue()  # type: ignore
        self.controller: Message = None  # type: ignore
        # Set context here so we can send a now playing embed
        self.context: commands.Context = None  # type: ignore
        self.client: commands.Bot = None  # type: ignore
        self.dj: Member = None  # type: ignore
        self.loop: bool = False

    async def do_next(self) -> None:

        if self.loop:
            return await self.play(self._ending_track)

        # Check if theres a controller still active and deletes it
        if self.controller:
            with suppress(HTTPException):
                await self.controller.delete()

    # Queue up the next track, else teardown the player
        try:
            track: Track = self.queue.get_nowait()  # type: ignore
        except queues.QueueEmpty:
            return await self.teardown()

        await self.play(track)

        # Call the controller (a.k.a: The "Now Playing" embed) and check if one exists
        time = timedelta(milliseconds=track.length)
        embed = Embed(
            description=f"**[{track.title}]({track.uri})**\n"
            f":bust_in_silhouette: Autor: **{track.author}**\n"
            f":hourglass: Duração: **{precisedelta(time)}**\n",
            color=Colour.random()
        )  # type: ignore
        embed.set_author(
            name=f"Tocando:",
            icon_url=
            "https://img.icons8.com/external-kiranshastry-lineal-color-kiranshastry/64/000000/external-music-new-year-kiranshastry-lineal-color-kiranshastry.png"
        )
        embed.set_thumbnail(url=track.thumbnail)  # type: ignore
        self.controller = await self.context.send(embed=embed)  # type: ignore

    async def teardown(self) -> None:
        """Clear internal states, remove player controller and disconnect."""
        with suppress((HTTPException), (KeyError)):
            await self.destroy()
            if self.controller:
                await self.controller.delete()
