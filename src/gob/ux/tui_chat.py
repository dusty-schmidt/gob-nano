"""TUI Chat Interface for GOB - Simple terminal chat"""

import os
import asyncio
import logging
import time
from pathlib import Path

from gob.core.memory.memory import MemoryManager

logger = logging.getLogger(__name__)


class Colors:
    """ANSI color codes for terminal output"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # User colors
    USER_FG = "\033[36;1m"       # Bold Cyan
    USER_PROMPT = "\033[36;1m"

    # Agent colors
    AGENT_FG = "\033[33;1m"      # Bold Yellow
    AGENT_PROMPT = "\033[33;1m"

    # System colors
    HEADER = "\033[35m"   # Magenta
    INFO = "\033[34m"     # Blue
    SUCCESS = "\033[32m"  # Green
    WARNING = "\033[33m"  # Yellow
    ERROR = "\033[31m"    # Red

    # Neutral
    BORDER = "\033[37m"   # White/Gray
    TEXT = "\033[0m"      # Default


def clear_screen():
    """Clear the terminal screen"""
    os.system("cls" if os.name == "nt" else "clear")


def print_banner(agent_name: str, model: str, description: str = ""):
    """Print the welcome banner"""
    name_upper = agent_name.upper()
    print(f"""{Colors.BORDER}
╔════════════════════════════════════════════════════════════════════╗
║                    {name_upper:<15} - TUI Mode                      ║
║              Ultra-minimal AI agent for edge devices                ║
╚════════════════════════════════════════════════════════════════════╝{Colors.RESET}

  Agent: {Colors.AGENT_FG}{agent_name}{Colors.RESET}
  Model: {Colors.INFO}{model}{Colors.RESET}
  {description}

  Commands: /help, /clear, /exit
""")


def format_message(role: str, content: str, agent_name: str = "gob", max_width: int = 70) -> str:
    """Format a chat message with word wrapping and colors"""
    if role == "user":
        prefix = f"{Colors.USER_PROMPT}You:{Colors.RESET}       "
        text_color = Colors.USER_FG
    else:
        prefix = f"{Colors.AGENT_PROMPT}{agent_name.capitalize()}:{Colors.RESET}     "
        text_color = Colors.AGENT_FG

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
    indent = " " * 13
    for i, line in enumerate(lines):
        if i == 0:
            result.append(f"{prefix}{text_color}{line}{Colors.RESET}")
        else:
            result.append(f"{indent}{text_color}{line}{Colors.RESET}")

    return "\n".join(result)


class TUIChat:
    """Simple TUI chat interface"""

    def __init__(self, orchestrator, memory: MemoryManager):
        self.orchestrator = orchestrator
        self.memory = memory
        self.conversation_id = "tui_session"
        self.running = False
        self.agent_name = orchestrator.agent.get("name", "gob")
        self.agent_desc = orchestrator.agent.get("description", "AI assistant")
        logger.info(f"TUI initialized: agent={self.agent_name}")

    def _show_help(self):
        """Show help message"""
        # Read version
        version = "0.3.0"
        try:
            version_file = Path(__file__).parent.parent.parent.parent / "VERSION"
            if version_file.exists():
                version = version_file.read_text().strip()
        except Exception:
            pass

        print(f"""
{Colors.BORDER}┌──────────────────────────────────────────────────────┐{Colors.RESET}
{Colors.BORDER}│{Colors.RESET}  {Colors.BOLD}GOB Help - Version {version}{Colors.RESET}{' ' * max(1, 35 - len(version))}{Colors.BORDER}│{Colors.RESET}
{Colors.BORDER}├──────────────────────────────────────────────────────┤{Colors.RESET}
{Colors.BORDER}│{Colors.RESET}  /help     - Show this help                          {Colors.BORDER}│{Colors.RESET}
{Colors.BORDER}│{Colors.RESET}  /clear    - Clear conversation history               {Colors.BORDER}│{Colors.RESET}
{Colors.BORDER}│{Colors.RESET}  /tools    - List available tools                     {Colors.BORDER}│{Colors.RESET}
{Colors.BORDER}│{Colors.RESET}  /status   - Show system status                      {Colors.BORDER}│{Colors.RESET}
{Colors.BORDER}│{Colors.RESET}  /prompt   - View system prompt                      {Colors.BORDER}│{Colors.RESET}
{Colors.BORDER}│{Colors.RESET}  /exit     - Exit the chat                           {Colors.BORDER}│{Colors.RESET}
{Colors.BORDER}└──────────────────────────────────────────────────────┘{Colors.RESET}
""")

    def _show_tools(self):
        """Show enabled tools"""
        info = self.orchestrator.get_agent_info()
        print(f"\n{Colors.HEADER}Enabled Tools:{Colors.RESET}")
        for tool in info.get("enabled_tools", []):
            print(f"  • {tool}")
        print()

    def _show_status(self):
        """Show system status"""
        info = self.orchestrator.get_agent_info()
        print(f"\n{Colors.INFO}Agent:{Colors.RESET} {info['name']}")
        print(f"{Colors.INFO}Model:{Colors.RESET} {self.orchestrator.llm.chat_model}")
        print(f"{Colors.INFO}Max iterations:{Colors.RESET} {info['max_iterations']}")
        print(f"{Colors.INFO}Tools:{Colors.RESET} {len(info['enabled_tools'])}")
        print()

    def _show_prompt(self):
        """Show the system prompt"""
        prompt = self.orchestrator.get_system_prompt()
        print(f"\n{Colors.DIM}{prompt}{Colors.RESET}\n")

    def _clear_history(self):
        """Clear conversation history"""
        self.conversation_id = f"tui_session_{int(time.time())}"
        self.orchestrator.messages = []  # Reset LLM context too
        print(f"{Colors.SUCCESS}Conversation history cleared.{Colors.RESET}")

    def _process_command(self, cmd: str) -> bool:
        """Process a slash command. Returns True if should continue."""
        cmd = cmd.lower().strip()

        if cmd in ("/exit", "/quit"):
            print(f"\n{Colors.INFO}Goodbye from {self.agent_name}!{Colors.RESET}")
            self.running = False
            return False
        elif cmd == "/help":
            self._show_help()
        elif cmd == "/clear":
            self._clear_history()
        elif cmd == "/tools":
            self._show_tools()
        elif cmd == "/status":
            self._show_status()
        elif cmd == "/prompt":
            self._show_prompt()
        else:
            print(f"{Colors.ERROR}Unknown command: {cmd}. Type /help for options.{Colors.RESET}")

        return True

    def run(self):
        """Run the TUI chat loop"""
        clear_screen()
        print_banner(self.agent_name, self.orchestrator.llm.chat_model, self.agent_desc)

        # Load previous session history
        self.orchestrator.load_session_history(self.conversation_id)
        msg_count = len(self.orchestrator.messages) - 1  # subtract system prompt
        if msg_count > 0:
            print(f"{Colors.INFO}Restored {msg_count} messages from previous session.{Colors.RESET}")
        print(f"{Colors.SUCCESS}{self.agent_name} is ready! Type /help for commands or start chatting.{Colors.RESET}\n")

        self.running = True

        while self.running:
            try:
                user_input = input(f"{Colors.USER_PROMPT}You:{Colors.RESET}       ").strip()

                if not user_input:
                    continue

                # Commands
                if user_input.startswith("/"):
                    if not self._process_command(user_input):
                        break
                    continue

                # Process message
                try:
                    start_time = time.time()
                    response = asyncio.run(
                        self.orchestrator.process_message(user_input, self.conversation_id)
                    )
                    elapsed = time.time() - start_time

                    # Display response
                    formatted = format_message("assistant", response, self.agent_name)
                    print(formatted)
                    print(f"{Colors.DIM}({elapsed:.1f}s){Colors.RESET}\n")

                    # Save to memory
                    self.memory.add_conversation(self.conversation_id, "user", user_input)
                    self.memory.add_conversation(self.conversation_id, "assistant", response)

                except Exception as e:
                    print(f"{Colors.ERROR}Error: {e}{Colors.RESET}\n")
                    logger.error(f"Message processing failed: {e}", exc_info=True)

            except KeyboardInterrupt:
                print(f"\n{Colors.INFO}Goodbye from {self.agent_name}!{Colors.RESET}")
                self.running = False
            except EOFError:
                self.running = False