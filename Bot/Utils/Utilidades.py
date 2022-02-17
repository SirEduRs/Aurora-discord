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
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, List, TypeAlias

import disnake
from disnake.ext import commands
from pytz import timezone

if TYPE_CHECKING:
    from Aurora import AuroraClass
    Aurora: TypeAlias = AuroraClass
else:
    Aurora: TypeAlias = None


def convert_time(unit: str, time: str):
    time_convert = {
        "milisegundos": {
            "s": 1000,
            "m": 60000,
            "h": 3600000,
            "d": 86400000,
        },
        "segundos": {
            "s": 1,
            "m": 60,
            "h": 3600,
            "d": 86400,
        }
    }
    try:
        return int(time[:-1]) * time_convert[unit][time[-1]]
    except:
        return time


class Object:
    def toJSON(self):
        return json.dumps(
            self, default=lambda o: o.__dict__, sort_keys=True, indent=4
        )


async def EmbedDefault(
    sender: commands.Context[Aurora] | disnake.ApplicationCommandInteraction,
    message: str,
    ephemeral: bool = False
):
    if isinstance(sender, disnake.ApplicationCommandInteraction):
        return await sender.response.send_message(  # type: ignore
            embed=disnake.Embed(colour=disnake.Colour.random(),
                                description=message),
            ephemeral=ephemeral)
    else:
        return await sender.send(embed=disnake.Embed(  # type: ignore
            colour=disnake.Colour.random(),
            description=message,
        ))


def formatdelta(delta: timedelta, fmt: str) -> str:
    d = {"days": delta.days}
    d['hours'], rem = divmod(delta.seconds, 3600)
    d['years'], d['dias'] = divmod(delta.days, 365)
    d['minutes'], d['seconds'] = divmod(rem, 60)
    return fmt.format(**d)


def pretty(value: Any, htchar: str = '\t', lfchar: str = '\n', indent: int = 0):
    nlch = lfchar + htchar * (indent + 1)
    if isinstance(value, dict):
        items: List[Any] = [
            nlch + repr(key) + ': ' +
            pretty(value[key], htchar, lfchar, indent + 1)  # type: ignore
            for key in value  # type: ignore
        ]
        return '{%s}' % (','.join(items) + lfchar + htchar * indent)
    elif isinstance(value, list):
        items = [
            nlch + pretty(item, htchar, lfchar, indent + 1)
            for item in value  # type: ignore
        ]
        return '[%s]' % (','.join(items) + lfchar + htchar * indent)
    elif isinstance(value, tuple):
        items = [
            nlch + pretty(item, htchar, lfchar, indent + 1)
            for item in value  # type: ignore
        ]
        return '(%s)' % (','.join(items) + lfchar + htchar * indent)
    else:
        result = str(value)
        environments = [
            'USERM', 'PASSM', 'DISCORD_TOKEN', 'DSN', 'API_HEROKU',
            'PASTEBIN_TOKEN', 'PASTEBIN_USER', 'PASTEBIN_PASS'
        ]
        for env in environments:
            result = result.replace(os.environ[env], '[CENSURADO]')
        return result


def pastebin_post(title: str, content: str):
    PASTEBIN_KEY = os.getenv("PASTEBIN_TOKEN")
    PASTEBIN_URL = 'https://pastebin.com/api/api_post.php'
    PASTEBIN_LOGIN_URL = 'https://pastebin.com/api/api_login.php'
    PASTEBIN_LOGIN = os.getenv("PASTEBIN_USER")
    PASTEBIN_PWD = os.getenv("PASTEBIN_PASS")
    login_params = dict(
        api_dev_key=PASTEBIN_KEY,
        api_user_name=PASTEBIN_LOGIN,
        api_user_password=PASTEBIN_PWD
    )

    data = urllib.parse.urlencode(login_params).encode("utf-8")
    req = urllib.request.Request(PASTEBIN_LOGIN_URL, data)

    with urllib.request.urlopen(req) as response:
        pastebin_vars = dict(
            api_option='paste',
            api_dev_key=PASTEBIN_KEY,
            api_user_key=response.read(),
            api_paste_name=title,
            api_paste_code=content,
            api_paste_private=1,
        )
        return urllib.request.urlopen(
            PASTEBIN_URL,
            urllib.parse.urlencode(pastebin_vars).encode('utf8')
        ).read()


async def color(
    user: disnake.Member | disnake.User, guild: disnake.Guild, bot: commands.Bot
):
    text = await bot.http.get_user(user.id)
    if text["banner_color"]:  # type: ignore
        return int(text["banner_color"][1:], 16)  # type: ignore
    elif guild:
        return user.colour
    else:
        return disnake.Colour.random()


async def get_userinfo(
    user_id: int, author: disnake.Member, guild: disnake.Guild,
    bot: commands.Bot
):
    user = await guild.fetch_member(user_id)
    name, daten, disp = None, None, None
    badges: List[str] = []
    roles: List[str] = []
    dateni, dt = None, disnake.utils.utcnow()
    name = user.nick if user.nick else user.name
    if user.joined_at:
        daten = user.joined_at.replace(tzinfo=timezone('America/Sao_Paulo'))
    if user.premium_since:
        dateni = user.premium_since.replace(
            tzinfo=timezone('America/Sao_Paulo')
        )
        dateni = formatdelta(
            datetime.now().replace(tzinfo=timezone('America/Sao_Paulo')) -
            dateni, "{days}"
        )  # type: ignore
        dateni = int(dateni)  # type: ignore
    if user.premium_since or user.avatar.is_animated():
        badges.append("<:nitro:861980521415704607>")
    [
        roles.append(re.mention)
        for re in user.roles if not re.name == "@everyone"
    ]  # type: ignore
    roles.reverse()
    if user.mobile_status[0] != "offline":  #type: ignore
        disp = "<:smartphone:873574351033729044> Mobile"
    elif user.desktop_status[0] != "offline":  #type: ignore
        disp = "<:desktop:873574351037927444> Desktop"
    elif user.web_status[0] != "offline":  #type: ignore
        disp = "<:web:873574350966648892> Web"
    date = user.created_at.replace(tzinfo=timezone('America/Sao_Paulo'))
    emoji = "<:coroa:784164230005784657>" if user.id == guild.owner_id else ":bust_in_silhouette:"
    match dateni:
        case num if num in range(0, 59):
            badges.append("<:lvl1:862393142473261066>")
        case num if num in range(60, 90):
            badges.append("<:lvl2:862393142548234281>")
        case num if num in range(90, 186):
            badges.append("<:lvl3:862393142589128734>")
        case num if num in range(186, 279):
            badges.append("<:lvl4:862393142627139585>")
        case num if num in range(279, 365):
            badges.append("<:lvl5:862393142828990524>")
        case num if num in range(365, 465):
            badges.append("<:lvl6:862393143147495514>")
        case num if num in range(465, 558):
            badges.append("<:lvl7:862393143025205258>")
        case num if num in range(558, 730):
            badges.append("<:lvl8:862393142678650891>")
        case num if num in range(730, 1500):
            badges.append("<:lvl9:862393142766731265>")
    emojis_dict = {
        "early_supporter":
            "<:earlysupporter:862108857567936552>",
        "hypesquad":
            "<:hypersquad:862108857370804255>",
        "hypesquad_brilliance":
            "<:brillance:862108857182453790>",
        "hypesquad_bravery":
            "<:bravery:862108856586207253>",
        "hypesquad_balance":
            "<:balance:862108857626656829>",
        "bug_hunter":
            "<:bughunter1:862109772618006569>",
        "bug_hunter_level_2":
            "<:bughunter2:862108857660604416>",
        "discord_certified_moderator":
            "<:moderatorcertified:862108857187041320>",
        "partner":
            "<:partner:862108857539100712>",
        "staff":
            "<:dcstaff:862108857223741491>",
        "verified_bot_developer":
            "<:devbadge:862108857369886721>",
    }
    for badge in user.public_flags.all():
        if badge.name in emojis_dict:
            badges.append(emojis_dict[badge.name])
    text = await bot.http.get_user(user.id)
    Embed = disnake.Embed(colour=await color(user, guild, bot), timestamp=dt)
    Embed.add_field(name=f"{emoji} Usúario:", value=f"{name}")
    if badges:
        Embed.add_field(
            name=f"<:badge:864523951102754816> Badges:", value=' '.join(badges)
        )
    Embed.add_field(name=f":page_facing_up: ID:", value=user.id, inline=False)
    Embed.add_field(
        name=f":technologist: Dispositivo:", value=disp, inline=False
    ) if disp else None
    Embed.add_field(
        name="<a:calendario:784374299540062228> Conta criada em:",
        value=f"<t:{date:%s}:D>"
    )
    Embed.add_field(
        name=":door: Entrou em:", value=f"<t:{daten:%s}:D>"
    ) if daten else None
    Embed.add_field(
        name=
        f"<:role:851508921612763157> Cargos ({len(roles)}/{len(author.guild.roles)}):",
        value=', '.join(roles),
        inline=False
    ) if roles else None
    Embed.set_thumbnail(url=user.display_avatar)
    Embed.set_footer(
        text=f"Comando usado por {author.name}", icon_url=author.display_avatar
    )
    if text["banner"]:  # type: ignore
        av = disnake.Embed(
            title="Avatar", colour=await color(user, guild, bot), timestamp=dt
        )
        dc = disnake.Embed(
            title="Banner", colour=await color(user, guild, bot), timestamp=dt
        )
        met = (await bot.fetch_user(user.id)).banner
        dc.set_image(url=met)
        av.set_image(url=user.display_avatar)
        dc.set_footer(
            text=f"Comando usado por {author.name}",
            icon_url=author.display_avatar
        )
        av.set_footer(
            text=f"Comando usado por {author.name}",
            icon_url=author.display_avatar
        )
        return [Embed, av, dc]
    else:
        av = disnake.Embed(
            title="Avatar", colour=await color(user, guild, bot), timestamp=dt
        )

        av.set_image(url=user.display_avatar)
        av.set_footer(
            text=f"Comando usado por {author.name}",
            icon_url=author.display_avatar
        )
        return [Embed, av]


def split_list(list_split: List[Any], n: int) -> List[List[Any]]:
    lists = []
    while len(list_split) > n:
        lists.append(list_split[:n])
        list_split = list_split[n:]
    lists.append(list_split)
    return lists


def permissions(permission: str):
    Permissions = {
        "add_reactions": "adicionar reações",
        "administrator": "administrador",
        "attach_files": "enviar arquivos",
        "ban_members": "banir membros",
        "change_nickname": "mudar apelido",
        "connect": "entrar na chamada",
        "create_instant_invite": "criar invite",
        "deafen_members": "ensurdecer membros",
        "embed_links": "inserir links",
        "external_emojis": "usar emojis externos",
        "kick_members": "expulsar membros",
        "manage_channels": "gerenciar canais",
        "manage_emojis": "gerenciar emojis",
        "manage_guild": "gerenciar o servidor",
        "manage_messages": "gerenciar mensagens",
        "external_stickers": "usar figurinhas externas",
        "manage_nicknames": "gerenciar apelidos",
        "manage_permissions": "gerenciar permissões",
        "manage_roles": "gerenciar cargos",
        "manage_webhooks": "gerenciar webhooks",
        "manage_threads": "gerenciar threads",
        "mention_everyone": "mencionar everyone",
        "move_members": "mover membros da chamada",
        "mute_members": "mutar membros",
        "moderate_members": "moderar membros",
        "priority_speaker": "voz prioritária",
        "read_message_history": "ler historico de mensagens",
        "read_messages": "ler mensagens novas",
        "send_messages_in_threads": "enviar mensagens em threads",
        "request_to_speak": "pedir para falar",
        "send_messages": "enviar mensagens",
        "send_tts_messages": "enviar mensagem com /tts",
        "speak": "falar na chamada",
        "stream": "ligar a camera/compartilhar a tela",
        "use_slash_commands": "usar slash commands",
        "use_voice_activation": "usar detecção de voz",
        "view_audit_log": "ver o registro de auditoria",
        "view_channel": "ver chat",
        "use_threads": "usar threads",
        "use_private_threads": "usar threads privadas",
        "create_public_threads": "Criar threads públicas",
        "create_private_threads": "Criar threads privadas",
        "view_guild_insights": "ver análises do servidor"
    }
    return Permissions[permission]
