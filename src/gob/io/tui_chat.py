"""TUI Chat Interface for GOB - Simple terminal chat"""

import os
import asyncio

from src.gob.core.memory.memory import MemoryManager
from src.gob.orchestrator import AgentOrchestrator


class Colors:
    """ANSI color codes for terminal output"""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # User colors - Perfectly matched Bold Cyan
    USER_FG = "\033[36;1m"
    USER_PROMPT = "\033[36;1m"

    # Agent colors - Perfectly matched Bold Yellow
    AGENT_FG = "\033[33;1m"
    AGENT_PROMPT = "\033[33;1m"

    # System colors
    HEADER = "\033[35m"  # Magenta
    INFO = "\033[34m"  # Blue
    SUCCESS = "\033[32m"  # Green
    WARNING = "\033[33m"  # Yellow
    ERROR = "\033[31m"  # Red

    # Neutral
    BORDER = "\033[37m"  # White/Gray
    TEXT = "\033[0m"  # Default


def clear_screen():
    """Clear the terminal screen"""
    os.system("cls" if os.name == "nt" else "clear")


def print_banner(agent_name: str, model: str, description: str = ""):
    """Print the welcome banner"""
    name_upper = agent_name.upper()
    banner = f"""{Colors.BORDER}
╔════════════════════════════════════════════════════════════════════╗
║                    {name_upper:<15} - TUI Mode                      ║
║              Ultra-minimal AI agent for edge devices                ║
╚════════════════════════════════════════════════════════════════════╝{Colors.RESET}

  Agent: {Colors.AGENT_FG}{agent_name}{Colors.RESET}
  Model: {Colors.INFO}{model}{Colors.RESET}
  {description}
  
  Type your messages below. Commands:
    /help     - Show help
    /clear    - Clear conversation history
    /restart  - Restart session and clear screen
    /tools    - List available tools
    /status   - Show system status
    /prompt   - View system prompt
    /exit     - Exit the chat

{Colors.BORDER}══════════════════════════════════════════════════════════════════════{Colors.RESET}
"""
    print(banner)


def format_message(
    role: str, content: str, agent_name: str = "gob", max_width: int = 70
) -> str:
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
    for i, line in enumerate(lines):
        if i == 0:
            result.append(f"{prefix}{text_color}{line}{Colors.RESET}")
        else:
            result.append(f"{' ' * 13}{text_color}{line}{Colors.RESET}")

    return "\n".join(result)


class TUIChat:
    """Simple TUI chat interface"""

    def __init__(self, orchestrator: AgentOrchestrator, memory: MemoryManager):
        self.orchestrator = orchestrator
        self.memory = memory
        self.conversation_id = "tui_session"
        self.running = False
        self.agent_name = orchestrator.agent.get("name", "gob")
        self.agent_desc = orchestrator.agent.get("description", "AI assistant")

    def _show_help(self):
        """Show help message"""
        help_text = f"""
{Colors.HEADER}Available Commands:{Colors.RESET}

  /help    - Show this help message
  /clear   - Clear conversation history
  /restart - Restart session and clear screen
  /tools   - List available tools
  /status  - Show system status
  /prompt  - View system prompt
  /exit    - Exit the chat

{Colors.INFO}Tips:{Colors.RESET}
  • Just type naturally to chat with {self.agent_name}
  • {self.agent_name} can search the web, run code, edit files
  • Running on Arch Linux - can install packages via pacman/pip
  • All tools execute in the Docker container
"""
        print(help_text)

    def _show_tools(self):
        """Show available tools"""
        agent_info = self.orchestrator.get_agent_info()
        print(
            f"\n{Colors.HEADER}Available Tools ({len(agent_info['enabled_tools'])}):{Colors.RESET}"
        )
        for tool in agent_info["enabled_tools"]:
            print(f"  • {tool}")
        print()

    def _show_status(self):
        """Show system status"""
        agent_info = self.orchestrator.get_agent_info()

        status = f"""
{Colors.HEADER}System Status:{Colors.RESET}

  Agent Name:        {Colors.AGENT_FG}{agent_info['name']}{Colors.RESET}
  Description:       {agent_info['description']}
  Model:             {Colors.INFO}{self.orchestrator.llm.chat.model}{Colors.RESET}
  Provider:          OpenRouter
  Max Iterations:    {agent_info['max_iterations']}
  Retry on Error:    {agent_info['retry_on_error']}
  
  Memory:            {len(self.memory.get_all())} entries
  Enabled Tools:     {len(agent_info['enabled_tools'])}
"""
        print(status)

        print("  Tools:")
        for tool in agent_info["enabled_tools"]:
            print(f"    • {tool}")

        print()

    def _show_prompt(self):
        """Show the current system prompt"""
        print(f"\n{Colors.HEADER}System Prompt:{Colors.RESET}\n")
        print(f"{Colors.BORDER}{'═' * 70}{Colors.RESET}")
        print(self.orchestrator.get_system_prompt())
        print(f"{Colors.BORDER}{'═' * 70}{Colors.RESET}")
        print()

    def _clear_history(self):
        """Clear conversation history"""
        self.conversation_id = f"tui_session_{len(self.memory.get_all())}"
        print(
            f"{Colors.SUCCESS}Conversation history cleared for {self.agent_name}!{Colors.RESET}\n"
        )

    def _process_command(self, cmd: str) -> bool:
        """Process a slash command. Returns True if should continue."""
        cmd = cmd.lower().strip()

        if cmd == "/exit" or cmd == "/quit":
            print(f"\n{Colors.SUCCESS}Goodbye from {self.agent_name}!{Colors.RESET}")
            self.running = False
            return False

        elif cmd == "/help":
            self._show_help()

        elif cmd == "/clear":
            self._clear_history()

        elif cmd == "/restart":
            clear_screen()
            self._clear_history()
            print_banner(self.agent_name, self.orchestrator.llm.chat.model, self.agent_desc)
            print(
                f"{Colors.SUCCESS}{self.agent_name.capitalize()} restarted!{Colors.RESET} How can I help you?\n"
            )

        elif cmd == "/tools":
            self._show_tools()

        elif cmd == "/status":
            self._show_status()

        elif cmd == "/prompt":
            self._show_prompt()

        else:
            print(f"{Colors.ERROR}Unknown command: {cmd}{Colors.RESET}")
            print("   Type /help for available commands\n")

        return True

    def run(self):
        """Run the TUI chat loop"""
        self.running = True

        clear_screen()
        print_banner(self.agent_name, self.orchestrator.llm.chat.model, self.agent_desc)

        print(
            f"{Colors.SUCCESS}{self.agent_name.capitalize()} is ready!{Colors.RESET} Type /help for commands or start chatting.\n"
        )

        while self.running:
            try:
                # Get user input with colored prompt
                user_input = input(
                    f"{Colors.USER_PROMPT}You:{Colors.RESET}       "
                ).strip()

                if not user_input:
                    continue

                # Add newline after user input for spacing
                print()

                # Check for commands
                if user_input.startswith("/"):
                    if not self._process_command(user_input):
                        break
                    continue
                
                # Process message through orchestrator (async call wrapped in sync context)
                try:
                    response = asyncio.run(self.orchestrator.process_message(user_input, self.conversation_id))

                    # Format and print response
                    print(format_message("assistant", response, self.agent_name))
                    print()  # Extra newline after response

                except Exception as e:
                    print(f"{Colors.ERROR}Error: {str(e)}{Colors.RESET}\n")

            except KeyboardInterrupt:
                print(
                    f"\n\n{Colors.WARNING}Interrupted. Use /exit to quit properly.{Colors.RESET}"
                )
                continue
            except EOFError:
                print(
                    f"{Colors.SUCCESS}Goodbye from {self.agent_name}!{Colors.RESET}"
                )
                break


def run_tui_chat(orchestrator: AgentOrchestrator, memory: MemoryManager):
    """Run the TUI chat interface"""
    chat = TUIChat(orchestrator, memory)
    chat.run()