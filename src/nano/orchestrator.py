"""Agent Orchestrator - Core reasoning and tool execution loop"""
import json
from typing import Dict, List, Any, Optional
from pathlib import Path

from src.nano.helpers.llm_client import LLMClient
from src.nano.helpers.memory.memory import MemoryManager
from src.nano.helpers.tool_loader import load_tool


class AgentOrchestrator:
    """Orchestrates agent reasoning and tool execution"""

    def __init__(
        self,
        llm_client: LLMClient,
        memory: MemoryManager,
        agent_config: Dict[str, Any],
        tools_config: Dict[str, Any]
    ):
        self.llm = llm_client
        self.memory = memory
        self.agent = agent_config
        self.enabled_tools = tools_config.get('enabled', [])
        self.max_iterations = agent_config.get('settings', {}).get('max_iterations', 5)

    def _build_system_prompt(self) -> str:
        """Build system prompt from agent configuration"""
        context = self.agent.get('context', '')
        tools_desc = self._get_tools_description()

        return f"""{context}

You have access to the following tools:
{tools_desc}

When you need to use a tool, respond with a JSON object in this format:
{{"tool": "tool_name", "params": {{"param1": "value1"}}}}

If you don't need a tool, respond normally.

Remember: You are running in a full Arch Linux container with access to:
- pacman (package manager)
- pip (Python packages)
- All standard Linux commands
- You can install packages at runtime when needed
"""

    def _get_tools_description(self) -> str:
        """Get description of available tools"""
        descriptions = []
        tool_specs = {
            'response': 'Send a text response to the user',
            'search_engine': 'Search the web for information (requires DDG package)',
            'code_execution': 'Execute Python code or terminal commands',
            'text_editor': 'Read, write, or modify files',
            'document_query': 'Read and query document contents'
        }

        for tool_name in self.enabled_tools:
            desc = tool_specs.get(tool_name, 'No description available')
            descriptions.append(f"  - {tool_name}: {desc}")

        return '\n'.join(descriptions)

    def _format_tool_for_llm(self, tool_name: str) -> Dict[str, Any]:
        """Format tool specification for LLM function calling"""
        tool_specs = {
            'search_engine': {
                "type": "function",
                "function": {
                    "name": "search_engine",
                    "description": "Search the web for information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"}
                        },
                        "required": ["query"]
                    }
                }
            },
            'code_execution': {
                "type": "function",
                "function": {
                    "name": "code_execution",
                    "description": "Execute Python code or shell commands",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string", "description": "Python code to execute"},
                            "language": {"type": "string", "enum": ["python", "bash"], "default": "python"}
                        },
                        "required": ["code"]
                    }
                }
            },
            'text_editor': {
                "type": "function",
                "function": {
                    "name": "text_editor",
                    "description": "Read, write, or modify files",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "enum": ["read", "write", "patch"]},
                            "path": {"type": "string", "description": "File path"},
                            "content": {"type": "string", "description": "Content for write/patch"}
                        },
                        "required": ["action", "path"]
                    }
                }
            },
            'document_query': {
                "type": "function",
                "function": {
                    "name": "document_query",
                    "description": "Read document contents",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Document path"}
                        },
                        "required": ["path"]
                    }
                }
            }
        }

        return tool_specs.get(tool_name)

    def _execute_tool(self, tool_name: str, params: Dict[str, Any]) -> str:
        """Execute a tool and return result"""
        try:
            tool_module = load_tool(tool_name)

            if tool_name == 'response':
                return params.get('message', 'No response provided')

            elif tool_name == 'search_engine':
                if hasattr(tool_module, 'search'):
                    return tool_module.search(params.get('query', ''))
                return "Search not implemented. Try installing duckduckgo-search via pip."

            elif tool_name == 'code_execution':
                if hasattr(tool_module, 'execute'):
                    return tool_module.execute(
                        params.get('code', ''),
                        params.get('language', 'python')
                    )
                return "Code execution not implemented."

            elif tool_name == 'text_editor':
                if hasattr(tool_module, 'read') and params.get('action') == 'read':
                    return tool_module.read(params.get('path', ''))
                elif hasattr(tool_module, 'write') and params.get('action') == 'write':
                    return tool_module.write(params.get('path', ''), params.get('content', ''))
                elif hasattr(tool_module, 'patch') and params.get('action') == 'patch':
                    return tool_module.patch(params.get('path', ''), params.get('content', ''))
                return "Text editor action not implemented."

            elif tool_name == 'document_query':
                if hasattr(tool_module, 'read_document'):
                    return tool_module.read_document(params.get('path', ''))
                return "Document query not implemented."

            return f"Tool {tool_name} not implemented"

        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"

    def process_message(self, user_message: str, conversation_id: Optional[str] = None) -> str:
        """Process a user message through the agent loop"""
        # Add user message to memory
        self.memory.add_entry({
            'role': 'user',
            'content': user_message,
            'conversation_id': conversation_id
        })

        # Build conversation history
        messages = [{'role': 'system', 'content': self._build_system_prompt()}]

        # Add recent memory entries (last 10)
        recent_entries = self.memory.get_all()[-10:]
        for entry in recent_entries:
            if 'role' in entry and 'content' in entry:
                messages.append({
                    'role': entry['role'],
                    'content': entry['content']
                })

        # Add current message if not already in history
        if not recent_entries or recent_entries[-1].get('content') != user_message:
            messages.append({'role': 'user', 'content': user_message})

        # Prepare tools for LLM
        tools = []
        for tool_name in self.enabled_tools:
            if tool_name != 'response':  # response is handled specially
                tool_spec = self._format_tool_for_llm(tool_name)
                if tool_spec:
                    tools.append(tool_spec)

        # Agent loop
        iteration = 0
        final_response = None

        while iteration < self.max_iterations:
            iteration += 1

            try:
                # Call LLM
                if tools:
                    response = self.llm.chat(messages, tools=tools)
                else:
                    response = self.llm.chat(messages)

                message = response['choices'][0]['message']

                # Check for tool calls
                if 'tool_calls' in message and message['tool_calls']:
                    tool_call = message['tool_calls'][0]
                    function = tool_call['function']
                    tool_name = function['name']

                    try:
                        params = json.loads(function['arguments'])
                    except json.JSONDecodeError:
                        params = {}

                    # Execute tool
                    result = self._execute_tool(tool_name, params)

                    # Add tool call and result to messages
                    messages.append({
                        'role': 'assistant',
                        'content': None,
                        'tool_calls': [tool_call]
                    })
                    messages.append({
                        'role': 'tool',
                        'tool_call_id': tool_call['id'],
                        'content': str(result)
                    })

                    # If it's a terminal response tool, we're done
                    if tool_name == 'response':
                        final_response = params.get('message', result)
                        break

                else:
                    # No tool call, direct response
                    final_response = message.get('content', 'No response')
                    break

            except Exception as e:
                final_response = f"Error: {str(e)}"
                break

        if final_response is None:
            final_response = "I couldn't complete the task within the iteration limit."

        # Add assistant response to memory
        self.memory.add_entry({
            'role': 'assistant',
            'content': final_response,
            'conversation_id': conversation_id
        })

        return final_response

    def process_message_stream(self, user_message: str, conversation_id: Optional[str] = None):
        """Process a message and stream the response (for TUI)"""
        # This is a simplified version for streaming
        # For now, just yield the final response
        response = self.process_message(user_message, conversation_id)
        yield response
