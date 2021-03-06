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

from typing import Tuple

import discord
from discord.ext import commands

from Aurora import AuroraClass
from Utils import Paginator
from Utils.Utilidades import split_list


class UtilityCog(commands.Cog, name=":toolbox: Utilidades"):  # type: ignore
    """
    Classe de comandos da categoria: Utilidades.

    Parameters:
    -----------
    
    bot (AuroraClass): Classe principal do bot.
    """
    def __init__(self, bot: commands.Bot):
        super(UtilityCog, self).__init__()
        self.bot = bot

    @commands.command(
        name="emojis", description="Mostra todos os emojis do servidor."
    )
    @commands.guild_only()
    async def _emojis(self, ctx: commands.Context[commands.Bot]):
        guild_emojis: Tuple[discord.Emoji] = ctx.guild.emojis
        list_embeds = Paginator.paginate_emojis(
            split_list(guild_emojis, 25), ctx.guild
        )
        await ctx.send(
            embed=list_embeds[0], view=Paginator(list_embeds, ctx.author.id)
        )  # type: ignore


async def setup(bot: AuroraClass):
    await bot.add_cog(UtilityCog(bot))
