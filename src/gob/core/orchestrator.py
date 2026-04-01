"""
Agent Orchestrator - The core agent loop
Handles: prompt → LLM → tool execution → repeat
"""

import json
import asyncio
import time
import logging
from typing import Any, Dict, List, Optional

from gob.core.llm_client import MultiLLM
from gob.core.memory.memory import MemoryManager
from gob.core.tool_loader import load_tool

logger = logging.getLogger(__name__)


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
        agent_name = self.agent.get("name", "gob")
        agent_desc = self.agent.get("description", "AI assistant")
        tools_desc = self._get_tools_description()

        verbose = self.preferences.get("verbose_outputs", False)

        parts = []

        if context:
            parts.append(context.strip())
        else:
            parts.append(f"You are {agent_name}, {agent_desc}.")

        if tools_desc:
            parts.append(f"\nYou have access to the following tools:")
            parts.append(tools_desc)

        parts.append("""
Environment Info:
- You are running in a Linux container
- You have access to standard Linux commands, pip, etc.
- You can install packages at runtime when needed
- You can read/write files, execute code, search the web, and query documents
""")

        if not verbose:
            parts.append("Be concise and direct in your responses.")

        parts.append("""
Tool Usage:
When you need to use a tool, respond with a JSON object:
{"tool": "tool_name", "params": {"param1": "value1"}}

If you don't need a tool, respond normally in plain text.
""")

        return "\n".join(parts).strip()

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

    def get_agent_info(self) -> dict:
        """Get agent configuration information"""
        return {
            "name": self.agent.get("name", "gob"),
            "description": self.agent.get("description", "AI assistant"),
            "enabled_tools": self.enabled_tools,
            "max_iterations": self.max_iterations,
        }

    def get_system_prompt(self) -> str:
        """Get the current system prompt"""
        return self._system_prompt

    async def process_message(self, message: str, conversation_id: str = "default") -> str:
        """Run agent loop: get response, execute tools, loop until final answer"""
        start_time = time.time()
        logger.info(f"Processing message for conversation: {conversation_id}")

        # Retrieve relevant memories if vector search is available
        recall_injection = ""
        if hasattr(self.memory, 'get_vector_based_memories'):
            try:
                recalled = self.memory.get_vector_based_memories(message, limit=5)
                if recalled:
                    memory_str = "\n\n# Relevant Memories\n"
                    memory_str += "These may or may not be relevant to the current query:\n"
                    memory_str += "\n".join([
                        f"- {r.get('text', '')[:300]}"
                        for r in recalled
                    ])
                    recall_injection = memory_str
                    logger.info(f"Injected {len(recalled)} recalled memories")
            except Exception as e:
                logger.debug(f"Memory recall skipped: {e}")

        # Initialize system prompt on first message, keep history after that
        system_prompt = self._system_prompt
        if recall_injection:
            system_prompt += recall_injection

        if not self.messages:
            self.messages = [{"role": "system", "content": system_prompt}]
        else:
            # Update system prompt (may have new memory recall)
            self.messages[0] = {"role": "system", "content": system_prompt}

        self.messages.append({"role": "user", "content": message})

        for iteration in range(self.max_iterations):
            logger.debug(f"Iteration {iteration + 1}/{self.max_iterations}")

            try:
                # Get response from LLM
                response = await self.llm.chat_complete(self.messages)

                # Try to parse as JSON (tool call)
                try:
                    tool_request = json.loads(response)
                except json.JSONDecodeError:
                    # Not JSON — this is the agent's final text answer
                    self.messages.append({"role": "assistant", "content": response})
                    total_time = time.time() - start_time
                    logger.info(f"Got text response in {total_time:.1f}s")
                    return response

                # Execute tool
                tool_name = tool_request.get("tool") or tool_request.get("tool_name")
                tool_args = tool_request.get("params") or tool_request.get("tool_args", {})

                if not tool_name:
                    return response  # Malformed JSON, treat as text

                logger.info(f"Executing tool: {tool_name}")

                try:
                    tool = load_tool(tool_name)
                    result = tool.execute(**tool_args)

                    if isinstance(result, dict):
                        result_str = json.dumps(result)
                    else:
                        result_str = str(result)
                except Exception as e:
                    result_str = f"Tool execution error: {str(e)}"
                    logger.error(f"Tool {tool_name} failed: {e}")

                # Add tool result to history
                self.messages.append({
                    "role": "assistant",
                    "content": response
                })
                self.messages.append({
                    "role": "user",
                    "content": f"Tool '{tool_name}' returned:\n{result_str}"
                })

                # Check if it's the response tool (final answer)
                if tool_name == "response":
                    final_text = result.get("text", result_str) if isinstance(result, dict) else result_str
                    total_time = time.time() - start_time
                    logger.info(f"Final response in {total_time:.1f}s after {iteration + 1} iterations")
                    return final_text

            except Exception as e:
                logger.error(f"Error in iteration {iteration}: {e}")
                return f"Error: {str(e)}"

        total_time = time.time() - start_time
        logger.warning(f"Max iterations ({self.max_iterations}) reached in {total_time:.1f}s")
        return "I reached my maximum thinking steps. Could you rephrase or simplify your request?"
