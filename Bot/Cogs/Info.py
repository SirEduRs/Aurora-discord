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

import platform
from asyncio import sleep
from datetime import datetime
from sys import platform as _platform

import discord
import psutil  # type: ignore
import pytz
from discord import app_commands
from discord.ext import commands
from humanize import i18n, naturalsize, precisedelta  # type: ignore
from stopwatch import Stopwatch as timer  # type: ignore

from Aurora import AuroraClass
from Utils import Paginator, Select
from Utils.Utilidades import permissions

i18n.activate("pt_BR")  # type: ignore


class Info(commands.Cog, name=":newspaper: Informações"):  # type: ignore
    """
    Classe de comandos da categoria: Informações.

    Parameters:
    -----------
    
    bot (AuroraClass): Classe principal do bot.
    """
    def __init__(self, bot: AuroraClass):
        super(Info, self).__init__()
        self.bot = bot

    #==============================Bot=================================

    @commands.command(description="Mostra o ping do bot.")
    async def ping(self, ctx: commands.Context[AuroraClass]):
        dt = discord.utils.utcnow()
        """ Pong! """
        before_ws = int(round(self.bot.latency * 1000, 1))
        pingdb = timer()
        await self.bot.pool.execute('SELECT version();')  # type: ignore
        pingdb.stop()
        Timer = timer()
        mes = await ctx.reply(embed=discord.Embed(title="Calculando o ping..."))
        Timer.stop()
        await sleep(1)
        await mes.edit(embed=discord.Embed(  # type: ignore
            title="PING",
            color=0x3399ff,
            timestamp=dt,
            description=
            f"**<:api:830084663547920464> Ping API:** `{before_ws} ms`\n"
            f"**<:time:830085577096691712> Tempo de Resposta:** `{Timer}`\n"
            f"**<:databasetime:830084663321952278> Tempo de Resposta da database:** `{pingdb}`"
        ).set_footer(text=f"Comando usado por {ctx.author.name}",
                     icon_url=ctx.author.display_avatar))

    @app_commands.command(
        name="ping", description="Mostra o ping do bot."
    )  # type: ignore
    async def ping_slash(self, interaction: discord.Interaction):
        #Create ping command in slash command
        dt = discord.utils.utcnow()
        before_ws = int(round(self.bot.latency * 1000, 1))
        pingdb = timer()
        await self.bot.pool.execute('SELECT version();')  # type: ignore
        pingdb.stop()
        Timer = timer()
        await interaction.response.defer()
        Timer.stop()
        await sleep(1)
        await interaction.edit_original_message(embed=discord.Embed(  # type: ignore
            title="PING",
            color=0x3399ff,
            timestamp=dt,
            description=
            f"**<:api:830084663547920464> Ping API:** `{before_ws} ms`\n"
            f"**<:time:830085577096691712> Tempo de Resposta:** `{Timer}`\n"
            f"**<:databasetime:830084663321952278> Tempo de Resposta da database:** `{pingdb}`"
        ).set_footer(text=f"Comando usado por {interaction.user.name}",
                     icon_url=interaction.user.display_avatar)  # type: ignore
                                                )
        interaction.response.is_done()

    @commands.command(
        description="Mostra o uptime do bot.", aliases=['up', 'ut']
    )
    async def uptime(self, ctx: commands.Context[AuroraClass]):
        uptime = datetime.now() - self.bot.utils["uptime"]
        return await ctx.send(
            embed=discord.Embed(
                timestamp=discord.utils.utcnow(),
                description=
                f"<:time:830085577096691712> Uptime:\n{precisedelta(uptime, format='%0.0f')} ({discord.utils.format_dt(self.bot.utils['uptime'], 'R')})"
            ).set_footer(
                text=f"Comando usado por {ctx.author.name}",
                icon_url=ctx.author.display_avatar
            )
        )

    @commands.command(
        description="Mostra as informações sobre o bot.",
        aliases=['bi', 'info']
    )
    async def botinfo(self, ctx: commands.Context[AuroraClass]):
        users, channel = 0, 0
        cpuper, mem = 0, 0
        uptime = datetime.now() - self.bot.utils["uptime"]  # type: ignore
        for guild in self.bot.guilds:
            users += len(guild.members)
            channel += len(guild.channels)
        proc = psutil.Process()
        with proc.oneshot():
            try:
                mem = proc.memory_full_info()
                cpuper = proc.cpu_percent(1)
            except psutil.AccessDenied:
                pass
        versionsql = await self.bot.pool.fetch(
            'SELECT version();'
        )  # type: ignore
        uptime = precisedelta(uptime, format='%0.0f')  # type: ignore
        commands_bot = await self.bot.fdb.get_document(
            'bot', 'commands'
        )  # type: ignore
        statics = discord.Embed(
            colour=discord.Colour.random(), timestamp=discord.utils.utcnow()
        )
        statics.add_field(
            name=":placard: Servidores:",
            value=f"**{len(self.bot.guilds)}** servidores."
        )
        statics.add_field(
            name="<:members:784373530405634099> Usuários:",
            value=f"**{users}** usuários."
        )
        statics.add_field(name=":hash: Canais:", value=f"**{channel}** canais.")
        statics.add_field(
            name="<:time:830085577096691712> Uptime:", value=uptime
        )
        statics.add_field(
            name=":chart_with_upwards_trend: Comandos Usados:",
            value=f"**{commands_bot['number']}** comandos."
        )
        statics.add_field(
            name="<:serverbt:786565568601260042> Banco de Dados ",
            value=versionsql[0][0][:15]
        )
        statics.add_field(
            name="<:python:821133789610770432> Python Version ",
            value=platform.python_version()
        )
        statics.add_field(
            name="<:discord:825122469278908446> Discord Library (d.py)",
            value=discord.__version__
        )  # type: ignore
        statics.add_field(
            name="<:api:830084663547920464> Ping API:",
            value=f"`{int(round(self.bot.latency * 1000, 1))} ms`"
        )
        statics.add_field(
            name="<:workstation:821131383501357059> Sistema",
            value=f"`{_platform}`"
        )
        statics.add_field(
            name="<:processador:783095365381521420> CPU:",
            value=f"`{cpuper} %`"
        )
        statics.add_field(
            name="<:memram:783095235252977684> RAM: ",
            value=f"`{naturalsize(mem.rss)}`"
        )  # type: ignore
        statics.set_footer(
            text=f"Comando usado por {ctx.author.name}",
            icon_url=ctx.author.display_avatar
        )
        await ctx.send(embed=statics)

    #=================================================================

    #==============================Server=============================
    @commands.command(
        description="Mostra as informações sobre o servidor.",
        aliases=['si', 'server']
    )
    @commands.guild_only()
    async def serverinfo(self, ctx):
        server = ctx.guild
        levels = {
            "none": "Nenhum",
            "low": "Baixo",
            "medium": "Médio",
            "high": "Alto",
            "highest": "Muito Alto"
        }
        verification = str(ctx.guild.verification_level)
        verification = levels[verification]
        bot = 0
        Splash, Banner = None, None
        dt = discord.utils.utcnow()
        date = server.created_at.replace(
            tzinfo=pytz.timezone('America/Sao_Paulo')
        )
        RoleBooster = server.premium_subscriber_role.mention if server.premium_subscriber_role else "Nenhum"
        for member in server.members:
            if member.bot:
                bot += 1
        Embeder = discord.Embed(
            title=server.name, colour=0x3399ff, timestamp=dt
        )
        Embeder.add_field(
            name="<:coroa:784164230005784657> Dono:",
            value=f"`{server.owner.name} ({server.owner.id})`"
        )
        Embeder.add_field(
            name="<a:calendario:784374299540062228> Criado em:",
            value=f"<t:{date:%s}:f>",
            inline=False
        )
        Embeder.add_field(
            name=
            f"<:members:784373530405634099> Total de Membros: `{server.member_count}`",
            value=
            f"├─ :bust_in_silhouette: Pessoas: `{server.member_count - bot}`\n"
            f"└─ :robot: Bots: `{bot}`",
            inline=False
        )
        Embeder.add_field(
            name="<:role:851508921612763157> Total de cargos:",
            value=f"`{len(server.roles)}`"
        )
        Embeder.add_field(
            name=
            f"<a:booster:784171831380672522> Nitro Boost: `Nível {server.premium_tier}`",
            value=
            f"├─ <a:nitrobooster:784174508881870849> Nitro Boosters: `{server.premium_subscription_count}`\n"
            f"└─ :rocket: Cargo Booster: {RoleBooster}",
            inline=False
        )
        Embeder.add_field(
            name="<:level:784374991437299712> Level de Verificação: ",
            value=f"`{verification}`",
            inline=False
        )
        Embeder.set_thumbnail(url=server.icon.url)
        Icon = discord.Embed(
            title="Icon", colour=discord.Colour.random(), timestamp=dt
        )
        Icon.set_image(url=server.icon.url)
        viewer = []
        viewer.append(Embeder), viewer.append(Icon)
        if server.banner:
            Banner = discord.Embed(
                title="Banner", colour=discord.Colour.random(), timestamp=dt
            )
            Banner.set_image(url=server.banner)
            Banner.set_footer(
                text=f"Comando usado por {ctx.author.name}",
                icon_url=ctx.author.display_avatar
            )
            viewer.append(Banner)
        if server.splash:
            Splash = discord.Embed(
                title="Splash", colour=discord.Colour.random(), timestamp=dt
            )
            Splash.set_image(url=server.splash)
            Splash.set_footer(
                text=f"Comando usado por {ctx.author.name}",
                icon_url=ctx.author.display_avatar
            )
            viewer.append(Splash)

        Embeder.set_footer(
            text=f"Comando usado por {ctx.author.name}",
            icon_url=ctx.author.display_avatar
        )
        Icon.set_footer(
            text=f"Comando usado por {ctx.author.name}",
            icon_url=ctx.author.display_avatar
        )
        await ctx.send(
            embed=Embeder, view=Paginator(viewer, ctx_id=ctx.author.id)
        )

    @commands.command(
        name="roleinfo",
        usage="roleinfo <ID do cargo| Menção | nome>",
        description="Mostra as informações sobre um cargo.",
        aliases=['role']
    )
    @commands.guild_only()
    async def _role(self, ctx, *, role):
        members = []
        ress = None
        perms = []
        roles = []

        role = role.replace("<", "")
        role = role.replace(">", "")
        role = role.replace("&", "")
        role = role.replace("@", "")
        dt = discord.utils.utcnow()

        class Viewer(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=60.0)

            async def interaction_check(self, interaction):
                if interaction.user.id != ctx.author.id:
                    await interaction.response.send_message(
                        content="Você não pode interagir aqui !",
                        ephemeral=True
                    )
                    return False
                else:
                    return True

        for r in ctx.guild.roles:
            roles.append(r.name)
        try:
            if len(role) > 16 and int(role):
                role = int(role)
                role = ctx.guild.get_role(role)
        except ValueError:
            pass
        if isinstance(role, str):
            ri, ri2 = {"name": [], "id": []}, {"name": [], "id": []}
            te = [k for k in roles if role in k]
            attempt = [
                [k for k in roles if role in k],  # Tenta normal 
                [k for k in roles
                 if role.title() in k],  #Tenta com a string em title()
                [k for k in roles
                 if role.upper() in k]  #Tenta com a string em caps
            ]
            if len(attempt[0]) == 1:
                role = discord.utils.get(ctx.guild.roles, name=attempt[0][0])
            elif len(attempt[0]) < 1:
                if len(attempt[1]) == 1:
                    role = discord.utils.get(
                        ctx.guild.roles, name=attempt[1][0]
                    )
                elif len(attempt[1]) < 1:
                    if len(attempt[2]) == 1:
                        role = discord.utils.get(
                            ctx.guild.roles, name=attempt[2][0]
                        )
                    else:
                        for r in attempt[2]:
                            rl = discord.utils.get(ctx.guild.roles, name=r)
                            if r == rl.name:
                                if len(ri["name"]) > 24:
                                    ri2["name"].append(r)
                                    ri2["id"].append(rl.id)
                                else:
                                    ri["name"].append(r)
                                    ri["id"].append(rl.id)
                        if len(ri["name"]) < 1:
                            return await ctx.send(
                                embed=discord.Embed(
                                    colour=0x3399ff,
                                    description=
                                    "Não encontrei nenhum cargo com esse nome."
                                )
                            )
                        else:
                            view = Viewer()
                            select = Select(ri, ctx.guild)
                            view.add_item(select)
                            if len(ri2["name"]) > 0:
                                select2 = Select(ri2, ctx.guild)
                                view.add_item(select2)
                            c = await ctx.send(
                                f"Encontrei esses seguintes cargos:\n",
                                #f">>> {ne.join(ri[:5])} \nE muitos outros..." if len(ri) > 5 else f"Encontrei esses seguintes cargos:\n>>> {ne.join(ri)}"
                                view=view
                            )
                            b = await view.wait()
                            if b is True:
                                if view.is_finished() is False:
                                    return await c.edit(
                                        content=None,
                                        embed=discord.Embed(
                                            colour=0x3399ff,
                                            description=
                                            f'{self.bot.utils["emoji"]["cancel"]} Comando cancelado !'
                                        ),
                                        view=None
                                    )

                else:
                    for r in attempt[1]:
                        rl = discord.utils.get(ctx.guild.roles, name=r)
                        if r == rl.name:
                            if len(ri["name"]) > 24:
                                ri2["name"].append(r), ri2["id"].append(rl.id)
                            else:
                                ri["name"].append(r), ri["id"].append(rl.id)
                    if len(ri["name"]) < 1:
                        return await ctx.send(
                            content=None,
                            embed=discord.Embed(
                                colour=0x3399ff,
                                description=
                                "Não encontrei nenhum cargo com esse nome."
                            )
                        )
                    else:
                        view, select = Viewer(), Select(ri, ctx.guild)
                        view.add_item(select)
                        if len(ri2["name"]) > 0:
                            select2 = Select(ri2, ctx.guild)
                            view.add_item(select2)
                        e = await ctx.send(
                            f"Encontrei esses seguintes cargos:\n", view=view
                        )
                        f = await view.wait()
                        if f is True:
                            if view.is_finished() is False:
                                return await e.edit(
                                    content=None,
                                    embed=discord.Embed(
                                        colour=0x3399ff,
                                        description=
                                        f'{self.bot.utils["emoji"]["cancel"]} Comando cancelado !'
                                    ),
                                    view=None
                                )
            else:
                for r in te:
                    rl = discord.utils.get(ctx.guild.roles, name=r)
                    if r == role:
                        ress, role = r, discord.utils.get(
                            ctx.guild.roles, name=r
                        )
                    if r == rl.name:
                        if len(ri["name"]) > 24:
                            ri2["name"].append(r)
                            ri2["id"].append(rl.id)
                        else:
                            ri["name"].append(r)
                            ri["id"].append(rl.id)
                if len(ri["name"]) < 1:
                    return await ctx.send(
                        content=None,
                        embed=discord.Embed(
                            colour=0x3399ff,
                            description=
                            "Não encontrei nenhum cargo com esse nome."
                        )
                    )
                else:
                    ne = '\n'
                    if ress is None:
                        view = Viewer()
                        select = Select(ri, ctx.guild)
                        view.add_item(select)
                        view.add_item(Select(ri2, ctx.guild)
                                     ) if len(ri2["name"]) > 0 else None
                        g = await ctx.send(
                            f"Encontrei esses seguintes cargos:\n", view=view
                        )
                        h = await view.wait()
                        if h is True:
                            if view.is_finished() is False:
                                return await g.edit(
                                    content=None,
                                    embed=discord.Embed(
                                        colour=0x3399ff,
                                        description=
                                        f'{self.bot.utils["emoji"]["cancel"]} Comando cancelado !'
                                    ),
                                    view=None
                                )

        if role:
            [members.append(re.mention) for re in role.members], [
                perms.append(permissions(pe[0]))
                for pe in role.permissions if pe[1] is True
            ]
            check = {True: "Sim", False: "Não"}
            men, botm, both = check[role.mentionable
                                   ], check[role.is_bot_managed()
                                           ], check[role.hoist]
            r, g, b = role.color.to_rgb()
            date = role.created_at.replace(
                tzinfo=pytz.timezone('America/Sao_Paulo')
            )
            Embed = discord.Embed(
                colour=role.color,
                timestamp=dt,
                description=f"⦂⦂ **ID**: `{role.id}`\n"
                f"⦂⦂ **Nome do cargo**: `{role.name}`\n"
                f"⦂⦂ **Cor Hex**: `{str(role.color).upper()}`\n"
                f"⦂⦂ **Cor R.G.B**: `{r,g,b}`\n"
                f"⦂⦂ **Criada em**: <t:{date:%s}:f>\n"
                f"⦂⦂ **Posição**: `{role.position}`\n"
                f"⦂⦂ **Mencionável**: `{men}`\n"
                f"⦂⦂ **É de um BOT ?** `{botm}`\n"
                f"⦂⦂ **É destacada ?** `{both}`\n"
                f"⦂⦂ **Permissões**:\n `{', '.join(perms) or 'Nenhuma'}`\n"
                f"⦂⦂ **Membros**:\n {', '.join(members) if len(members) <= 15 and len(members) > 0 else len(members)}"
            ).set_footer(
                text=f"Comando usado por {ctx.author.name}",
                icon_url=ctx.author.display_avatar
            )
            return await ctx.send(embed=Embed)
        else:
            return await ctx.send(
                embed=discord.Embed(
                    colour=0x3399ff,
                    description="Não consegui encontrei nenhum cargo..."
                )
            )

    #==================================================================


async def setup(bot: AuroraClass):
    await bot.add_cog(Info(bot))
    print(
        "\033[1;92m[Cog Load]\033[1;94m Information\033[1;96m carregado com sucesso !"
    )
