import discord
from discord.ext import commands

class RadioStreamer(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='r!')
