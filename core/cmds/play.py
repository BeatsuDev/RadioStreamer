import subprocess
import asyncio

import requests
import discord
import ffmpeg

def valid_url(url) -> bool:
    resp = requests.get(url, stream=True)
    # Not finished yet
    return True

async def notify_bot_owner(bot, ctx, e):
    self.logger.warning(f"{e} in {ctx.guild.name} by "
                        f"{ctx.author.name}#{ctx.author.discriminator}")
    async with self.bot.application_info() as app_info:
        try:
            # Could be done more thoroughly, like checking other channels or existing invites
            # but it's not too important, so won't spend time to do that.
            guild_invite = await ctx.channel.create_invite(reason="OpusNotLoaded error. Invite for bot owner.")
            guild_invite_msg = "Invite to guild: " + guild_invite.code
        except:
            guild_invite_msg = "Could not create invite for the given channel."

        await app_info.owner.send(f"OpusNotLoaded exception was raised in {ctx.guild.name}. {guild_invite}")

async def stream_to(voice_client, url, ctx):
    resp = requests.get(url, stream=True)

    # Gather information about stream
    station_name = resp.headers.get("icy-name", "unknown station")
    genre = resp.headers.get("icy-genre")
    stream_fmt = resp.headers.get("Content-Type")
    bitrate = int(resp.headers.get("icy-br", 0))
    samplerate = int(resp.headers.get("icy-sr", 0))
    audio_info = resp.headers.get("ice-audio-info")
    metaint = int(resp.headers.get("icy-metaint", 0))

    # Send information about stream
    desc = ""
    for category, value in zip(["Genre", "Format", "Bitrate", "Samplerate", "Audio Info"],
                                [genre, stream_fmt, bitrate, samplerate, audio_info]):
        if value:
            desc += f"{category}: {value}\n"

    embed = discord.Embed(title="Radio information:",
                          description=desc,
                          colour=ctx.author.colour.value or 0xff0)
    embed.set_author(name=f"Streaming from {station_name}", icon_url=voice_client.user.avatar_url)
    await ctx.send(embed=embed)

    converter = (
        ffmpeg
        .input(url, re=None)
        .output("pipe:1", format="s16le")
        .run_async(pipe_stdout=True)
    )
    voice_client.play(discord.PCMAudio(converter.stdout))
