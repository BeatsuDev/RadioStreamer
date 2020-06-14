import subprocess
import asyncio

import requests
import discord

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
    genre = resp.headers.get("icy-genre", "unknown genre")
    station_name = resp.headers.get("icy-name", "unknown station")
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

    converter = subprocess.Popen(f"ffmpeg -i - -f s16le -ar {str(samplerate)} -b:a {bitrate}k pipe:1").split(),
			                      stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    voice_client.play(discord.PCMAudio(converter.stdout))
    await _process_audio_stream(resp, converter, metaint)


async def _process_audio_stream(resp, converter, metaint):
    audio_data = b''
    if metaint > 0:
        for chunk in resp.iter_content(1024):
            # Sleep a bit for other processes
            await asyncio.sleep(0.01)
            # Blindly push the chunk to the audio data
            audio_data += chunk

            if len(audio_data) > metaint:
                # Whoops, we went too far. But hold on, let's capture all the metadata before we proceed
                metasize = 16*audio_data[metaint]

                if len(audio_data) > (metaint + metasize):
                    # Now we're past both the audio data and the metadata
                    # After we've retreived the metadata, we now need to send the audio data off to somewhere else for processing
                    metadata = str(audio_data[metaint+1:metaint+1+metasize].rstrip(b'\x00'), 'utf-8')
                    try:
                        current_song = re.search(r"StreamTitle='(.*?)';", metadata).group(1)
                    except:
                        pass
                    audio_data_part = audio_data[:metaint]

                    # Now the audio data is already sent for processing, we can discard everything we've sent
                    audio_data = audio_data[metaint + 1 + metasize:]
                    converter.stdin.write(audio_data_part)
                else:
                    continue
    else:
        for chunk in resp.iter_content(1024):
            await asyncio.sleep(0.01)
            converter.stdin.write(chunk)
