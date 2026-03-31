"""TUI Chat Interface for GOB - Simple terminal chat"""

import os
import asyncio
import logging
import time

from src.gob.core.memory.memory import MemoryManager
from src.gob.orchestrator import AgentOrchestrator

logger = logging.getLogger(__name__)

# Chat logger that outputs to screen for debugging
def log_to_tui(level, message):
    """Log message to chat screen for debugging"""
    timestamp = time.strftime('%H:%M:%S')
    # Use the logger module's log_to_chat function
    from gob.core.logger import log_to_chat
    log_to_chat(level, f"[{timestamp}] {level}: {message}")
    # Also print to console for immediate feedback
    print(f"{Colors.INFO}[{timestamp}] {level}: {message}{Colors.RESET}")
    print(f"{Colors.INFO}[{timestamp}] {level}: {message}{Colors.RESET}")


class Colors:
    """ANSI color codes for terminal output"""
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

  Commands: /help, /clear, /restart, /tools, /status, /prompt, /exit
"""
    log_to_chat("INFO", f"\\n{banner}")
    print(banner)
    print(banner)
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
        logger.info(f"TUI chat initialized with agent: {self.agent_name}")

    def _show_help(self):
        """Show clean, modern help message with version info"""
        # Read version from VERSION file
        version = "0.2.2"  # Default fallback
        try:
            with open('/a0/usr/projects/gob/VERSION', 'r') as f:
                version = f.read().strip()
        except:
            pass

        help_text = f"""
{Colors.BORDER}┌──────────────────────────────────────────────────────┐{Colors.RESET}
{Colors.BORDER}│{Colors.RESET}  {Colors.BOLD}GOB Help - Version {version}{Colors.RESET}{' ' * (35 - len(version))}{Colors.BORDER}│{Colors.RESET}
{Colors.BORDER}├──────────────────────────────────────────────────────┤{Colors.RESET}
{Colors.BORDER}│{Colors.RESET}  {Colors.HEADER}Chat Commands{Colors.RESET}{' ' * (42 - len('Chat Commands'))}{Colors.BORDER}│{Colors.RESET}
{Colors.BORDER}│{Colors.RESET}  • /help     - Show this help{' ' * (24)}{Colors.BORDER}│{Colors.RESET}
{Colors.BORDER}│{Colors.RESET}  • /clear    - Clear conversation history{' ' * (17)}{Colors.BORDER}│{Colors.RESET}
{Colors.BORDER}│{Colors.RESET}  • /restart  - Restart session{' ' * (23)}{Colors.BORDER}│{Colors.RESET}
{Colors.BORDER}│{Colors.RESET}  • /exit     - Exit the chat{' ' * (26)}{Colors.BORDER}│{Colors.RESET}
{Colors.BORDER}│{Colors.RESET}{' ' * 52}{Colors.BORDER}│{Colors.RESET}
{Colors.BORDER}│{Colors.RESET}  {Colors.HEADER}System Commands{Colors.RESET}{' ' * (40 - len('System Commands'))}{Colors.BORDER}│{Colors.RESET}
{Colors.BORDER}│{Colors.RESET}  • /tools    - List available tools{' ' * (20)}{Colors.BORDER}│{Colors.RESET}
{Colors.BORDER}│{Colors.RESET}  • /status   - Show system status{' ' * (21)}{Colors.BORDER}│{Colors.RESET}
{Colors.BORDER}│{Colors.RESET}  • /prompt   - View system prompt{' ' * (21)}{Colors.BORDER}│{Colors.RESET}
{Colors.BORDER}│{Colors.RESET}{' ' * 52}{Colors.BORDER}│{Colors.RESET}
{Colors.BORDER}│{Colors.RESET}  {Colors.INFO}Quick Tips{Colors.RESET}{' ' * (44 - len('Quick Tips'))}{Colors.BORDER}│{Colors.RESET}
{Colors.BORDER}│{Colors.RESET}  • Type naturally to chat with {self.agent_name}{' ' * (18 - len(self.agent_name))}{Colors.BORDER}│{Colors.RESET}
{Colors.BORDER}│{Colors.RESET}  • {self.agent_name} can search the web, run code{' ' * (25 - len(self.agent_name))}{Colors.BORDER}│{Colors.RESET}
{Colors.BORDER}│{Colors.RESET}  • All tools execute in the Docker container{' ' * (11)}{Colors.BORDER}│{Colors.RESET}
{Colors.BORDER}└──────────────────────────────────────────────────────┘{Colors.RESET}
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
  Model:             {Colors.INFO}{self.orchestrator.llm.chat_model}{Colors.RESET}
  Provider:          OpenRouter
  Max Iterations:    {agent_info['max_iterations']}
  Retry on Error:    {agent_info['retry_on_error']}
  
  Memory:            {len(self.memory.get_all())} entries
  Enabled Tools:   {len(agent_info['enabled_tools'])}
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
        logger.debug(f"Processing command: {cmd}")

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
            print_banner(self.agent_name, self.orchestrator.llm.chat_model, self.agent_desc)
            logger.info("Session restarted")

        elif cmd == "/tools":
            self._show_tools()

        elif cmd == "/status":
            self._show_status()

        elif cmd == "/prompt":
            self._show_prompt()

        else:
            print(f"{Colors.ERROR}Unknown command: {cmd}{Colors.RESET}")
            print(f"Type {Colors.INFO}/help{Colors.RESET} for available commands\n")
        
        return True

    def run(self):
        """Run the TUI chat loop"""
        clear_screen()
        print_banner(self.agent_name, self.orchestrator.llm.chat_model, self.agent_desc)
        print(f"\n{Colors.SUCCESS}{self.agent_name} is ready! Type /help for commands or start chatting.{Colors.RESET}\n")
        
        self.running = True
        logger.info("Starting TUI chat loop")

        while self.running:
            try:
                user_input = input(f"{Colors.USER_PROMPT}You:{Colors.RESET}       ").strip()
                
                if not user_input:
                    continue
                
                logger.info(f"Received user input: {user_input[:50]}...")

                # Check for commands
                if user_input.startswith("/"):
                    continue_processing = self._process_command(user_input)
                    if not continue_processing:
                        break
                else:
                    # Process user message with comprehensive logging
                    log_to_chat("INFO", f"Processing message: {user_input[:50]}...")
                    start_time = time.time()
                    
                    try:
                        log_to_chat("DEBUG", "Calling orchestrator.process_message...")
                        # Convert async call to sync for TUI
                        import asyncio
                        response = asyncio.run(self.orchestrator.process_message(user_input, self.conversation_id))
                        total_time = time.time() - start_time
                        log_to_chat("INFO", f"Response received in {total_time:.1f}s")
                        
                        # Format and print the response
                        formatted_response = format_message("assistant", response, self.agent_name)
                        print(formatted_response)
                        
                        # Add to conversation memory
                        self.memory.add_conversation(self.conversation_id, "user", user_input)
                        self.memory.add_conversation(self.conversation_id, "assistant", response)
                        
                    except Exception as e:
                        error_time = time.time() - start_time
                        log_to_chat("ERROR", f"Failed to process message after {error_time:.1f}s: {e}")
                        error_msg = format_message("assistant", f"❌ Error: {str(e)}", self.agent_name)
                        print(error_msg)

            except KeyboardInterrupt:
                print(f"\n{Colors.SUCCESS}Goodbye from {self.agent_name}!{Colors.RESET}")
                self.running = False
            except Exception as e:
                logger.error(f"Error in chat loop: {e}")
                log_to_chat("ERROR", f"Chat loop error: {e}")
                self.running = False