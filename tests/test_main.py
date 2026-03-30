"""Tests for main.py entry point"""
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path


class TestMainEntry:
    """Test suite for main.py entry point."""

    def test_main_imports(self):
        """Test that main.py can be imported without errors."""
        from src.gob import main
        assert hasattr(main, 'main')

    @patch('src.gob.main.load_config')
    @patch('src.gob.main.load_agent')
    @patch('src.gob.main.MemoryManager')
    def test_main_loads_config_agent_memory(self, mock_memory, mock_agent, mock_config):
        """Test that main() loads config, agent, and memory."""
        mock_config.return_value = {
            'agent': {'profile': 'default'},
            'llm': {'provider': 'openrouter', 'model': 'qwen/qwen3.5-flash-02-23', 'api_key': 'test-key'},
            'tools': {'enabled': ['response']}
        }
        mock_agent.return_value = {'name': 'Test Agent'}
        
        from src.gob.main import main
        
        # Capture output to avoid print statements during test
        with patch('builtins.print'):
            main()
        
        mock_config.assert_called_once()
        mock_agent.assert_called_once_with('default')
        mock_memory.assert_called_once()

    @patch('src.gob.main.load_config')
    def test_main_exits_on_missing_api_key(self, mock_config):
        """Test that main() exits if API key is not configured."""
        mock_config.return_value = {
            'agent': {'profile': 'default'},
            'llm': {'provider': 'openrouter', 'model': 'qwen/qwen3.5-flash-02-23', 'api_key': 'your_key_here'},
            'tools': {'enabled': []}
        }
        
        from src.gob.main import main
        
        with patch('builtins.print'):
            with pytest.raises(SystemExit):
                main()

    def test_main_can_run(self):
        """Integration test: main() can run with real config."""
        from src.gob.main import main
        
        # This should complete without error
        with patch('builtins.print'):
            main()
