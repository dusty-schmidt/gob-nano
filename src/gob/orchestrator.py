import json
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.gob.core.llm_client import MultiLLM
from src.gob.core.memory.memory import MemoryManager
from src.gob.core.tool_loader import load_tool


class AgentOrchestrator:
    """Orchestrates agent reasoning and tool execution"""

    def __init__(
        self,
        llm_client: MultiLLM,
        memory: MemoryManager,
        agent_config: Dict[str, Any],
        tools_config: Dict[str, Any],
    ):
        self.llm = llm_client
        self.memory = memory
        self.agent = agent_config
        self.messages: List[Dict[str, str]] = []

        # Extract enabled tools from agent config or tools config
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
        context = self.agent.get("context", "")
        agent_name = self.agent.get("name", "GOB-NANO")
        agent_desc = self.agent.get("description", "AI assistant")
        tools_desc = self._get_tools_description()

        verbose = self.preferences.get("verbose_outputs", False)
        include_timestamps = self.preferences.get("include_timestamps", True)

        system_prompt_parts = []

        if context:
            system_prompt_parts.append(context.strip())
        else:
            system_prompt_parts.append(f"You are {agent_name}, {agent_desc}.")

        if tools_desc:
            system_prompt_parts.append(f"\nYou have access to the following tools:")
            system_prompt_parts.append(tools_desc)

        system_prompt_parts.append("""
Environment Info:
- You are running in a full Arch Linux container
- You have access to: pacman (package manager), pip (Python packages), all standard Linux commands
- You can install packages at runtime when needed via 'pip install <package>' or 'pacman -S <package>'
- You can read/write files, execute code, search the web, and query documents
""")

        behavior_parts = []
        if not verbose:
            behavior_parts.append("Be concise and direct in your responses.")
        if include_timestamps:
            behavior_parts.append("Include timestamps when relevant.")

        if behavior_parts:
            system_prompt_parts.append("\nBehavior Guidelines:")
            system_prompt_parts.append(" ".join(behavior_parts))

        system_prompt_parts.append("""
Tool Usage:
When you need to use a tool, respond with a JSON object:
{"tool": "tool_name", "params": {"param1": "value1"}}

If you don't need a tool, respond normally in plain text.
""")

        return "\n".join(system_prompt_parts).strip()

    def _get_tools_description(self) -> str:
        descriptions = []
        tool_specs = {
            "response": "Send a text response to the user",
            "search_engine": "Search the web for information using DuckDuckGo",
            "code_execution": "Execute Python code or bash commands",
            "text_editor": "Read, write, or modify files",
            "document_query": "Read and parse document contents",
        }
        for tool_name in self.enabled_tools:
            desc = tool_specs.get(tool_name, "No description available")
            descriptions.append(f"  • {tool_name}: {desc}")
        return "\n".join(descriptions) if descriptions else "No tools configured."

    async def process_message(self, message: str, conversation_id: str = "default") -> str:
        """Run agent loop: get response, execute tools, loop until final answer"""
        # Retrieve relevant memories first (async call to utility model)
        recall_injection = ""
        if hasattr(self.memory, 'get_vector_based_memories'):
            # Build context from recent messages for smart recall
            recent_context = "\n".join([
                m.get('content', '') for m in self.messages[-5:] 
            ])
            
            # If no recent messages, use the user's new message
            if not recent_context:
                recent_context = message
            
            # Use utility model to generate a semantic search query (cheaper than chat model)
            if hasattr(self.llm, 'generate_query'):
                try:
                    recall_query = await self.llm.generate_query(recent_context, "memory retrieval")
                except Exception:
                    recall_query = recent_context  # Fallback if generation fails
            else:
                recall_query = recent_context
            
            # Search vector store for relevant memories
            recalled = self.memory.get_vector_based_memories(recall_query, limit=8)
            
            if recalled:
                # Format recalled memories for injection into system prompt
                memory_str = "\n\n# Relevant Memories on the Topic\n"
                memory_str += "Following are facts and context about the current topic.\n"
                memory_str += "- Do not overly rely on them - they might not be relevant.\n\n"
                memory_str += "\n\n".join([
                    f"-{result.get('text', '')[:500]}..."
                    for result in recalled
                ])
                recall_injection = memory_str
        
        # Build system prompt with tools
        base_prompt = self._build_system_prompt()
        
        # Add memory recall to system prompt if available
        if recall_injection:
            system_prompt = base_prompt + recall_injection
        else:
            system_prompt = base_prompt
            
        self.messages = [{"role": "system", "content": system_prompt}]
        
        # Add user message to history

        for iteration in range(self.max_iterations):
            try:
                # Get response from LLM (await async call)
                response = await self.llm.chat_complete(self.messages)

                # Parse JSON response
                try:
                    tool_request = json.loads(response)
                except json.JSONDecodeError:
                    # If not JSON, assume it's a text response (agent final answer)
                    # In a real app, we'd save this to memory, but we need memory integration first
                    return response

                # Execute tool
                tool_name = tool_request.get("tool_name")
                tool_args = tool_request.get("tool_args", {})

                if not tool_name:
                    continue

                # Execute tool (synchronous for now, could be async in future)
                try:
                    tool = load_tool(tool_name)
                    result = tool.execute(**tool_args)
                    if isinstance(result, dict):
                        result_str = json.dumps(result)
                    else:
                        result_str = str(result)
                except Exception as e:
                    result_str = f"Tool execution error: {str(e)}"

                # Add tool result to history
                self.messages.append({
                    "role": "tool",
                    "content": f"Tool: {tool_name}\nResult: {result_str}"
                })

                # Check if it's a final response tool
                if tool_name == "response":
                    final_text = result.get("text", result_str) if isinstance(result, dict) else result_str
                    return final_text

            except Exception as e:
                error_msg = f"Error in iteration {iteration}: {str(e)}"
                return error_msg

        return "Maximum iterations reached"