import asyncio
import logging

import discord
from discord.ext import commands

from core.cmds.play import valid_url
from core.cmds.play import stream_to

class Streamer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("COG")


    @commands.guild_only()
    @commands.command(aliases=["play"])
    async def stream(self, ctx, stream_link):
        '''Streams audio from an Icecast-like streaming service'''
        # Check if user is in a voice channel
        if not ctx.author.voice:
            await ctx.send("You must be in a voice channel before playing a stream!")
            return

        # Check if the link is a valid one
        if not valid_url(stream_link):
            await ctx.send("The URL provided was not an *stream* link. "
                           "Please provide a direct link to the mp3 source stream.")
            return

        # Check if the bot can play audio there
        member_converter = discord.ext.commands.MemberConverter()
        bot_member = await member_converter.convert(ctx, self.bot.user.mention)
        perms = ctx.author.voice.channel.permissions_for(bot_member)
        if not (perms.connect and perms.speak):
            await ctx.send("I'm not allowed to connect and speak in the VC you're in!")
            return

        # Connect and get voice client
        try:
            vcl = await ctx.author.voice.channel.connect()

        except asyncio.TimeoutError:
            await ctx.send(f"Timed out when attempting to join {ctx.author.voice.channel.name}")
            return
        except discord.ClientException:
            # Already joined a voice channel
            vcl = discord.utils.get(self.bot.voice_clients, channel__id=ctx.author.voice.channel.id)
        except discord.opus.OpusNotLoaded as e:
            await notify_bot_owner(bot, ctx, e)
            await ctx.send("OpusNotLoaded error. Bot creators have be notified! Hold on with this "
                           "feature for a bit, while the bot creators have a look.")
            return

        # Stream to VC
        try:
            await stream_to(vcl, stream_link, ctx)
            return
        except Exception as e:
            await ctx.send(f"Failed to stream from the given url. Error: {e}")
            return

    @commands.guild_only()
    @commands.command(aliases=["end"])
    async def stop(self, ctx):
        """Disconnects the bot"""
        if not ctx.author.voice:
            await ctx.send(f"{ctx.author.mention} You're not in a voice channel!")
            return

        bot_voice_client = discord.utils.get(self.bot.voice_clients, channel=ctx.author.voice.channel)
        if not bot_voice_client:
            await ctx.send(f"{ctx.author.mention} The bot isn't connected to your voice channel!")
            return

        await ctx.message.add_reaction("✔")
        await bot_voice_client.disconnect()
        return


def setup(bot):
    bot.add_cog(Streamer(bot))
