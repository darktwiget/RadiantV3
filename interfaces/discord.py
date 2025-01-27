import discord
from discord.ext import commands
import json
import logging
import os
import random
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import dotenv
import yaml
from agents.core_agent import CoreAgent
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dotenv.load_dotenv()

    
class DiscordAgent(CoreAgent):
    def __init__(self, loop: Optional[Any] = None):
        super().__init__()
        self.loop = loop or asyncio.get_event_loop()

        # Define Discord intents and initialize the bot

        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        intents.typing = False
        intents.presences = False


        self.bot = commands.Bot(command_prefix=os.getenv("COMMAND_PREFIX", "!"), intents=intents)
        self.token = os.getenv("DISCORD_TOKEN")
        
        self.setup_handlers()

    def setup_handlers(self) -> None:
        @self.bot.event
        async def on_ready():
            logger.info(f"Bot is ready and logged in as {self.bot.user}")

        @self.bot.hybrid_command(name="hello", with_app_command=True, description="Say hello to the bot!")

        async def hello(ctx: commands.Context):
            await ctx.send(f"Hello {ctx.author.display_name}! How can I help you?")

        @self.bot.command(name="uptime", help="Check bot uptime")
        async def uptime(ctx):
            current_time = datetime.utcnow()
            uptime_duration = current_time - self.start_time
            await ctx.send(f"Bot uptime: {uptime_duration}")

        @self.bot.event
        async def on_message(message):
            # Ignore bot's own messages
            if message.author == self.bot.user:
                return

            try:
                # Get user message
                user_message = message.content.strip().lower()

                text_response, image_url, extra_data = await self.handle_message(user_message)
                logger.debug(f"Extra data returned from handle_message: {extra_data}")
                text_response, image_url, _ = await self.handle_message(user_message)

                if image_url:
                    embed = discord.Embed(title="Here you go!", color=discord.Color.blue())
                    embed.set_image(url=image_url)
                    await message.channel.send(embed=embed)
                elif text_response:
                    await message.channel.send(text_response)
                else:
                    await message.channel.send("Sorry, I couldn't process your message.", delete_after=10)

            except discord.DiscordException as e:
                logger.error(f"Discord error occurred: {str(e)}")
                await message.channel.send("A Discord-related error occurred.")
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                await message.channel.send("Sorry, I encountered an error processing your message.")

            # Ensure other commands still work
            await self.bot.process_commands(message)

        # Command: Simple echo function
        @self.bot.command()
        async def echo(ctx, *, message: str):
            await ctx.send(f"You said: {message}", allowed_mentions=discord.AllowedMentions.none())

    def run(self) -> None:
        self.bot.run(self.token)
