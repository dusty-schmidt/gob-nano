import unittest
import sys
import os
from pathlib import Path
from unittest.mock import MagicMock

# Add the project root to the path so 'src' is visible
sys.path.insert(0, '/a0/usr/projects/gob')

from src.gob.orchestrator import AgentOrchestrator
from src.gob.helpers.config_loader import load_config
from src.gob.helpers.memory.memory import MemoryManager

class TestOrchestrator(unittest.TestCase):
    def setUp(self):
        # Load default config
        self.config = load_config()
        
        # Create mock LLM client to avoid API calls
        self.mock_llm = MagicMock()
        
        # Create memory manager with Path object
        self.memory = MemoryManager(Path('/tmp/test_memory.jsonl'))
        
        # Get agent and tools config from main config
        self.agent_config = self.config.get('agent', {})
        self.tools_config = self.config.get('tools', {})
        
        # Initialize orchestrator with all required arguments
        self.orchestrator = AgentOrchestrator(
            llm_client=self.mock_llm,
            memory=self.memory,
            agent_config=self.agent_config,
            tools_config=self.tools_config
        )

    def test_initialization(self):
        self.assertIsNotNone(self.orchestrator)
        self.assertEqual(self.orchestrator.agent['name'], 'gob')
        self.assertIsNotNone(self.orchestrator.llm)
        self.assertIsNotNone(self.orchestrator.memory)

    def test_get_system_prompt(self):
        prompt = self.orchestrator.get_system_prompt()
        self.assertIsInstance(prompt, str)
        # The prompt should contain the agent name from default.yaml (lowercase)
        self.assertIn('gob', prompt)

    def test_memory_initialization(self):
        self.assertIsNotNone(self.orchestrator.memory)

    def test_max_iterations_default(self):
        # Default max_iterations should be 5 from agent settings
        self.assertEqual(self.orchestrator.max_iterations, 5)

if __name__ == '__main__':
    unittest.main()
