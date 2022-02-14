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
from Utils import Paginator
from Utils.Utilidades import get_userinfo


class User(commands.Cog, name=":bust_in_silhouette: Usuário"):  # type: ignore
    """docstring for Usúario"""
    def __init__(self, bot: commands.Bot):
        super(User, self).__init__()
        self.bot = bot

    @commands.command(
        description="Mostra a foto de perfil de um usúario",
        usage="avatar <menção|ID>",
        name="avatar",
        aliases=['a', 'av']
    )
    async def _avatar(
        self,
        ctx: commands.Context[AuroraClass],
        *,
        member: disnake.Member | disnake.User = None
    ):
        dt = disnake.utils.utcnow()
        member = member or ctx.author
        if member == ctx.author:
            Embeder = disnake.Embed(
                title="Sua foto de perfil:", colour=0x0101DF, timestamp=dt
            )
            Embeder.set_image(url=member.display_avatar)
            Embeder.set_footer(
                text=f"Comando usado por {ctx.author.name}",
                icon_url=ctx.author.avatar.url
            )
            return await ctx.send(embed=Embeder)  # type: ignore
        elif member == ctx.me:
            Embeder = disnake.Embed(
                title="Foto de Perfil do BOT:", colour=0x0101DF, timestamp=dt
            )
            Embeder.set_image(url=member.display_avatar)
            Embeder.set_footer(
                text=f"Comando usado por {ctx.author.name}",
                icon_url=ctx.author.avatar.url
            )
            return await ctx.send(embed=Embeder)  # type: ignore
        else:
            Embeder = disnake.Embed(
                title=f"Foto de perfil de {member}",
                colour=0x0101DF,
                timestamp=dt
            )
            Embeder.set_image(url=member.display_avatar)
            Embeder.set_footer(
                text=f"Comando usado por {ctx.author.name}",
                icon_url=ctx.author.avatar.url
            )
            return await ctx.send(embed=Embeder)  # type: ignore

    @commands.command(
        name="banner",
        aliases=['b'],
        description="Mostra o banner de um usúario",
        usage="banner <menção|ID>",
    )
    @commands.guild_only()
    async def _banner(
        self,
        ctx: commands.Context[AuroraClass],
        *,
        member: disnake.Member | disnake.User = None
    ):
        dt = disnake.utils.utcnow()
        if member is not None:
            member = member or ctx.author
            banner = (await self.bot.fetch_user(member.id)).banner
            if banner is None:
                if member == ctx.author:
                    txt = "Você não possui um banner."
                else:
                    txt = "Esse membro não possui um banner."
                Embeder = disnake.Embed(
                    title=txt, colour=disnake.Colour.random(), timestamp=dt
                )
                return await ctx.send(embed=Embeder)  # type: ignore
            if member == ctx.author:
                Embeder = disnake.Embed(
                    title="Seu banner:",
                    colour=disnake.Colour.random(),
                    timestamp=dt
                )
                Embeder.set_image(url=banner)
                Embeder.set_footer(
                    text=f"Comando usado por {ctx.author.name}",
                    icon_url=ctx.author.avatar.url
                )
                return await ctx.send(embed=Embeder)  # type: ignore
            else:
                Embeder = disnake.Embed(
                    title=f"Banner de {member}",
                    colour=disnake.Colour.random(),
                    timestamp=dt
                )
                Embeder.set_image(url=banner)
                Embeder.set_footer(
                    text=f"Comando usado por {ctx.author.name}",
                    icon_url=ctx.author.avatar.url
                )
                return await ctx.send(embed=Embeder)  # type: ignore
        else:
            banner = (await self.bot.fetch_user(ctx.author.id)).banner
            if banner is None:
                txt = "Você não possui um banner."
                return await ctx.send(
                    embed=disnake.Embed(
                        title=txt, colour=disnake.Colour.random(), timestamp=dt
                    )
                )  # type: ignore
            else:
                Embeder = disnake.Embed(
                    title="Seu banner:", colour=0x0101DF, timestamp=dt
                )
                Embeder.set_image(url=banner)
                Embeder.set_footer(
                    text=f"Comando usado por {ctx.author.name}",
                    icon_url=ctx.author.display_avatar
                )

    @commands.command(
        description="Mostra as informações do usúario.",
        usage="userinfo <menção|ID>",
        name="userinfo",
        aliases=['ui', 'user']
    )
    @commands.guild_only()
    async def _userinfo(
        self,
        ctx: commands.Context[AuroraClass],
        *,
        user: disnake.Member = None
    ):
        user = user or ctx.author
        list_embeds = await get_userinfo(
            user_id=user.id, author=ctx.author, guild=ctx.guild, bot=self.bot
        )
        View = Paginator(list_embeds, ctx.author.id)
        View.button_current.disabled = True
        View.button_last.disabled = True
        await ctx.send(embed=list_embeds[0], view=View)


def setup(bot: AuroraClass):
    bot.add_cog(User(bot))
    print(
        "\033[1;92m[Cog Load]\033[1;94m User\033[1;96m carregado com sucesso !"
    )
