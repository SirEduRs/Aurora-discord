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

from io import BytesIO

import disnake
import humanize  # type: ignore
from disnake.ext import commands
from disnake.ext.commands import errors  # type: ignore

from Aurora import AuroraClass
from Utils import Database
from Utils.Utilidades import EmbedDefault as Embed
from Utils.Utilidades import permissions


class Errors(commands.Cog):
    def __init__(self, bot: AuroraClass):
        super(Errors, self).__init__()
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return

        cog = ctx.cog
        db = Database(self.bot)
        getprefix = await db.get_prefix(ctx.message)
        erro = getattr(error, 'original', error)
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        if isinstance(erro, commands.CommandOnCooldown):
            timer = humanize.precisedelta(error.retry_after)
            return await Embed(
                ctx, f"Calma, espere {timer} para usar o comando novamente !"
            )

        elif isinstance(erro, commands.MissingRequiredArgument):
            return await Embed(
                ctx,
                f"Você esqueceu de algo para esse comando funcionar, veja `{getprefix}help {ctx.command.name}` !"
            )

        elif isinstance(erro, errors.NoPrivateMessage):
            return await Embed(
                ctx, "Esse comando só pode ser usado em um servidor !"
            )

        elif isinstance(erro, errors.CommandNotFound):
            return

        elif isinstance(erro, errors.NotOwner):
            return await Embed(
                ctx,
                f"{self.bot.utils['emoji']['owner']} Somente meu desenvolvedor pode usar esse comando !"
            )

        elif isinstance(erro, errors.MemberNotFound):
            return await Embed(
                ctx, "Desculpe, mas não consegui encontrar esse membro..."
            )

        elif isinstance(erro, errors.MissingPermissions):
            perms = error.missing_permissions
            if len(perms) == 1:
                return await Embed(
                    ctx,
                    f"Você precisa da permissão `{permissions(perms[0])}` para executar esse comando !"
                )
            elif len(perms) > 1:
                a = ', '.join(permissions(perms))
                return await Embed(
                    ctx,
                    f"Você precisa das permissões {a} para executar esse comando."
                )
        elif isinstance(erro, errors.BotMissingPermissions):
            perms = error.missing_permissions
            if len(perms) == 1:
                return await Embed(
                    ctx,
                    f"Eu preciso da permissão `{permissions(perms[0])}` para executar esse comando !"
                )
            elif len(perms) > 1:
                a = ', '.join(permissions(perms))
                return await Embed(
                    ctx,
                    f"Eu preciso das permissões `{a}` para executar esse comando."
                )

        elif isinstance(erro, errors.ChannelNotFound):
            return await Embed(
                ctx,
                f"Eu não encontrei o canal **{error.argument}** neste servidor !"
            )

        CHANNEL_LOG = await self.bot.fetch_channel(866314136534253618)
        lines = str(error)
        if ctx.command:
            if len(lines) > 1500:
                result = BytesIO(lines.encode('utf-8'))
                file = disnake.File(fp=result, filename=f"error.txt")
                EMBED = disnake.Embed(colour=disnake.Colour.red())
                EMBED.description = f"_Comando_: **`{ctx.command.name}`**\n" \
                     f"_Usuário_: **`{ctx.author}`**\n"
                await CHANNEL_LOG.send(embed=EMBED)
                await CHANNEL_LOG.send(file=file)
            else:
                EMBED = disnake.Embed(colour=disnake.Colour.red())
                EMBED.description = f"_Comando_: **`{ctx.command.name}`**\n" \
                     f"_Usuário_: **`{ctx.author}`**\n" \
                     f"```py\n{lines}```"
                await CHANNEL_LOG.send(embed=EMBED)

        else:
            if len(lines) > 1500:
                result = BytesIO(lines.encode('utf-8'))
                file = disnake.File(fp=result, filename=f"error.txt")
                EMBED = disnake.Embed(colour=disnake.Colour.red())
                EMBED.description = f"_Usuário_: **`{ctx.author}`**\n"
                await CHANNEL_LOG.send(embed=EMBED)
                await CHANNEL_LOG.send(file=file)
            else:
                EMBED = disnake.Embed(colour=disnake.Colour.red())
                EMBED.description = f"_Usuário_: **`{ctx.author}`**\n" \
                     f"```py\n{lines}```"
                await CHANNEL_LOG.send(embed=EMBED)

        raise error


def setup(bot: AuroraClass):
    bot.add_cog(Errors(bot))
    print(
        "\033[1;95m[Events Load]\033[1;94m Error Event\033[1;96m carregado com sucesso !"
    )
