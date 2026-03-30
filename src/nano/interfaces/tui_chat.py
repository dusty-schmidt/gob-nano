"""TUI Chat Interface for NANO - Simple terminal chat"""
import sys
import os
from typing import Dict, Any, Optional

from src.nano.orchestrator import AgentOrchestrator
from src.nano.helpers.memory.memory import MemoryManager


def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_banner(agent_name: str, model: str):
    """Print the welcome banner"""
    banner = f"""
╔════════════════════════════════════════════════════════════════════╗
║                    GOB-NANO Agent - TUI Mode                        ║
║              Ultra-minimal AI agent for edge devices                ║
╚════════════════════════════════════════════════════════════════════╝

  Agent: {agent_name}
  Model: {model}
  
  Type your messages below. Commands:
    /help     - Show help
    /clear    - Clear conversation history
    /tools    - List available tools
    /status   - Show system status
    /exit     - Exit the chat

══════════════════════════════════════════════════════════════════════
"""
    print(banner)


def format_message(role: str, content: str, max_width: int = 70) -> str:
    """Format a chat message with word wrapping"""
    prefix = "🧑 You:      " if role == "user" else "🤖 NANO:     "

    # Simple word wrap
    words = content.split()
    lines = []
    current_line = ""

    for word in words:
        if len(current_line) + len(word) + 1 <= max_width:
            current_line += " " + word if current_line else word
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    # Add prefix to first line, indent others
    result = []
    for i, line in enumerate(lines):
        if i == 0:
            result.append(f"{prefix}{line}")
        else:
            result.append(f"{' ' * 13}{line}")

    return '\n'.join(result)


def print_response_stream(content: str):
    """Print response with typing effect (simulated)"""
    import time

    prefix = "🤖 NANO:     "
    print(prefix, end='', flush=True)

    # Print word by word for effect
    words = content.split()
    for i, word in enumerate(words):
        if i > 0:
            print(' ', end='', flush=True)
        print(word, end='', flush=True)
        # Small delay for effect (optional - can be removed for speed)
        # time.sleep(0.01)

    print()  # Final newline


class TUIChat:
    """Simple TUI chat interface"""

    def __init__(
        self,
        orchestrator: AgentOrchestrator,
        memory: MemoryManager
    ):
        self.orchestrator = orchestrator
        self.memory = memory
        self.conversation_id = "tui_session"
        self.running = False

    def _show_help(self):
        """Show help message"""
        help_text = """
📖 Available Commands:

  /help    - Show this help message
  /clear   - Clear conversation history
  /tools   - List available tools
  /status  - Show system status
  /exit    - Exit the chat

💡 Tips:
  • Just type naturally to chat with NANO
  • NANO can search the web, run code, edit files
  • Running on Arch Linux - can install packages via pacman/pip
  • All tools execute in the Docker container
"""
        print(help_text)

    def _show_tools(self):
        """Show available tools"""
        print("\n🔧 Available Tools:")
        for tool in self.orchestrator.enabled_tools:
            print(f"  • {tool}")
        print()

    def _show_status(self):
        """Show system status"""
        status = f"""
📊 System Status:

  Agent:    {self.orchestrator.agent.get('name', 'Unknown')}
  Model:    {self.orchestrator.llm.model}
  Provider: {self.orchestrator.llm.config.get('provider', 'unknown')}
  Memory:   {len(self.memory.get_all())} entries
  Tools:    {len(self.orchestrator.enabled_tools)} enabled
  
  Enabled Tools:
"""
        print(status)
        for tool in self.orchestrator.enabled_tools:
            print(f"    • {tool}")
        print()

    def _clear_history(self):
        """Clear conversation history"""
        # Note: This doesn't actually delete the memory file,
        # just starts a new conversation ID
        self.conversation_id = f"tui_session_{len(self.memory.get_all())}"
        print("🗑️  Conversation history cleared!\n")

    def _process_command(self, cmd: str) -> bool:
        """Process a slash command. Returns True if should continue."""
        cmd = cmd.lower().strip()

        if cmd == '/exit' or cmd == '/quit':
            print("\n👋 Goodbye!")
            self.running = False
            return False

        elif cmd == '/help':
            self._show_help()

        elif cmd == '/clear':
            self._clear_history()

        elif cmd == '/tools':
            self._show_tools()

        elif cmd == '/status':
            self._show_status()

        else:
            print(f"❓ Unknown command: {cmd}")
            print("   Type /help for available commands\n")

        return True

    def run(self):
        """Run the TUI chat loop"""
        self.running = True

        clear_screen()
        print_banner(
            self.orchestrator.agent.get('name', 'NANO'),
            self.orchestrator.llm.model
        )

        print("🚀 NANO is ready! Type /help for commands or start chatting.\n")

        while self.running:
            try:
                # Get user input
                user_input = input("🧑 You:      ").strip()

                if not user_input:
                    continue

                # Check for commands
                if user_input.startswith('/'):
                    if not self._process_command(user_input):
                        break
                    continue

                # Process message through orchestrator
                print("🤖 NANO:     ", end='', flush=True)

                try:
                    response = self.orchestrator.process_message(
                        user_input,
                        self.conversation_id
                    )

                    # Clear the "NANO:" line and print full response
                    print('\r' + ' ' * 50 + '\r', end='')
                    print(format_message("assistant", response))
                    print()

                except Exception as e:
                    print(f"\r❌ Error: {str(e)}\n")

            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Use /exit to quit properly.")
                continue
            except EOFError:
                print("\n👋 Goodbye!")
                break


def run_tui_chat(
    orchestrator: AgentOrchestrator,
    memory: MemoryManager
):
    """Run the TUI chat interface"""
    chat = TUIChat(orchestrator, memory)
    chat.run()
