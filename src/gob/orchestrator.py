"""Agent Orchestrator - Core reasoning and tool execution loop"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.gob.helpers.llm_client import LLMClient
from src.gob.helpers.memory.memory import MemoryManager
from src.gob.helpers.tool_loader import load_tool


class AgentOrchestrator:
    """Orchestrates agent reasoning and tool execution"""

    def __init__(
        self,
        llm_client: LLMClient,
        memory: MemoryManager,
        agent_config: Dict[str, Any],
        tools_config: Dict[str, Any],
    ):
        self.llm = llm_client
        self.memory = memory
        self.agent = agent_config


        # Extract enabled tools from agent config or tools config
        # Agent config takes precedence
        agent_tools = agent_config.get("tools", [])
        config_tools = tools_config.get("enabled", [])
        self.enabled_tools = agent_tools if agent_tools else config_tools

        # Get settings from agent config
        agent_settings = agent_config.get("settings", {})
        self.max_iterations = agent_settings.get("max_iterations", 5)
        self.retry_on_error = agent_settings.get("retry_on_error", True)
        self.auto_suggest_tools = agent_settings.get("auto_suggest_tools", False)

        # Get preferences
        self.preferences = agent_config.get("preferences", {})

        # Build and cache system prompt
        self._system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        """Build system prompt from agent configuration"""
        # Get context from agent config (the system prompt)
        context = self.agent.get("context", "")

        # Get agent metadata
        agent_name = self.agent.get("name", "GOB-NANO")
        agent_desc = self.agent.get("description", "AI assistant")

        # Build tools description
        tools_desc = self._get_tools_description()

        # Get preferences
        verbose = self.preferences.get("verbose_outputs", False)
        include_timestamps = self.preferences.get("include_timestamps", True)

        # Construct the system prompt
        system_prompt_parts = []

        # Add agent identity
        if context:
            system_prompt_parts.append(context.strip())
        else:
            system_prompt_parts.append(f"You are {agent_name}, {agent_desc}.")

        # Add available tools info
        if tools_desc:
            system_prompt_parts.append(f"\nYou have access to the following tools:")
            system_prompt_parts.append(tools_desc)

        # Add environment info
        system_prompt_parts.append("""
Environment Info:
- You are running in a full Arch Linux container
- You have access to: pacman (package manager), pip (Python packages), all standard Linux commands
- You can install packages at runtime when needed via 'pip install <package>' or 'pacman -S <package>'
- You can read/write files, execute code, search the web, and query documents
""")

        # Add behavior guidelines based on preferences
        behavior_parts = []
        if not verbose:
            behavior_parts.append("Be concise and direct in your responses.")
        if include_timestamps:
            behavior_parts.append("Include timestamps when relevant.")

        if behavior_parts:
            system_prompt_parts.append("\nBehavior Guidelines:")
            system_prompt_parts.append(" ".join(behavior_parts))

        # Add tool usage format
        system_prompt_parts.append("""
Tool Usage:
When you need to use a tool, respond with a JSON object:
{"tool": "tool_name", "params": {"param1": "value1"}}

If you don't need a tool, respond normally in plain text.
""")

        return "\n".join(system_prompt_parts).strip()

    def _get_tools_description(self) -> str:
        """Get description of available tools"""
        descriptions = []
        tool_specs = {
            "response": "Send a text response to the user",
            "search_engine": "Search the web for information using DuckDuckGo (auto-installs if needed)",
            "code_execution": "Execute Python code or bash commands in the container",
            "text_editor": "Read, write, or modify files (read, write, patch actions)",
            "document_query": "Read and parse document contents (txt, md, json, etc.)",
        }

        for tool_name in self.enabled_tools:
            desc = tool_specs.get(tool_name, "No description available")
            descriptions.append(f"  • {tool_name}: {desc}")

        return "\n".join(descriptions) if descriptions else "No tools configured."

    def _format_tool_for_llm(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Format tool specification for LLM function calling"""
        tool_specs = {
            "search_engine": {
                "type": "function",
                "function": {
                    "name": "search_engine",
                    "description": "Search the web for information using DuckDuckGo",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query string",
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of results (default 5)",
                                "default": 5,
                            },
                        },
                        "required": ["query"],
                    },
                },
            },
            "code_execution": {
                "type": "function",
                "function": {
                    "name": "code_execution",
                    "description": "Execute Python code or bash commands",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "Code or command to execute",
                            },
                            "language": {
                                "type": "string",
                                "enum": ["python", "bash"],
                                "description": "Language: 'python' or 'bash'",
                                "default": "python",
                            },
                        },
                        "required": ["code"],
                    },
                },
            },
            "text_editor": {
                "type": "function",
                "function": {
                    "name": "text_editor",
                    "description": "Read, write, or modify files",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["read", "write", "patch"],
                                "description": "Action to perform",
                            },
                            "path": {"type": "string", "description": "File path"},
                            "content": {
                                "type": "string",
                                "description": "Content for write/patch operations",
                            },
                        },
                        "required": ["action", "path"],
                    },
                },
            },
            "document_query": {
                "type": "function",
                "function": {
                    "name": "document_query",
                    "description": "Read document contents",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Path to document file",
                            }
                        },
                        "required": ["path"],
                    },
                },
            },
        }

        return tool_specs.get(tool_name)

    def _execute_tool(self, tool_name: str, params: Dict[str, Any]) -> str:
        """Execute a tool and return result"""
        try:
            tool_module = load_tool(tool_name)

            if tool_name == "response":
                return params.get(
                    "message", params.get("content", "No response provided")
                )

            elif tool_name == "search_engine":
                query = params.get("query", "")
                max_results = params.get("max_results", 5)

                if hasattr(tool_module, "search"):
                    return tool_module.search(query, max_results)
                elif hasattr(tool_module, "execute"):
                    return tool_module.execute(query, max_results)
                return "Search not available. Try installing duckduckgo-search via pip."

            elif tool_name == "code_execution":
                code = params.get("code", "")
                language = params.get("language", "python")

                if hasattr(tool_module, "execute"):
                    return tool_module.execute(code, language)
                elif hasattr(tool_module, "run"):
                    return tool_module.run(code, language=language)
                return "Code execution not available."

            elif tool_name == "text_editor":
                action = params.get("action", "read")
                path = params.get("path", "")
                content = params.get("content", "")

                if action == "read" and hasattr(tool_module, "read"):
                    result = tool_module.read(path)
                    if isinstance(result, dict):
                        return result.get("content", str(result))
                    return str(result)
                elif action == "write" and hasattr(tool_module, "write"):
                    result = tool_module.write(path, content)
                    if isinstance(result, dict):
                        if result.get("success"):
                            return f"File written successfully: {path}"
                        return f"Error: {result.get('error', 'Unknown error')}"
                    return str(result)
                elif action == "patch" and hasattr(tool_module, "patch"):
                    result = tool_module.patch(path, content)
                    return str(result)
                return f"Text editor action '{action}' not available."

            elif tool_name == "document_query":
                path = params.get("path", "")

                if hasattr(tool_module, "read_document"):
                    return tool_module.read_document(path)
                elif hasattr(tool_module, "query"):
                    return tool_module.query(path)
                return "Document query not available."

            return f"Tool {tool_name} not implemented"

        except Exception as e:
            error_msg = f"Error executing {tool_name}: {str(e)}"
            if self.retry_on_error:
                error_msg += " (retry_on_error is enabled)"
            return error_msg

    def process_message(
        self, user_message: str, conversation_id: Optional[str] = None
    ) -> str:
        """Process a user message through the agent loop"""
        # Add user message to memory
        self.memory.add_entry(
            {
                "role": "user",
                "content": user_message,
                "conversation_id": conversation_id,
            }
        )

        # Build conversation history with system prompt
        messages = [{"role": "system", "content": self._system_prompt}]

        # Add recent memory entries (last 10)
        recent_entries = self.memory.get_all()[-10:]
        for entry in recent_entries:
            if "role" in entry and "content" in entry:
                messages.append({"role": entry["role"], "content": entry["content"]})

        # Add current message if not already in history
        if not recent_entries or recent_entries[-1].get("content") != user_message:
            messages.append({"role": "user", "content": user_message})

        # Prepare tools for LLM
        tools = []
        for tool_name in self.enabled_tools:
            if tool_name != "response":  # response is handled specially
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

                message = response["choices"][0]["message"]

                # Check for tool calls
                if "tool_calls" in message and message["tool_calls"]:
                    tool_call = message["tool_calls"][0]
                    function = tool_call["function"]
                    tool_name = function["name"]

                    try:
                        params = json.loads(function["arguments"])
                    except json.JSONDecodeError:
                        params = {}

                    # Execute tool
                    result = self._execute_tool(tool_name, params)

                    # Add tool call and result to messages
                    messages.append(
                        {
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [tool_call],
                        }
                    )
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": str(result),
                        }
                    )

                else:
                    # No tool call, direct response
                    final_response = message.get("content", "No response")
                    break

            except Exception as e:
                final_response = f"Error: {str(e)}"
                break

        if final_response is None:
            final_response = "I couldn't complete the task within the iteration limit."

        # Add assistant response to memory
        self.memory.add_entry(
            {
                "role": "assistant",
                "content": final_response,
                "conversation_id": conversation_id,
            }
        )

        return final_response

    def get_system_prompt(self) -> str:
        """Get the current system prompt (for debugging/display)"""
        return self._system_prompt

    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent configuration info"""
        return {
            "name": self.agent.get("name", "Unknown"),
            "description": self.agent.get("description", ""),
            "enabled_tools": self.enabled_tools,
            "max_iterations": self.max_iterations,
            "retry_on_error": self.retry_on_error,
            "preferences": self.preferences,
        }


