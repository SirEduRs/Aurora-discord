from datetime import timedelta

import disnake
from disnake.ext.commands import (  # type: ignore
    BucketType,
    Cog,
    Context,
    command,
    cooldown,
)
from humanize import precisedelta

import Utils.pomice as pomice
from Aurora import AuroraClass
from Utils.Player import PlayerMusic
from Utils.pomice import Track
from Utils.Utilidades import EmbedDefault as Embed


class MusicBot(Cog, name="<:music:936038809794138143> Música"):  # type: ignore
    def __init__(self, bot: AuroraClass):
        self.bot = bot
        self.pomice = bot.pomice

    @command(
        name='play',
        aliases=['tocar', 'p'],
        description='Tocar uma música do Youtube ou Spotify',
        usage='play <nome ou link>'
    )
    async def _play(self, ctx: Context[AuroraClass], *, music: str):
        channel = getattr(ctx.author.voice, 'channel', None)  # type: ignore
        if not channel:
            return await Embed(
                ctx, message="Você precisa estar em um canal de voz !"
            )

        if not ctx.voice_client:
            if ctx.me.voice:
                return await Embed(
                    ctx, message="Eu já estou em um canal de voz !"
                )
            #node = self.pomice.get_best_node(algorithm=NodeAlgorithm.by_ping)
            node = self.pomice.get_node(identifier='São Paulo')
            await ctx.author.voice.channel.connect(
                cls=PlayerMusic(node=node)
            )  # type: ignore
            await ctx.guild.change_voice_state(channel=channel, self_deaf=True)

        player: PlayerMusic = ctx.voice_client  # type: ignore
        player.context = ctx
        player._bot = self.bot
        lenght: int = 0

        results = await player.get_tracks(query=f'{music}', ctx=ctx)

        if not results:
            return await Embed(
                ctx,
                message="Não consegui encontrar nenhuma música com esse nome !"
            )

        if isinstance(results, pomice.Playlist):
            for track in results.tracks:  # type: ignore
                lenght += track.length
                await player.queue.put(track)  # type: ignore
            if player.is_playing:
                count = len(results.tracks)
                embed = disnake.Embed(
                    title=
                    f":white_check_mark: Playlist adicionada a fila com sucesso !",
                    description=
                    f":name_badge: Nome: **[{results.name}]({music})**\n"
                    f":hourglass: Duração: `{precisedelta(timedelta(milliseconds=lenght))}`\n"
                    f":musical_note: Músicas: `{count}`",
                    colour=disnake.Colour.random()
                )
                embed.set_thumbnail(url=results.thumbnail)
                embed.set_footer(text=f"Tocando agora: {player.current.title}")
                await ctx.send(embed=embed)
        else:
            track = results[0]
            await player.queue.put(track)  # type: ignore
            if player.is_playing:
                embed = disnake.Embed(
                    title=
                    ":white_check_mark: Música adicionada a fila com sucesso !",
                    description=f"[{track.title}]({track.uri})",  # type: ignore
                    colour=disnake.Colour.random()
                )
                embed.set_thumbnail(url=track.thumbnail)  # type: ignore
                embed.set_footer(
                    text=f"Tocando agora: {player.current.title}"
                )  # type: ignore
                await ctx.send(embed=embed)  # type: ignore

        if not player.is_playing:
            await player.do_next()

    """@command(
        name='leave',
        aliases=['sair'],
        description='Sair do canal de voz',
        usage='leave'
    )
    async def _leave(self, ctx: Context[AuroraClass]):
        channel = getattr(ctx.author.voice, 'channel', None)  # type: ignore
        if not channel:
            return await Embed(
                ctx, message="Você precisa estar em um canal de voz !"
            )

        if not ctx.voice_client:
            return await Embed(
                ctx, message="Eu não estou em um canal de voz !"
            )

        player: PlayerMusic = ctx.voice_client  # type: ignore



        await ctx.voice_client.disconnect()"""

    @command(
        name='pause',
        aliases=['pausar'],
        description='Pausar a música',
        usage='pause'
    )
    async def _pause(self, ctx: Context[AuroraClass]):
        channel = getattr(ctx.author.voice, 'channel', None)  # type: ignore
        if not channel:
            return await Embed(
                ctx, message="Você precisa estar em um canal de voz !"
            )

        if not ctx.voice_client:
            return await Embed(ctx, message="Eu não estou em um canal de voz !")

        player: PlayerMusic = ctx.voice_client  # type: ignore
        if not player.is_playing:
            return await Embed(ctx, message="Não estou tocando nada !")

        await player.set_pause(True)
        await Embed(
            ctx,
            message=
            f"<:music:936038809794138143> Pausado: **[{player.current.title}]({player.current.uri})**"
        )

    @command(
        name='resume',
        aliases=['continuar'],
        description='Continuar a música',
        usage='resume'
    )
    async def _resume(self, ctx: Context[AuroraClass]):
        channel = getattr(ctx.author.voice, 'channel', None)  # type: ignore
        if not channel:
            return await Embed(
                ctx, message="Você precisa estar em um canal de voz !"
            )

        if not ctx.voice_client:
            return await Embed(ctx, message="Eu não estou em um canal de voz !")

        player: PlayerMusic = ctx.voice_client  # type: ignore
        if not player.is_playing:
            return await Embed(ctx, message="Não estou tocando nada !")

        await player.set_pause(False)
        await Embed(
            ctx,
            message=
            f"<:music:936038809794138143> Continuando: **[{player.current.title}]({player.current.uri})**"
        )

    @command(
        name='stop',
        aliases=['parar'],
        description='Para a música atual',
    )
    async def _stop(self, ctx: Context[AuroraClass]):
        player: PlayerMusic = ctx.voice_client  # type: ignore
        if not ctx.voice_client:
            return await Embed(ctx, message="Eu não estou em um canal de voz !")
        if not player.is_playing:
            return await Embed(ctx, message="Não estou tocando nada !")

        if player.current.requester != ctx.author:
            return await Embed(
                ctx,
                message="Você não pode parar a música que não requisitou !"
            )

        await player.teardown()
        await ctx.send(embed=disnake.Embed(  # type: ignore
            title=":white_check_mark: Música parada com sucesso !", ))

    @command(
        name="volume",
        aliases=['vol'],
        description='Ajusta o volume da música',
        usage='volume <número>'
    )
    @cooldown(1, 5, BucketType.user)
    async def _volume(self, ctx: Context[AuroraClass], volume: int):
        if volume < 0 or volume > 100:
            return await Embed(ctx, message="O volume deve ser entre 0 e 100 !")
        player: PlayerMusic = ctx.voice_client  # type: ignore
        if not player.is_playing:
            return await Embed(ctx, message="Não estou tocando nada !")
        await player.set_volume(volume)
        await ctx.send(embed=disnake.Embed(  # type: ignore
            title=":white_check_mark: Volume alterado com sucesso !",
            description=f"**Volume**: `{volume}`"
        ))

    @command(
        name="queue",
        aliases=['fila'],
        description='Mostra a fila de músicas',
    )
    async def _queue(self, ctx: Context[AuroraClass]):
        player: PlayerMusic = ctx.voice_client  # type: ignore
        if not player.is_playing:
            return await Embed(ctx, message="Não estou tocando nada !")
        if not player.queue.qsize():
            return await Embed(ctx, message="A fila está vazia !")

        embed = disnake.Embed(
            title=":musical_note: Fila de músicas",
            description="",
            colour=disnake.Colour.random()
        )

        embed.set_footer(text=f"Tocando agora: {player.current.title}")

        for i, track in enumerate(player.queue._queue):
            embed.description += f"{i + 1}. **[{track.title}]({track.uri})**\n"

        await ctx.send(embed=embed)

    @command(
        name='skip',
        aliases=['pular'],
        description='Pula a música atual',
    )
    async def _skip(self, ctx: Context[AuroraClass]):
        player: PlayerMusic = ctx.voice_client
        if not player.is_playing:
            return await Embed(ctx, message="Não estou tocando nada !")

        if player.current.requester != ctx.author:
            return await Embed(ctx, message="Você não pode pular essa música !")

        await player.stop()

    @Cog.listener()
    async def on_pomice_track_end(self, player: PlayerMusic, track: Track, _):
        await player.do_next()

    @Cog.listener()
    async def on_pomice_track_stuck(self, player: PlayerMusic, track: Track, _):
        await player.do_next()

    @Cog.listener()
    async def on_pomice_track_exception(
        self, player: PlayerMusic, track: Track, _
    ):
        await player.do_next()


def setup(bot: AuroraClass):
    bot.add_cog(MusicBot(bot))
