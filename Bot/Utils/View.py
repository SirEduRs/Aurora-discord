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

import asyncio
import json
from typing import TYPE_CHECKING, Any, Callable, Dict, List, TypeAlias

import disnake
import pytz
from disnake.ext import commands

from .Utilidades import permissions

if TYPE_CHECKING:
    from Aurora import AuroraClass
    Aurora: TypeAlias = AuroraClass
else:
    Aurora: TypeAlias = None

with open("Utils/Archives/emojis.json") as emojis:
    _emoji = json.loads(emojis.read())


class Compact:
    def __init__(self, lista: Dict[Any, Any]):
        self.list = lista
        super().__init__()
        self.value = None
        self.name: List[str] = []
        self.icon: List[str] = []
        self.id: List[int] = []

    def returnlist(self, typev: str):
        if typev == "role":
            for key in self.list:
                if key == "name":
                    for c in self.list[key]:
                        self.name.append(c)
                if key == "id":
                    for a in self.list[key]:
                        self.id.append(a)
            return zip(self.name, self.id)
        elif typev == "log":
            for key in self.list:
                if key == "name":
                    for c in self.list[key]:
                        self.name.append(c)
                if key == "log":
                    for a in self.list[key]:
                        self.id.append(a)
            return zip(self.name, self.id)
        else:
            for key in self.list:
                if key == "name":
                    for c in self.list[key]:
                        self.name.append(c)
                if key == "id":
                    for a in self.list[key]:
                        self.id.append(a)
                if key == "icon":
                    for b in self.list[key]:
                        self.icon.append(b)
            return zip(self.name, self.id, self.icon)


class Select(disnake.ui.Select):  # type: ignore
    def __init__(self, role: Dict[Any, Any], guild: disnake.Guild):
        self.role = Compact(role).returnlist("role")
        self.guild = guild
        self.value = None
        super().__init__(
            placeholder="Escolha o cargo:",
            min_values=1,
            max_values=1,
            options=[
                disnake.SelectOption(
                    label=f"ID: {idr}", description=name, value=name
                ) for name, idr in self.role
            ]
        )  # type: ignore

    async def callback(self, interaction: disnake.MessageInteraction):
        role = disnake.utils.get(
            self.guild.roles, name=interaction.values[0]
        )  # type: ignore
        if role:
            members: List[str] = list()
            perms: List[str] = list()
            dt = disnake.utils.utcnow()

            [members.append(re.mention) for re in role.members]  # type: ignore
            [
                perms.append(permissions(pe[0]))
                for pe in role.permissions if pe[1] is True
            ]  # type: ignore
            check = {True: "Sim", False: "Não"}

            men, botm, both = check[role.mentionable
                                   ], check[role.is_bot_managed()
                                           ], check[role.hoist]
            r, g, b = role.color.to_rgb()
            date = role.created_at.replace(
                tzinfo=pytz.timezone('America/Sao_Paulo')
            )
            Embed = disnake.Embed(
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
                text=f"Comando usado por {interaction.user.name}",
                icon_url=interaction.user.display_avatar
            )
            return await interaction.response.edit_message(
                content=None, embed=Embed, view=None
            )  # type: ignore


class ViewConfirm(disnake.ui.View):
    def __init__(self, author_id: int):
        self.author_id = author_id
        super().__init__()
        self.value: bool = False

    async def interaction_check(self, interaction: disnake.MessageInteraction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                content="Você não pode interagir aqui !", ephemeral=True
            )  # type: ignore
            return False
        else:
            return True

    @disnake.ui.button(
        emoji=_emoji["confirm"], style=disnake.ButtonStyle.green
    )  # type: ignore
    async def _confirm(self, _):
        self.value = True
        self.stop()

    @disnake.ui.button(
        emoji=_emoji["cancel"], style=disnake.ButtonStyle.red
    )  # type: ignore
    async def _cancel(self, _):
        self.value = False
        self.stop()


class ViewSimple(disnake.ui.View):
    def __init__(self, author_id: int):
        self.author_id = author_id
        super(ViewSimple, self).__init__()

    async def interaction_check(self, interaction: disnake.MessageInteraction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                content="Você não pode interagir aqui !", ephemeral=True
            )  # type: ignore
            return False
        else:
            return True


class Paginator(disnake.ui.View):
    def __init__(self, pages: List[disnake.Embed], ctx_id: int):
        self.cur_page: int = 1
        self.pages = pages
        self.ctx_id = ctx_id
        self.n_pages: int = len(pages)
        super().__init__(timeout=60.0)

    async def interaction_check(self, interaction: disnake.MessageInteraction):
        if interaction.user.id != self.ctx_id:
            await interaction.response.send_message(
                content="Você não pode interagir aqui !", ephemeral=True
            )  # type: ignore
            return False
        else:
            return True

    @staticmethod
    def paginate_emojis(list_emoji: List[disnake.Emoji],
                        guild: disnake.Guild) -> List[disnake.Embed]:
        collectionstr = list()
        for lists in list_emoji:
            collectionstr.append(
                disnake.Embed(
                    title=f"Emojis: {len(guild.emojis)}",
                    description='\n'.join(map(lambda c: f'{c} ➞ `{c}`', lists))
                )
            )
        return collectionstr

    @property
    def current(self):
        return str(self.cur_page)

    @disnake.ui.button(
        label="\N{BLACK LEFT-POINTING TRIANGLE}",
        style=disnake.ButtonStyle.secondary,
        disabled=True
    )  # type: ignore
    async def button_last(
        self, button: disnake.Button, interaction: disnake.MessageInteraction
    ):
        if self.cur_page > 1:
            self.cur_page -= 1
            self.button_next.disabled = False  # type: ignore
            self.button_current.label = self.current  # type: ignore
            button.disabled = True if self.cur_page == 1 else None  # type: ignore
            await interaction.response.edit_message(
                embed=self.pages[self.cur_page - 1], view=self
            )  # type: ignore

    @disnake.ui.button(
        label="1", style=disnake.ButtonStyle.primary, disabled=True
    )  # type: ignore
    async def button_current(self, _, interaction: disnake.MessageInteraction):
        self.button_current.label = self.current  # type: ignore
        await interaction.response.edit_message(view=self)  # type: ignore

    @disnake.ui.button(
        label="\N{BLACK RIGHT-POINTING TRIANGLE}",
        style=disnake.ButtonStyle.secondary
    )  # type: ignore
    async def button_next(
        self, button: disnake.Button, interaction: disnake.Interaction
    ):
        if self.cur_page != self.n_pages:
            self.cur_page += 1
            self.button_last.disabled = False  # type: ignore
            self.button_current.label = self.current  # type: ignore
            button.disabled = True if self.cur_page == self.n_pages else None  # type: ignore
            await interaction.response.edit_message(
                embed=self.pages[self.cur_page - 1], view=self
            )  # type: ignore

    @disnake.ui.button(
        emoji=_emoji["stop"], style=disnake.ButtonStyle.red
    )  # type: ignore
    async def button_stop(
        self, button: disnake.Button, interaction: disnake.Interaction
    ):
        await interaction.response.edit_message(view=None)  # type: ignore

    @disnake.ui.button(
        emoji=_emoji["trash"], style=disnake.ButtonStyle.red
    )  # type: ignore
    async def button_close(
        self, button: disnake.Button, interaction: disnake.Interaction
    ):
        await interaction.message.delete()  # type: ignore


class ViewerAdmin(disnake.ui.View):
    def __init__(
        self, ctx: commands.Context[Aurora], action: str,
        member: disnake.Member, reason: str, guild: disnake.Guild
    ):
        self.action = action
        self.member = member
        self.reason = reason
        self.guild = guild
        self.ctx = ctx
        super().__init__(timeout=60.0)

    async def interaction_check(self, interaction: disnake.Interaction):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(
                content="Você não pode interagir aqui !", ephemeral=True
            )  # type: ignore
            return False
        else:
            return True

    @disnake.ui.button(
        emoji=_emoji["confirm"], style=disnake.ButtonStyle.green
    )  # type: ignore
    async def _confirm(
        self, button: disnake.Button, interaction: disnake.Interaction
    ):
        if self.action == "kick":
            self.action = "expulsou"
            await self.guild.kick(self.member, reason=self.reason)
        elif self.action == "ban":
            self.action = "baniu"
            await self.guild.ban(self.member, reason=self.reason)
        elif self.action == "unban":
            self.action = "desbaniu"
            await self.guild.unban(self.member)
        await interaction.response.edit_message(  # type: ignore
            embed=disnake.Embed(
                description=
                f"Você {self.action} o membro {self.member.mention} com sucesso !!\nMotivo: `{self.reason}`",
                colour=disnake.Colour.random()),
            view=None)

    @disnake.ui.button(
        emoji=_emoji["cancel"], style=disnake.ButtonStyle.red
    )  # type: ignore
    async def _cancel(
        self, button: disnake.Button, interaction: disnake.Interaction
    ):
        await interaction.response.edit_message(  # type: ignore
            embed=disnake.Embed(description=f"Comando cancelado !!", ),
            view=None)


# ---------------------------------------------------------------------------------------------------------------------- #
class SelectLogs(disnake.ui.Select):  # type: ignore
    def __init__(
        self, logs: Dict[Any, Any], ctx: commands.Context[Aurora], bot: Aurora
    ):
        self.logs = Compact(logs).returnlist("log")
        self.bot = bot
        self.ctx = ctx
        super().__init__(
            min_values=1,
            max_values=1,
            options=[
                disnake.SelectOption(label=name, value=log)
                for name, log in self.logs
            ]
        )  # type: ignore

    async def callback(self, interaction: disnake.Interaction):
        VIEW = ViewConfirm(interaction.user.id)
        log: str = interaction.values[0]  # type: ignore
        log = "📄 Logs de Mensagem" if log == "message_log" else log
        log = "👤 Logs de Membro" if log == "member_log" else log
        log = "⚙️ Logs de Moderação" if log == "mod_log" else log
        await interaction.response.edit_message(  # type: ignore
            embed=disnake.Embed(
                description=
                f"Log selecionado: **{log}**\nVocê tem certeza que deseja ativar/desativar o log ?",
                colour=disnake.Colour.random()),
            view=VIEW)
        await VIEW.wait()
        await interaction.delete_original_message()
        if VIEW.value:
            await self.ctx.send(  # type: ignore
                embed=disnake.Embed(
                    description=f"Qual canal você deseja que seja os logs ?",
                    colour=disnake.Colour.random()),
                view=None)  # type: ignore
            try:
                func: Callable[
                    [disnake.Message], bool
                ] = lambda m: m.author.id == interaction.user.id and m.channel == interaction.channel
                message = await self.bot.wait_for(
                    "message", check=func, timeout=60.0
                )
            except asyncio.TimeoutError:
                return await self.ctx.send(  # type: ignore
                    embed=disnake.Embed(
                        description=f"Tempo esgotado, comando cancelado !!",
                        colour=disnake.Colour.random()))

            channel = await commands.TextChannelConverter().convert(
                self.ctx, message.content
            )  # type: ignore

            if channel is None:
                return await self.ctx.send(  # type: ignore
                    embed=disnake.Embed(
                        description=
                        f"Canal não encontrado, comando cancelado !!",
                        colour=disnake.Colour.random()))

            await self.bot.db.set_log(
                self.ctx.guild.id, channel.id, interaction.values[0]
            )  # type: ignore

            return await self.ctx.send(  # type: ignore
                embed=disnake.Embed(description=f"Log ativado com sucesso !!",
                                    colour=disnake.Colour.random()), )
        elif VIEW.value is None:
            return await self.ctx.send(  # type: ignore
                embed=disnake.Embed(description=f"Comando cancelado !!",
                                    colour=disnake.Colour.random()))

        elif VIEW.value is False:
            await self.bot.db.set_log(
                self.ctx.guild.id, None, interaction.values[0]
            )  # type: ignore
            return await self.ctx.send(  # type: ignore
                embed=disnake.Embed(
                    description=f"Log desativado com sucesso !!",
                    colour=disnake.Colour.random()))
