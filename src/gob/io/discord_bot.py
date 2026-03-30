import discord
from discord.ext import commands
import logging
import time

logger = logging.getLogger(__name__)

class GobDiscordBot(commands.Bot):
    def __init__(self, config, memory, llm_client):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.messages = True
        super().__init__(command_prefix="!", intents=intents)
        self.config = config
        self.memory = memory
        self.llm_client = llm_client
        self.last_message_time = {}  # Rate limiting: user_id -> timestamp
        self.rate_limit_window = 2.0  # 2 seconds cooldown

    async def on_ready(self):
        logger.info(f"Logged in as {self.user}")

    async def on_message(self, message):
        # Ignore bot's own messages
        if message.author == self.user:
            return

        # Rate limiting check
        current_time = time.time()
        user_id = message.author.id
        if user_id in self.last_message_time:
            if current_time - self.last_message_time[user_id] < self.rate_limit_window:
                return  # Ignore message if too soon
        self.last_message_time[user_id] = current_time

        # Handle commands
        if message.content.startswith(self.command_prefix):
            await self.process_commands(message)
            return

        # Handle DMs
        if isinstance(message.channel, discord.DMChannel):
            await self._handle_conversation(message)
            return

        # Handle mentions
        if self.user in message.mentions:
            await self._handle_conversation(message)

    async def _handle_conversation(self, message):
        # Placeholder for conversation logic
        pass
