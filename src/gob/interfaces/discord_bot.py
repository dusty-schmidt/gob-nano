"""Discord Bot Interface for GOB"""

import asyncio
from typing import Any, Dict, Optional

import discord
from discord.ext import commands

from src.gob.helpers.memory.memory import MemoryManager
from src.gob.orchestrator import AgentOrchestrator


class GobDiscordBot(commands.Bot):
    """Discord bot for GOB agent"""

    def __init__(
        self,
        orchestrator: AgentOrchestrator,
        memory: MemoryManager,
        config: Dict[str, Any],
        *args,
        **kwargs,
    ):
        # Configure intents
        # Note: message_content is required for the bot to read message content
        # You must enable it in Discord Developer Portal > Bot > Privileged Gateway Intents
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix=config.get("prefix", "!"), intents=intents, *args, **kwargs
        )

        self.orchestrator = orchestrator
        self.memory = memory
        self.config = config
        self.conversation_contexts: Dict[int, str] = {}  # channel_id -> conversation_id
        self.guild_contexts: Dict[int, Dict[str, int]] = (
            {}
        )  # guild_id -> {channel_name: channel_id}
        self.active_guild_id: Optional[int] = None  # Track current guild for posting

        # Set orchestrator callbacks for Discord integration
        self.orchestrator.on_thinking = self._handle_thinking
        self.orchestrator.on_result = self._handle_result
        self.orchestrator.on_tool_execute = self._handle_tool_execute

    async def on_ready(self):
        """Called when bot is ready"""
        print(f"🤖 Discord bot logged in as {self.user}")
        print(f"   Bot ID: {self.user.id}")
        print(f"   Prefix: {self.command_prefix}")
        print(f"   Connected to {len(self.guilds)} guilds")

        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.watching, name="for messages | !help"
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

    async def _handle_thinking(self, thinking: str):
        """Handle thinking callback from orchestrator"""
        if self.active_guild_id:
            await self.post_thinking(self.active_guild_id, thinking)

    async def _handle_result(self, title: str, content: str):
        """Handle result callback from orchestrator"""
        if self.active_guild_id:
            await self.post_result(self.active_guild_id, title, content)

    async def _handle_tool_execute(self, tool_name: str, params: Dict[str, Any]):
        """Handle tool execution callback from orchestrator"""
        if self.active_guild_id:
            message = f"🔧 Using tool: **{tool_name}**"
            await self.post_thinking(self.active_guild_id, message)

    async def _handle_conversation(self, message: discord.Message):
        """Handle a conversation message"""
        # Get or create conversation ID for this channel/user
        channel_id = message.channel.id
        if channel_id not in self.conversation_contexts:
            self.conversation_contexts[channel_id] = f"discord_{channel_id}"

        conversation_id = self.conversation_contexts[channel_id]

        # Set active guild for callbacks
        if isinstance(message.guild, discord.Guild):
            self.active_guild_id = message.guild.id

        # Show typing indicator
        async with message.channel.typing():
            try:
                # Process message through orchestrator
                response = await asyncio.to_thread(
                    self.orchestrator.process_message, message.content, conversation_id
                )

                # Send response (split if too long)
                if len(response) > 2000:
                    # Split into chunks
                    chunks = [
                        response[i : i + 1900] for i in range(0, len(response), 1900)
                    ]
                    for chunk in chunks:
                        await message.reply(chunk)
                else:
                    await message.reply(response)

            except Exception as e:
                await message.reply(f"❌ Error processing your request: {str(e)}")
            finally:
                # Clear active guild
                self.active_guild_id = None

    @commands.command(name="help")
    async def help_command(self, ctx: commands.Context):
        """Show help information"""
        embed = discord.Embed(
            title="🤖 GOB Agent",
            description="Your minimal AI assistant for edge devices",
            color=discord.Color.blue(),
        )

        embed.add_field(
            name="How to use",
            value="Mention me (@gob) or DM me to start a conversation",
            inline=False,
        )

        embed.add_field(
            name="Commands",
            value=(
                f"`{self.command_prefix}help` - Show this message\n"
                f"`{self.command_prefix}clear` - Clear conversation history\n"
                f"`{self.command_prefix}status` - Show bot status"
            ),
            inline=False,
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
            inline=False,
        )

        embed.set_footer(
            text="Running on Arch Linux with 'Computer as a Tool' philosophy"
        )

        await ctx.send(embed=embed)

    @commands.command(name="clear")
    async def clear_command(self, ctx: commands.Context):
        """Clear conversation history for this channel"""
        channel_id = ctx.channel.id
        if channel_id in self.conversation_contexts:
            del self.conversation_contexts[channel_id]
            await ctx.send("🗑️ Conversation history cleared!")
        else:
            await ctx.send("No conversation history to clear.")

    @commands.command(name="status")
    async def status_command(self, ctx: commands.Context):
        """Show bot status"""
        embed = discord.Embed(title="📊 Bot Status", color=discord.Color.green())

        embed.add_field(name="Model", value=self.orchestrator.llm.model, inline=True)
        embed.add_field(
            name="Agent",
            value=self.orchestrator.agent.get("name", "Unknown"),
            inline=True,
        )
        embed.add_field(
            name="Active Conversations",
            value=len(self.conversation_contexts),
            inline=True,
        )

        enabled_tools = ", ".join(self.orchestrator.enabled_tools)
        embed.add_field(name="Enabled Tools", value=enabled_tools, inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="setup_project")
    @commands.is_owner()
    async def setup_project(self, ctx: commands.Context, project_name: str):
        """Create a new project server with automated channels"""
        try:
            # Create guild
            guild = await self.user.create_guild(
                name=f"{project_name} - GOB Workspace",
                region=discord.VoiceRegion.us_west,
            )

            # Create categories and channels
            tasks_category = await guild.create_category("📋 Tasks & Work")
            collab_category = await guild.create_category("💬 Collaboration")
            results_category = await guild.create_category("📊 Results")

            # Tasks channels
            await guild.create_text_channel(
                name="todo",
                category=tasks_category,
                topic="Todo items - React 👀 when working, ✅ when done",
            )
            await guild.create_text_channel(
                name="in-progress",
                category=tasks_category,
                topic="Currently being worked on",
            )
            await guild.create_text_channel(
                name="completed",
                category=tasks_category,
                topic="Completed items and achievements",
            )

            # Collaboration channels
            await guild.create_text_channel(
                name="discussions",
                category=collab_category,
                topic="Team discussions and brainstorming",
            )
            await guild.create_text_channel(
                name="questions",
                category=collab_category,
                topic="Ask @GOB questions - mention to get response",
            )
            await guild.create_text_channel(
                name="agents-thinking",
                category=collab_category,
                topic="GOB's reasoning and thought process",
            )

            # Results channels
            await guild.create_text_channel(
                name="results",
                category=results_category,
                topic="Task completion reports and outputs",
            )
            await guild.create_text_channel(
                name="code-snippets",
                category=results_category,
                topic="Code generated by GOB",
            )
            await guild.create_text_channel(
                name="file-updates",
                category=results_category,
                topic="File changes and workdir sync status",
            )

            # Store guild context
            self.guild_contexts[guild.id] = {}

            # Create invite
            invite = await guild.default_channel.create_invite(max_age=0)

            await ctx.send(
                f"✅ **Created project server: {guild.name}**\n"
                f"📎 Invite link: {invite.url}\n\n"
                f"**Channels created:**\n"
                f"📋 **Tasks**: #todo, #in-progress, #completed\n"
                f"💬 **Collaboration**: #discussions, #questions, #agents-thinking\n"
                f"📊 **Results**: #results, #code-snippets, #file-updates"
            )
        except Exception as e:
            await ctx.send(f"❌ Error creating project server: {str(e)}")

    async def post_to_channel(self, guild_id: int, channel_name: str, content: str):
        """Post message to a specific channel in a guild"""
        try:
            guild = self.get_guild(guild_id)
            if not guild:
                return

            channel = discord.utils.get(guild.text_channels, name=channel_name)
            if channel:
                if len(content) > 2000:
                    chunks = [
                        content[i : i + 1900] for i in range(0, len(content), 1900)
                    ]
                    for chunk in chunks:
                        await channel.send(chunk)
                else:
                    await channel.send(content)
        except Exception as e:
            print(f"Error posting to {channel_name}: {str(e)}")

    async def post_thinking(self, guild_id: int, thinking: str):
        """Post agent thinking to #agents-thinking"""
        await self.post_to_channel(guild_id, "agents-thinking", f"🧠 {thinking}")

    async def post_result(self, guild_id: int, title: str, content: str):
        """Post task result to #results"""
        message = f"✅ **{title}**\n{content}"
        await self.post_to_channel(guild_id, "results", message)


def run_discord_bot(
    orchestrator: AgentOrchestrator, memory: MemoryManager, config: Dict[str, Any]
):
    """Run the Discord bot"""
    token = config.get("token")
    if not token or token.startswith("your_"):
        raise ValueError(
            "Discord bot token not configured. Set DISCORD_BOT_TOKEN in .env"
        )

    bot = GobDiscordBot(orchestrator, memory, config)
