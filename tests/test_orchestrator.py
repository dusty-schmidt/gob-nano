import unittest
from unittest.mock import MagicMock

from gob.core.orchestrator import AgentOrchestrator
from gob.core.config_loader import load_config
from gob.core.agent_loader import load_agent
from gob.core.memory.memory import MemoryManager


class TestOrchestrator(unittest.TestCase):
    def setUp(self):
        self.config = load_config()

        # Mock LLM client to avoid API calls
        self.mock_llm = MagicMock()
        self.mock_llm.chat_model = "test-model"

        # In-memory SQLite for tests
        self.memory = MemoryManager(db_path="/tmp/test_gob_memory.db")

        # Load agent config
        self.agent_config = load_agent(
            self.config.get("agent", {}).get("profile", "default")
        )
        self.tools_config = self.config.get("tools", {})

        # Initialize orchestrator
        self.orchestrator = AgentOrchestrator(
            llm_client=self.mock_llm,
            memory=self.memory,
            agent_config=self.agent_config,
            tools_config=self.tools_config,
        )

    def test_initialization(self):
        self.assertIsNotNone(self.orchestrator)
        self.assertEqual(self.orchestrator.agent["name"], "gob")
        self.assertIsNotNone(self.orchestrator.llm)
        self.assertIsNotNone(self.orchestrator.memory)

    def test_get_system_prompt(self):
        prompt = self.orchestrator.get_system_prompt()
        self.assertIsInstance(prompt, str)
        self.assertIn("gob", prompt.lower())

    def test_memory_initialization(self):
        self.assertIsNotNone(self.orchestrator.memory)

    def test_max_iterations(self):
        # From default.yaml settings.max_iterations
        self.assertEqual(self.orchestrator.max_iterations, 20)

    def test_enabled_tools(self):
        self.assertIn("code_execution", self.orchestrator.enabled_tools)
        self.assertIn("response", self.orchestrator.enabled_tools)

    def test_load_session_history_empty(self):
        """Loading history for a non-existent session should not crash"""
        self.orchestrator.load_session_history("nonexistent_session")
        self.assertEqual(len(self.orchestrator.messages), 0)

    def test_get_agent_info(self):
        info = self.orchestrator.get_agent_info()
        self.assertEqual(info["name"], "gob")
        self.assertIsInstance(info["enabled_tools"], list)


if __name__ == "__main__":
    unittest.main()
