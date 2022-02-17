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

import disnake
from disnake.ext import commands

from Aurora import AuroraClass
from Utils import Database, SelectLogs, ViewSimple


class Config(commands.Cog, name=":gear: Configuração"):  # type: ignore
    """
    Classe de comandos da categoria: Configuração.

    Parameters:
    -----------

    bot (AuroraClass): Classe principal do bot.
    """
    def __init__(self, bot: AuroraClass):
        self.bot = bot

    @commands.command(
        name="setprefix",
        usage="setprefix <Prefixo novo>",
        description="Troca o prefixo do bot no servidor.",
        aliases=["change_prefix", "prefix"]
    )
    @commands.has_guild_permissions(manage_guild=True)
    async def _prefix(self, ctx, prefixnew="a."):
        db = Database(self.bot)
        await db.update_prefix(ctx.guild.id, prefixnew)
        if prefixnew != "a.":
            a = disnake.Embed(
                description=f"Prefixo alterado !\nNovo prefixo: {prefixnew}",
                colour=disnake.Colour.random()
            )
            await ctx.send(embed=a)
        else:
            ab = disnake.Embed(
                description=f"Prefixo resetado !\nPrefixo: `{prefixnew}`",
                colour=disnake.Colour.random()
            )
            await ctx.send(embed=ab)

    @commands.group(pass_context=True, invoke_without_command=True)
    @commands.has_guild_permissions(manage_guild=True)
    async def config(self, ctx):
        if ctx.author.id != self.bot.owner_id:
            return await ctx.send(
                embed=disnake.Embed(
                    colour=disnake.Colour.random(),
                    description="Comando em manutenção !!"
                )
            )
        db = Database(self.bot)
        Embed = disnake.Embed(
            title="Configurações dos logs", colour=disnake.Colour.random()
        )
        mes, meb, mod = None, None, None
        Logs = {"name": [], "log": []}
        mes = await db.get_log(ctx.guild.id, "message_log")
        meb = await db.get_log(ctx.guild.id, "member_log")
        mod = await db.get_log(ctx.guild.id, "mod_log")
        Embed.description = f"Logs de mensagem: {mes.mention if mes else self.bot.utils['emoji']['cancel']}\n" \
             f"Logs de membro: {meb.mention if meb else self.bot.utils['emoji']['cancel']}\n" \
             f"Logs de moderação: {mod.mention if mod else self.bot.utils['emoji']['cancel']}\n"

        Logs["name"].append("📄 Logs de Mensagem"
                           ), Logs["log"].append("message_log")
        Logs["name"].append("👤 Logs de Membro"
                           ), Logs["log"].append("member_log")
        Logs["name"].append("⚙️ Logs de Moderação"
                           ), Logs["log"].append("mod_log")
        View = ViewSimple(ctx.author.id)
        View.add_item(SelectLogs(Logs, ctx, self.bot))
        await ctx.send(embed=Embed, view=View)


def setup(bot: AuroraClass):
    bot.add_cog(Config(bot))
    print(
        "\033[1;92m[Cog Load]\033[1;94m Config\033[1;96m carregado com sucesso !"
    )
