import os
import logging
import dataset

import discord
from discord.ext import commands

class RadioStreamer(commands.Bot):
    def __init__(self):
        self.logger = logging.getLogger("BOT")
        self.db = dataset.connect("sqlite:///MAIN_DB.db")

        super().__init__(command_prefix="r!")

    def _get_prefix(ctx, msg):
        return

    async def on_ready(self):
        # Load every cog
        for fname in os.listdir(os.path.join("core", "cogs")):
            if not fname.endswith('.py'): continue
            try:
                self.load_extension(f"core.cogs.{fname[:-3]}")
            except Exception as e:
                self.logger.warning(f"Failed to load cog {fname}. Error: {e}")

        # Ready message
        self.logger.critical(f"Connected as {self.user.name}#{self.user.discriminator} "
                         f"to {len(self.guilds)} guilds and {len(self.users)} users.")
