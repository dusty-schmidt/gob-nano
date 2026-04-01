"""
Agent Orchestrator — with G.O.B. autopsy integration and hot-reload.
Handles: prompt → LLM → tool execution → repeat
"""

import json
import time
import importlib
import logging
from typing import Any, Dict, List, Optional

from gob.core.llm_client import MultiLLM
from gob.core.memory.memory import MemoryManager
from gob.core.tool_loader import load_tool

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Orchestrates agent reasoning, tool execution, failure recovery, and hot-reload."""

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
        self.tools_config = tools_config
        self.messages: List[Dict[str, str]] = []

        # Extract enabled tools
        agent_tools = agent_config.get("tools", [])
        config_tools = tools_config.get("enabled", [])
        self.enabled_tools = agent_tools if agent_tools else config_tools

        # Settings
        agent_settings = agent_config.get("settings", {})
        self.max_iterations = agent_settings.get("max_iterations", 5)
        self.retry_on_error = agent_settings.get("retry_on_error", True)
        self.auto_suggest_tools = agent_settings.get("auto_suggest_tools", False)
        self.preferences = agent_config.get("preferences", {})

        # System prompt
        self._system_prompt = self._build_system_prompt()

    # ── Hot-reload (Epic 4, Story 31) ────────────────────────────────────

    def reload_components(self) -> None:
        """Re-import core tools and refresh agent config without restarting the agent.

        This method allows the orchestrator to pick up code changes made in tool
        modules or configuration files after a successful merge to main.
        """
        logger.info("[RELOAD] Reloading tool modules and configuration...")

        # Reload each enabled tool module
        for tool_name in self.enabled_tools:
            try:
                importlib.import_module(f"gob.tools.{tool_name}")
                importlib.reload(importlib.import_module(f"gob.tools.{tool_name}"))
                logger.info(f"[RELOAD] Tool reloaded: {tool_name}")
            except Exception as e:
                logger.warning(f"[RELOAD] Failed to reload {tool_name}: {e}")

        # Refresh tools list from config (in case config changed)
        new_agent_tools = self.agent.get("tools", [])
        new_config_tools = self.tools_config.get("enabled", [])
        new_enabled = new_agent_tools if new_agent_tools else new_config_tools
        if new_enabled != self.enabled_tools:
            logger.info(f"[RELOAD] Enabled tools updated: {self.enabled_tools} → {new_enabled}")
            self.enabled_tools = new_enabled

        self._system_prompt = self._build_system_prompt()
        logger.info("[RELOAD] ✅ Components reloaded.")

    def on_merge_detected(self) -> None:
        """Hook called automatically after a successful merge to main.

        Triggers reload and informs the agent that its codebase has been updated.
        """
        self.reload_components()


    # ── System prompt builder ────────────────────────────────────────────

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

        parts.append("""\nEnvironment Info:
- You are running in a Linux container
- You have access to standard Linux commands, pip, etc.
- You can install packages at runtime when needed
- You can read/write files, execute code, search the web, and query documents
""")

        if not verbose:
            parts.append("Be concise and direct in your responses.")

        parts.append("""\nTool Usage:
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

    # ── Agent info & system prompt access ────────────────────────────────

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

    def load_session_history(self, conversation_id: str, max_messages: int = 20):
        """Load previous conversation history from SQLite for cross-session memory"""
        try:
            history = self.memory.get_conversations(conversation_id, limit=max_messages)
            if history:
                self.messages = [{"role": "system", "content": self._system_prompt}]
                for msg in history:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    if role in ("user", "assistant") and content:
                        self.messages.append({"role": role, "content": content})
                logger.info(f"Loaded {len(history)} messages from session '{conversation_id}'")
            else:
                logger.info(f"No previous history for session '{conversation_id}'")
        except Exception as e:
            logger.warning(f"Could not load session history: {e}")

    async def process_message(self, message: str, conversation_id: str = "default") -> str:
        """Run agent loop: get response, execute tools, loop until final answer"""
        start_time = time.time()
        logger.info(f"Processing message for conversation: {conversation_id}")

        # Memory recall
        recall_injection = ""
        if hasattr(self.memory, 'get_vector_based_memories'):
            try:
                recalled = self.memory.get_vector_based_memories(message, limit=5)
                if recalled:
                    recall_injection = "\n\n# Relevant Memories\n" + "\n".join([f"- {r.get('text', '')[:300]}" for r in recalled])
                    logger.info(f"Injected {len(recalled)} recalled memories")
            except Exception as e:
                logger.debug(f"Memory recall skipped: {e}")

        # Init history
        system_prompt = self._system_prompt + recall_injection if recall_injection else self._system_prompt
        if not self.messages:
            self.messages = [{"role": "system", "content": system_prompt}]
        else:
            self.messages[0] = {"role": "system", "content": system_prompt}
        self.messages.append({"role": "user", "content": message})

        for iteration in range(self.max_iterations):
            logger.debug(f"Iteration {iteration + 1}/{self.max_iterations}")
            try:
                response = await self.llm.chat_complete(self.messages)

                # Parse tool call
                try:
                    tool_request = json.loads(response)
                except json.JSONDecodeError:
                    self.messages.append({"role": "assistant", "content": response})
                    return response

                tool_name = tool_request.get("tool") or tool_request.get("tool_name")
                tool_args = tool_request.get("params") or tool_request.get("tool_args", {})
                if not tool_name:
                    return response

                logger.info(f"Executing tool: {tool_name}")

                try:
                    tool = load_tool(tool_name)
                    result = tool.execute(**tool_args)

                    # ----------------------------------------------------------------
                    # Autopsy integration (Epic 3, Story 26)
                    # ----------------------------------------------------------------
                    if isinstance(result, dict) and not result.get("success", True):
                        exit_code = result.get("exit_code", 1)
                        stdout = result.get("stdout", "")
                        stderr = result.get("stderr", "")

                        # Generate and store autopsy
                        from gob.core.autopsy import summarize_failure
                        autopsy = summarize_failure(exit_code, stdout, stderr)
                        self.memory.add_failure_log(
                            exit_code=exit_code,
                            stdout=stdout,
                            stderr=stderr,
                            autopsy_report=autopsy,
                            tool_name=tool_name,
                            session_id=conversation_id,
                        )
                        logger.warning(f"[AUTOPSY] {tool_name} failed — injection prepared")

                        result_str = json.dumps(result, indent=2) + "\n\n" + autopsy
                    elif isinstance(result, dict):
                        result_str = json.dumps(result, indent=2)
                    else:
                        result_str = str(result)

                except Exception as e:
                    result_str = f"Tool execution error: {str(e)}"
                    logger.error(f"Tool {tool_name} failed: {e}")

                self.messages.append({"role": "assistant", "content": response})
                self.messages.append({"role": "user", "content": f"Tool '{tool_name}' returned:\n{result_str}"})

                if tool_name == "response":
                    final_text = result.get("text", result_str) if isinstance(result, dict) else result_str
                    return final_text

            except Exception as e:
                logger.error(f"Error in iteration {iteration}: {e}")
                return f"Error: {str(e)}"

        return "I reached my maximum thinking steps. Could you rephrase or simplify your request?"
