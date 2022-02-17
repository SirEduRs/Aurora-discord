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

from datetime import datetime

import disnake
import pytz
from disnake import Embed
from disnake.ext import commands
from disnake.ext.commands import Command

from Aurora import AuroraClass
from Utils.Database import Database


class Help(commands.Cog, name=":clipboard: Ajuda"):
    """
    Classe de comandos da categoria: Ajuda.

    Parameters:
    -----------
    
    bot (AuroraClass): Classe principal do bot.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="help",
        aliases=['ajuda'],
        description="Mostra o menu de ajuda do bot."
    )
    async def _help(
        self, ctx: commands.Context[AuroraClass], command: str = None
    ):
        db = Database(self.bot)
        getprefix = await db.get_prefix(ctx.message)
        dt = datetime.utcnow().astimezone(pytz.timezone('America/Sao_Paulo')
                                         ).strftime("%d/%m/%Y às %H:%M")
        if command:
            command: Command = self.bot.get_command(command)
            if command:
                if not command.cog_name in [
                    'Integration', 'Jishaku',
                    '<:coroa:784164230005784657> Developer'
                ]:
                    embed = Embed(
                        title=
                        f"Informações sobre o comando: `{command.qualified_name}`",
                        colour=0x3399ff,
                    )
                    embed.add_field(
                        name=":name_badge: Nome:", value=command.qualified_name
                    )
                    if command.usage:
                        embed.add_field(
                            name=":page_facing_up: Como usar:",
                            value=command.usage
                        )
                    if command.aliases:
                        embed.add_field(
                            name=":book: Alternativas:",
                            value=(', '.join(command.aliases)),
                            inline=False
                        )
                    if command.description:
                        embed.set_footer(
                            text=f"{command.description}",
                            icon_url=
                            "https://img.icons8.com/plasticine/100/000000/info-squared.png"
                        )
                    await ctx.send(embed=embed)
            else:
                await ctx.send(
                    embed=disnake.Embed(
                        colour=disnake.Colour.random(),
                        description=
                        f"Não encontrei nenhum comando com esse nome !!"
                    ).set_footer(
                        text=f"Comando usado por {ctx.author.name} ➜ {dt}",
                        icon_url=ctx.author.avatar.url
                    )
                )
        else:
            page = Embed(
                title=f":book: Menu de Ajuda",
                colour=0x3399ff,
                description=
                f"Seja bem-vindo ao meu menu de ajuda com todos os comandos que eu possuo. Aqui uma dica para facilitar o uso:\n"
                f"Para saber as informações sobre algum comando, use: `{getprefix}help <comando>`."
            ).set_footer(
                text=
                "< > - Parâmetros obrigatórios. | [ ] - Parâmetros opcionais."
            )
            page.set_thumbnail(
                url="https://img.icons8.com/plasticine/100/000000/help.png"
            )
            for cog in self.bot.cogs:
                if not cog in ['Integration', 'Jishaku']:
                    if ctx.author.id == self.bot.owner_id:
                        c = self.bot.get_cog(cog)
                        commands = [b.qualified_name for b in c.walk_commands()]
                        if commands:
                            if len(commands) < 2:
                                page.add_field(
                                    name=cog, value=f"`{', '.join(commands)}`"
                                )
                            else:
                                page.add_field(
                                    name=cog,
                                    value=f"`{', '.join(commands)}`",
                                    inline=False
                                )
                    else:
                        if not cog in ['<:coroa:784164230005784657> Developer']:
                            c = self.bot.get_cog(cog)
                            commands = [
                                b.qualified_name for b in c.walk_commands()
                            ]
                            if commands:
                                if len(commands) < 2:
                                    page.add_field(
                                        name=cog,
                                        value=f"`{', '.join(commands)}`"
                                    )
                                else:
                                    page.add_field(
                                        name=cog,
                                        value=f"`{', '.join(commands)}`",
                                        inline=False
                                    )

            await ctx.send(embed=page)


def setup(bot: AuroraClass):
    bot.add_cog(Help(bot))
    print(
        "\033[1;92m[Cog Load]\033[1;94m Help\033[1;96m carregado com sucesso !"
    )
