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

import secrets
from datetime import datetime

import disnake
import pytz
from disnake.ext import commands

from Aurora import AuroraClass
from Utils import Database
from Utils.Utilidades import pastebin_post


class On_MessageEvents(commands.Cog):
    """docstring for On_MessageEvent"""
    def __init__(self, bot: AuroraClass):
        super(On_MessageEvents, self).__init__()
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if (f'<@{self.bot.user.id}>' == message.content
           ) or (f'<@!{self.bot.user.id}>' == message.content):
            db = Database(self.bot)
            getprefix = await db.get_prefix(message)
            embed = disnake.Embed(
                colour=disnake.Colour.random(),
                description=
                f"Olá {message.author.mention} !\nMeu prefixo nesse servidor é: `{getprefix}`."
            )
            embed.set_footer(
                text=f"Para saber todos os meus comandos, use {getprefix}help"
            )
            embed.set_thumbnail(url=self.bot.user.avatar.url)
            await message.channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message: disnake.Message):
        db = Database(self.bot)
        log = await db.get_log(message.guild.id, "message_log")
        getprefix = await db.get_prefix(message)
        dt = datetime.utcnow().astimezone(pytz.timezone('America/Sao_Paulo')
                                         ).strftime("%d/%m/%Y às %H:%M")
        if log:
            if message.author.bot is False:
                if not message.content.startswith(f"{getprefix}login"):
                    if not message.channel.id in [
                        819586447627255878, 760914893762461756
                    ]:
                        Embed = disnake.Embed(
                            title="Mensagem deletada !",
                            description=
                            f"**Autor**: {message.author} ({message.author.id})\n"
                            f"**Canal**: {message.channel.mention} ({message.channel.id})\n"
                            f"**Mensagem**: \n```{message.content}```\n",
                            colour=disnake.Colour.random()
                        )
                        Embed.set_thumbnail(url=message.author.avatar.url)
                        Embed.set_footer(
                            text=f"{dt}",
                            icon_url=
                            "https://img.icons8.com/plasticine/100/000000/clock--v1.png"
                        )
                        await log.send(embed=Embed)

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        text = ""
        db = Database(self.bot)
        log = await db.get_log(messages[0].guild.id, "message_log")
        dt = datetime.utcnow().astimezone(pytz.timezone('America/Sao_Paulo')
                                         ).strftime("%d/%m/%Y às %H:%M")
        if log:
            for message in messages:
                if message.author.bot is False:
                    dts = message.created_at.astimezone(
                        pytz.timezone('America/Sao_Paulo')
                    ).strftime("%d/%m/%Y %H:%M")
                    text += f"[{dt}] {message.author}: {message.content}\n"
            a = secrets.token_urlsafe(4)
            b = pastebin_post(f"{messages[0].guild.name} - {a}", text)
            Embed = disnake.Embed(
                title="Mensagens deletadas !",
                description=f"**Canal**: {messages[0].channel.mention}\n"
                f"Link para as mensagens [aqui]({b.decode('utf-8')}).",
                colour=disnake.Colour.random()
            )
            dt = datetime.utcnow().astimezone(
                pytz.timezone('America/Sao_Paulo')
            ).strftime("%d/%m/%Y às %H:%M")
            Embed.set_thumbnail(url=messages[0].guild.icon.url)
            Embed.set_footer(
                text=dt,
                icon_url=
                "https://img.icons8.com/plasticine/100/000000/clock--v1.png"
            )
            await log.send(embed=Embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        db = Database(self.bot)
        log = await db.get_log(after.guild.id, "message_log")
        dt = datetime.utcnow().astimezone(pytz.timezone('America/Sao_Paulo')
                                         ).strftime("%d/%m/%Y às %H:%M")
        if log:
            if before.author.bot is False:
                if before.content != after.content:
                    Embed = disnake.Embed(
                        title="Mensagem editada !",
                        description=
                        f"**Autor**: {after.author} ({after.author.id})\n"
                        f"**Canal**: {after.channel.mention} ({after.channel.id})\n"
                        f"**Mensagem Antiga**: \n```{before.content}```\n"
                        f"**Mensagem Atual**: \n```{after.content}```\n",
                        colour=disnake.Colour.random()
                    )
                    Embed.set_thumbnail(url=after.author.avatar.url)
                    Embed.set_footer(
                        text=f"{dt}",
                        icon_url=
                        "https://img.icons8.com/plasticine/100/000000/clock--v1.png"
                    )
                    await log.send(embed=Embed)


def setup(bot: AuroraClass):
    bot.add_cog(On_MessageEvents(bot))
    print(
        "\033[1;95m[Events Load]\033[1;94m Message Event\033[1;96m carregado com sucesso !"
    )
