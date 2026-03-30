"""Discord Bot Interface for NANO"""
import asyncio
import discord
from discord.ext import commands
from typing import Dict, Any, Optional

from src.gob.orchestrator import AgentOrchestrator
from src.gob.helpers.memory.memory import MemoryManager


class NanoDiscordBot(commands.Bot):
    """Discord bot for NANO agent"""

    def __init__(
        self,
        orchestrator: AgentOrchestrator,
        memory: MemoryManager,
        config: Dict[str, Any],
        *args,
        **kwargs
    ):
        # Configure intents
        # Note: message_content is required for the bot to read message content
        # You must enable it in Discord Developer Portal > Bot > Privileged Gateway Intents
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix=config.get('prefix', '!'),
            intents=intents,
            *args,
            **kwargs
        )

        self.orchestrator = orchestrator
        self.memory = memory
        self.config = config
        self.conversation_contexts: Dict[int, str] = {}  # channel_id -> conversation_id

    async def on_ready(self):
        """Called when bot is ready"""
        print(f"🤖 Discord bot logged in as {self.user}")
        print(f"   Bot ID: {self.user.id}")
        print(f"   Prefix: {self.command_prefix}")
        print(f"   Connected to {len(self.guilds)} guilds")

        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="for messages | !help"
        )
        await self.change_presence(activity=activity)

    async def on_message(self, message: discord.Message):
        """Handle incoming messages"""
        # Ignore bot's own messages
        if message.author == self.user:
            return

        # Check if message is a command
        if message.content.startswith(self.command_prefix):
            await self.process_commands(message)
            return

        # Handle DMs (always respond)
        if isinstance(message.channel, discord.DMChannel):
            await self._handle_conversation(message)
            return

        # Handle mentions in guild channels
        if self.user in message.mentions:
            await self._handle_conversation(message)
            return

    async def _handle_conversation(self, message: discord.Message):
        """Handle a conversation message"""
        # Get or create conversation ID for this channel/user
        channel_id = message.channel.id
        if channel_id not in self.conversation_contexts:
            self.conversation_contexts[channel_id] = f"discord_{channel_id}"

        conversation_id = self.conversation_contexts[channel_id]

        # Show typing indicator
        async with message.channel.typing():
            try:
                # Process message through orchestrator
                response = await asyncio.to_thread(
                    self.orchestrator.process_message,
                    message.content,
                    conversation_id
                )

                # Send response (split if too long)
                if len(response) > 2000:
                    # Split into chunks
                    chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
                    for chunk in chunks:
                        await message.reply(chunk)
                else:
                    await message.reply(response)

            except Exception as e:
                await message.reply(f"❌ Error processing your request: {str(e)}")

    @commands.command(name='help')
    async def help_command(self, ctx: commands.Context):
        """Show help information"""
        embed = discord.Embed(
            title="🤖 GOB-GOB Agent",
            description="Your minimal AI assistant for edge devices",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="How to use",
            value="Mention me (@gob) or DM me to start a conversation",
            inline=False
        )

        embed.add_field(
            name="Commands",
            value=(
                f"`{self.command_prefix}help` - Show this message\n"
                f"`{self.command_prefix}clear` - Clear conversation history\n"
                f"`{self.command_prefix}status` - Show bot status"
            ),
            inline=False
        )

        embed.add_field(
            name="Capabilities",
            value=(
                "• Web search\n"
                "• Code execution (Python/bash)\n"
                "• File editing\n"
                "• Document reading\n"
                "• Package installation (pacman/pip)"
            ),
            inline=False
        )

        embed.set_footer(text="Running on Arch Linux with 'Computer as a Tool' philosophy")

        await ctx.send(embed=embed)

    @commands.command(name='clear')
    async def clear_command(self, ctx: commands.Context):
        """Clear conversation history for this channel"""
        channel_id = ctx.channel.id
        if channel_id in self.conversation_contexts:
            del self.conversation_contexts[channel_id]
            await ctx.send("🗑️ Conversation history cleared!")
        else:
            await ctx.send("No conversation history to clear.")

    @commands.command(name='status')
    async def status_command(self, ctx: commands.Context):
        """Show bot status"""
        embed = discord.Embed(
            title="📊 Bot Status",
            color=discord.Color.green()
        )

        embed.add_field(name="Model", value=self.orchestrator.llm.model, inline=True)
        embed.add_field(name="Agent", value=self.orchestrator.agent.get('name', 'Unknown'), inline=True)
        embed.add_field(name="Active Conversations", value=len(self.conversation_contexts), inline=True)

        enabled_tools = ', '.join(self.orchestrator.enabled_tools)
        embed.add_field(name="Enabled Tools", value=enabled_tools, inline=False)

        await ctx.send(embed=embed)


def run_discord_bot(
    orchestrator: AgentOrchestrator,
    memory: MemoryManager,
    config: Dict[str, Any]
):
    """Run the Discord bot"""
    token = config.get('token')
    if not token or token.startswith('your_'):
        raise ValueError("Discord bot token not configured. Set DISCORD_BOT_TOKEN in .env")

    bot = NanoDiscordBot(orchestrator, memory, config)
    bot.run(token)
