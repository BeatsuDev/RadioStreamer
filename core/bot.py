import os
import logging

import discord
from discord.ext import commands

class RadioStreamer(commands.Bot):
    def __init__(self):
        self.logger = logging.getLogger("BOT")

        super().__init__(command_prefix="r!")

    async def on_ready(self):
        # Load every cog
        for fname in os.listdir(os.path.join("core", "cogs")):
            if not fname.endswith('.py'): continue
            try:
                self.load_cog(f"core.cogs.{fname}")
            except Exception as e:
                self.logger.warning(f"Failed to load cog {fname}")

        # Ready message
        self.logger.info(f"Connected as {self.user.name}#{self.user.discriminator} "
                         f"to {len(self.guilds)} guilds and {len(self.users)} users.")
