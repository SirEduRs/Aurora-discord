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
from Utils.Utilidades import formatdelta


class On_MemberEvents(commands.Cog):
    """docstring for On_MemberEvents"""
    def __init__(self, bot: AuroraClass):
        super(On_MemberEvents, self).__init__()
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id == 513807537150099471:
            a = member.joined_at - member.created_at
            date = formatdelta(a, "{days}")
            date = int(date)
            dater = formatdelta(
                a,
                "{days} dias, {hours} horas, {minutes} minutos e {seconds} segundos."
            )
            if date < 10:
                try:
                    await member.send(
                        embed=disnake.Embed(
                            colour=disnake.Colour.random(),
                            description=
                            f"Você foi kickado do servidor por: Anti-Fake System | Conta criada em {dater}"
                        )
                    )
                except:
                    pass
                await member.guild.kick(
                    member,
                    reason=f"Anti-Fake System | Conta criada em {dater}"
                )
            try:
                cargo = disnake.utils.get(
                    member.guild.roles, id=838901535345868831
                )
                await member.add_roles(cargo)
            except Exception as e:
                print(e)


def setup(bot: AuroraClass):
    bot.add_cog(On_MemberEvents(bot))
