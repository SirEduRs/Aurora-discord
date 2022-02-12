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

from os import environ

import disnake
from disnake.ext import commands

from Aurora import AuroraClass


class On_ReadyEvent(commands.Cog):
    def __init__(self, bot: AuroraClass):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.pomice.create_node(
            bot=self.bot,
            host='168.138.69.116',
            port='2333',
            password=environ['LAVALINK_PASS'],
            identifier='Canada'
        )
        await self.bot.pomice.create_node(
            bot=self.bot,
            host='150.230.94.5',
            port='2333',
            password=environ['LAVALINK_PASS'],
            identifier='São Paulo'
        )
        await self.bot.pool.execute(
            "CREATE TABLE IF NOT EXISTS users(id bigint PRIMARY KEY, account text UNIQUE);"
        )
        await self.bot.pool.execute(
            "CREATE TABLE IF NOT EXISTS vips(account text PRIMARY KEY, vip text, duration text, UNIQUE (account, vip));"
        )
        await self.bot.pool.execute(
            "CREATE TABLE IF NOT EXISTS guilds(guild_id bigint PRIMARY KEY, prefix varchar(255), logs json not null);"
        )
        user = await self.bot.fetch_user(self.bot.owner_id)
        users = 0
        for guild in self.bot.guilds:
            users += len(guild.members)
        print(f"\033[m{('▬▬' * 20)}")
        print(f"\033[m▍\033[1;95mDono: \033[1;96m{str(user)}           \033[m▍")
        print(
            f"\033[m▍\033[1;95mLogado em \033[1;96m{self.bot.user.name} \033[1;94m({self.bot.user.id}) \033[m▍"
        )
        print(
            f"\033[m▍\033[1;95mServidores: \033[1;96m{str(len(self.bot.guilds))}                          \033[m▍"
        )  #str(owner).rjust(50)
        print(
            f"\033[m▍\033[1;95mUsuários: \033[1;96m{str(users)}                         \033[m▍"
        )
        print(f"\033[m{('▬▬' * 20)}")
        await self.bot.change_presence(
            status=disnake.Status.dnd,
            activity=disnake.Game(name="Evoluindo sempre !")
        )


def setup(bot: AuroraClass):
    bot.add_cog(On_ReadyEvent(bot))
    print(
        "\033[1;95m[Events Load]\033[1;94m On Ready\033[1;96m carregado com sucesso !"
    )
