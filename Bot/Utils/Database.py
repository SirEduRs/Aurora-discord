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

import json
import os
import secrets
from typing import Any, List, Optional

import asyncpg
import disnake
from disnake.ext.commands import Bot
from firebase_admin import firestore


class Database:
    def __init__(self, bot: Bot):
        self.bot = bot

    @staticmethod
    async def init_db(conn: asyncpg.connection.Connection):
        await conn.set_type_codec(
            'jsonb',
            schema='pg_catalog',
            encoder=lambda v: json.dumps(v),
            decoder=lambda v: json.loads(v)
        )

    async def initialize_pool(self) -> Optional[asyncpg.pool.Pool]:
        #Crie um pool sem senha
        pool = await asyncpg.create_pool(
            host="database",
            user=os.environ["PG_USER"],
            password=os.environ["PG_PASS"],
            database=os.environ["PG_DB"],
            init=self.init_db
        )
        return pool

    async def get(self, serverid: int):
        async with self.bot.pool.acquire() as connection:
            resp = await connection.fetch(
                f'SELECT * FROM guilds WHERE guild_id = {serverid}'
            )
            if resp:
                return resp[0]
            return None

    async def create(self, serverid: int, prefix: str):
        async with self.bot.pool.acquire() as connection:
            logs = {"message_log": None, "member_log": None, "mod_log": None}
            logs = json.dumps(logs)
            try:
                await connection.execute(
                    f'INSERT INTO guilds(guild_id, prefix, logs) VALUES($1, $2, $3)',
                    serverid, prefix, logs
                )
                return True
            except asyncpg.exceptions.UniqueViolationError:
                pass

    async def update_prefix(self, serverid: int, prefix: str):
        async with self.bot.pool.acquire() as connection:
            return await connection.execute(
                f"UPDATE guilds SET prefix = '{prefix}' WHERE guild_id = {serverid}"
            )

    async def get_prefix(self, message: disnake.Message) -> str:
        async with self.bot.pool.acquire() as connection:
            server, prefixo = None, None
            if message.guild:
                server = await self.get(message.guild.id)
                if server:
                    prefixo = await connection.fetch(
                        f'SELECT prefix FROM guilds WHERE guild_id = {message.guild.id}'
                    )
                if prefixo:
                    return prefixo[0][0]
                if server is None:
                    await self.create(message.guild.id, "a.")
                return "a."
            return "a."

    async def set_log(self, serverid: int, channel_id: int, log: str):
        async with self.bot.pool.acquire() as connection:
            try:
                logs = (
                    await connection.fetch(
                        f"SELECT logs FROM guilds where guild_id = {serverid}"
                    )
                )[0][0]
                logs = json.loads(logs)
                logs[log] = channel_id
                log_c = json.dumps(logs)
                await connection.execute(
                    f"UPDATE guilds SET logs = $1 WHERE guild_id = $2", log_c,
                    serverid
                )
                return True
            except Exception:
                raise Exception

    async def get_log(self, serverid: int, log: str) -> Any:
        async with self.bot.pool.acquire() as connection:
            response = (
                await connection.
                fetch(f"SELECT logs FROM guilds WHERE guild_id = {serverid}")
            )[0][0]
            if response:
                response = json.loads(response)
                resp = response[log]
                if resp:
                    return await self.bot.fetch_channel(resp)
                return None
            else:
                logs = {
                    "message_log": None,
                    "member_log": None,
                    "mod_log": None
                }
                logs = json.dumps(logs)
                await connection.execute(
                    f"UPDATE guilds SET logs = $1 WHERE guild_id = $2", logs,
                    serverid
                )
                return None

    async def get_account(self, userid: int) -> str | None:
        async with self.bot.pool.acquire() as connection:
            resp = await connection.fetch(
                f"SELECT account FROM users WHERE id = {userid}"
            )
            if resp:
                return resp[0]
            else:
                return None

    async def add_user(self, userid: int, account: str):
        async with self.bot.pool.acquire() as connection:
            return await connection.execute(
                f"INSERT INTO users(id, account) VALUES ($1, $2)", userid,
                account
            )

    async def delete_user(self, userid: int):
        async with self.bot.pool.acquire() as connection:
            return await connection.execute(
                f"DELETE FROM users WHERE id = {userid}"
            )

    async def create_vip(
        self, account: str, vip: str, duration: str
    ) -> disnake.Message:
        async with self.bot.pool.acquire() as connection:
            date = disnake.utils.format_dt(duration, "f")
            duration = str(duration)
            await connection.execute(
                f"INSERT INTO vips(account, vip, duration) VALUES ($1, $2, $3)",
                account, vip, duration
            )
            channel = await self.bot.fetch_channel(909397032672837662)
            embed = disnake.Embed(
                title="VIP CREATED",
                description=f"Conta: **`{account}`**\n"
                f"Vip: **`{vip}`**\n"
                f"Data de termino: {date}",
                color=disnake.Color.green()
            )
            return await channel.send(embed=embed)

    async def get_all_vips(self) -> List[Any]:
        async with self.bot.pool.acquire() as connection:
            return await connection.fetch("SELECT * FROM vips")

    async def remove_vip(self, account: str, vip: str) -> disnake.Message:
        async with self.bot.pool.acquire() as connection:
            vipa = await connection.fetch(
                "SELECT vip FROM vips WHERE account = $1 AND vip = $2;",
                account, vip
            )
            await connection.execute(
                f"DELETE FROM vips WHERE account = $1 AND vip = $2;", account,
                vip
            )
            channel = await self.bot.fetch_channel(909397032672837662)
            embed = disnake.Embed(
                title="VIP REMOVED",
                description=f"Conta: **`{account}`**\nVip: **`{vipa[0][0]}`**",
                color=disnake.Color.red()
            )
            return await channel.send(embed=embed)


class Firebase:
    def __init__(self, bot=None):
        self.bot = bot
        self.db = firestore.client()

    async def get_collection(self, collection: str):
        values = dict()
        docs = self.db.collection(collection).stream()
        for doc in docs:
            values[doc.id] = doc.to_dict()
        return values

    async def get_document(self, collection: str, doc: str) -> dict | Any:
        doc = self.db.collection(collection).document(doc).get().to_dict()
        if doc:
            return doc
        else:
            return False

    async def get_documents(self, collection: str):
        values: List[str] = list()
        docs = self.db.collection(collection).stream()
        for doc in docs:
            values.append(doc.id)
        return values

    async def delete_document(self, collection: str, doc: str):
        return self.db.collection(collection).document(doc).delete()

    async def update_document(self, collection: str, doc: str, data):
        return self.db.collection(collection).document(doc).update(data)

    async def add_document(self, collection: str, data, id: str = ''):
        return self.db.collection(collection).add(
            document_data=data, document_id=id
        )

    async def set_data(self, collection, doc, data):
        return self.db.collection(collection).document(doc).set(data)

    async def create_document(self, collection, doc, data):
        return self.db.collection(collection).document(doc).set(data)

    async def create_user(self, data):
        token = secrets.token_urlsafe(16)
        self.db.collection("users").document(token).set(data)
        return token
