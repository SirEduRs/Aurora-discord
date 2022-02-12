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

import os
import re
import time
import traceback
from io import BytesIO

import disnake
from disnake import Colour, Embed
from disnake.ext import commands

from Aurora import AuroraClass
from Utils.Utilidades import pretty


class ComandosOwnerBot(
    commands.Cog, name="<:coroa:784164230005784657> Developer"
):  # type: ignore
    def __init__(self, bot: AuroraClass):
        super(ComandosOwnerBot, self).__init__()
        self.bot = bot

    @commands.command(
        name="reload",
        aliases=['restart'],
        description="Reinicia algum cog do bot."
    )
    @commands.is_owner()
    async def _reload(
        self, ctx: commands.Context[AuroraClass], *, extension: str = None
    ):
        if extension is None:
            desc = ""
            channel = await self.bot.fetch_channel(866314136534253618)
            for ext in list(self.bot.extensions):
                print(ext)
                if ext != "jishaku":
                    try:
                        self.bot.reload_extension(ext)
                    except Exception as e:
                        desc += f"<:cancelar:858707313452122162> `{ext}`\n"
                        await channel.send(embed=disnake.Embed(  # type: ignore
                            colour=0x3399ff,
                            description=f"```py\n{e}```"))
                    else:
                        desc += f"<:confirmar:858707288105287720> `{ext}`\n"

            await ctx.send(embed=disnake.Embed(  # type: ignore
                colour=disnake.Colour.random(),
                title="Modules Reloades !",
                description=desc))
        else:
            try:
                self.bot.reload_extension(f"Cogs.{extension}")
            except commands.ExtensionNotFound as e:
                await ctx.send(
                    '<:error:822893520678682644> `Extensão não encontrada !`'
                )  # type: ignore
            else:
                await ctx.send(
                    f'<:restart:822891197529063446> `Extensão {extension} reiniciada`'
                )  # type: ignore

    @commands.command(
        name="dbeval",
        aliases=['sql', 'evaldb'],
        description="Executa alguma query no PostgresSQL."
    )
    @commands.is_owner()
    async def _dbeval(
        self, ctx: commands.Context[AuroraClass], *, query: str = ''
    ):
        arq = None

        class Error(disnake.ui.View):
            def __init__(self):
                super(Error, self).__init__()

            async def interaction_check(self, interaction: disnake.Interaction):
                if interaction.user.id != ctx.author.id:  # type: ignore
                    return False
                else:
                    return True

            @disnake.ui.button(
                emoji="<:trash:822156106683121694>",
                style=disnake.ButtonStyle.red
            )  # type: ignore
            async def trasherr(
                self, button: disnake.Button, interaction: disnake.Interaction
            ):
                if arq:
                    await archerrdb.delete()
                for c in self.children:  # type: ignore
                    c.disabled = True  # type: ignore
                await alerr.edit(
                    embed=Embed(
                        title=f"<:error:822893520678682644> **Eval fechado !**",
                        colour=Colour(0x3399ff)
                    ),
                    view=self
                )  # type: ignore

        class Result(disnake.ui.View):
            def __init__(self):
                super(Result, self).__init__()

            async def interaction_check(self, interaction: disnake.Interaction):
                if interaction.user.id != ctx.author.id:  # type: ignore
                    return False
                else:
                    return True

            @disnake.ui.button(
                emoji="<:trash:822156106683121694>",
                style=disnake.ButtonStyle.red
            )  # type: ignore
            async def trashres(
                self, button: disnake.Button, interaction: disnake.Interaction
            ):
                if arq:
                    await arch.delete()
                for b in self.children:  # type: ignore
                    b.disabled = True  # type: ignore
                await db.edit(
                    embed=Embed(
                        title=f"<:result:822893531491336252> **Eval fechado !**",
                        colour=Colour(0x3399ff)
                    ),
                    view=self
                )  # type: ignore

            @disnake.ui.button(
                emoji="<:result:822893531491336252>",
                style=disnake.ButtonStyle.green
            )  # type: ignore
            async def resultr(
                self, button: disnake.Button, interaction: disnake.Interaction
            ):
                for chil in self.children:  # type: ignore
                    chil.disabled = True  # type: ignore
                await db.edit(view=self)  # type: ignore

        if query is not None:
            if not query.endswith(';'):
                query += ';'
            try:
                await self.bot.pool.execute(query)  # type: ignore
            except Exception:
                err = str(traceback.format_exc())
                ErrorEmbed = Embed(colour=Colour(0x3399ff))
                Check = ["USERM", "PASSM", "DISCORD_TOKEN", "DSN"]
                for c in Check:
                    err = re.sub(os.environ[c], "[CENSURADO]", err)
                if len(err) > 1024:
                    arq = True
                    ErrorEmbed.add_field(
                        name='<:error:822893520678682644> Erro:',
                        value=
                        f'```\nErro foi muito grande, enviei um arquivo com o erro.```',
                        inline=False
                    )
                else:
                    ErrorEmbed.add_field(
                        name='<:error:822893520678682644> Erro:',
                        value=f'```\n{err}```',
                        inline=False
                    )
                if arq:
                    archerrdb = await ctx.send(
                        file=disnake.File(
                            filename='error.py',
                            fp=BytesIO(err.encode('utf-8'))
                        )
                    )  # type: ignore
                alerr = await ctx.reply(
                    embed=ErrorEmbed, view=Error(), mention_author=False
                )
                time.sleep(1)
            else:
                queryembed = Embed(colour=Colour(0x3399ff))
                queryembed.add_field(
                    name='<:code:822893241443155969> Query:',
                    value=f'```sql\n{query}```'
                )
                if 'select' in query.lower():
                    resultr = []
                    for record in await self.bot.pool.fetch(
                        query
                    ):  # type: ignore
                        try:
                            resultr.append(dict(record))  # type: ignore
                        except ValueError:
                            resultr.append(tuple(record))  # type: ignore
                    resultr = tuple(resultr)  # type: ignore
                    if len(resultr) == 1:  # type: ignore
                        result = pretty(resultr[0])
                    elif len(resultr) > 1:  # type: ignore
                        result = pretty(resultr)
                    else:
                        result = "Nothing..."
                    if len(result) > 1024:
                        arq = True
                        queryembed.add_field(
                            name='<:result:822893531491336252> Resultado:',
                            value=
                            f'```\nResultado foi muito grande, enviei um arquivo com o resultado.```',
                            inline=False
                        )
                    else:
                        queryembed.add_field(
                            name='<:result:822893531491336252> Resultado:',
                            value=f'```py\n{result}```',
                            inline=False
                        )
                    if arq:
                        arch = await ctx.send(
                            file=disnake.File(
                                filename='result.py',
                                fp=BytesIO(result.encode('utf-8'))
                            )
                        )  # type: ignore
                    db = await ctx.send(
                        embed=queryembed, view=Result()
                    )  # type: ignore
        else:
            await ctx.send(
                embed=disnake.Embed(
                    colour=0x3399ff,
                    description="Você precisa inserir a query para eu executar !"
                )
            )  # type: ignore


def setup(bot: AuroraClass):
    bot.add_cog(ComandosOwnerBot(bot))
    print(
        "\033[1;92m[Cog Load]\033[1;94m Owner\033[1;96m carregado com sucesso !"
    )
