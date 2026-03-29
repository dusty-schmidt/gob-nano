"""Tests for NANO - no LLM connectivity required."""
import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestConfigLoading:
    """Test suite for configuration management."""

    def test_resolve_env_vars_basic(self):
        """Test that ${VAR_NAME} syntax is properly resolved from env."""
        from src.nano.helpers.config_loader import resolve_env_vars
        
        os.environ['TEST_VAR'] = 'resolved_value'
        result = resolve_env_vars('prefix_${TEST_VAR}_suffix')
        assert result == 'prefix_resolved_value_suffix'
        del os.environ['TEST_VAR']
        
        # Test missing var becomes empty string
        result = resolve_env_vars('${MISSING_VAR}')
        assert result == ''

    def test_resolve_env_vars_non_string(self):
        """Test that non-string values are returned unchanged."""
        from src.nano.helpers.config_loader import resolve_env_vars
        
        assert resolve_env_vars(123) == 123
        assert resolve_env_vars(None) is None
        assert resolve_env_vars(['list', 'items']) == ['list', 'items']

    def test_resolve_config_env_vars_recursive(self):
        """Test recursive resolution in nested dicts."""
        from src.nano.helpers.config_loader import resolve_config_env_vars
        
        os.environ['API_KEY'] = 'secret123'
        config = {
            'llm': {
                'api_key': '${API_KEY}',
                'model': 'qwen/qwen3.5-flash-02-23'
            },
            'discord': {
                'token': '${DISCORD_TOKEN}'
            }
        }
        result = resolve_config_env_vars(config)
        
        assert result['llm']['api_key'] == 'secret123'
        assert result['llm']['model'] == 'qwen/qwen3.5-flash-02-23'
        assert result['discord']['token'] == ''  # Not set
        del os.environ['API_KEY']

    def test_load_config_returns_dict(self):
        """Test that load_config returns a valid dict."""
        from src.nano.helpers.config_loader import load_config
        
        config = load_config()
        assert isinstance(config, dict)
        assert 'llm' in config
        assert 'discord' in config
        assert 'agent' in config

    def test_config_loaded_from_project_root(self):
        """Test that config is loaded from correct path."""
        from src.nano.helpers.config_loader import load_config
        
        config = load_config()
        # Verify we loaded our project's config
        assert config['agent']['name'] == 'nano_agent'


class TestMemoryOperations:
    """Test suite for memory system - file-based JSONL."""

    def test_memory_file_creation(self, tmp_path):
        """Test that MemoryManager creates parent directory on init."""
        from src.nano.helpers.memory.memory import MemoryManager
        
        memory_file = tmp_path / 'subdir' / 'memory.jsonl'
        assert not memory_file.exists()
        assert not memory_file.parent.exists()
        
        manager = MemoryManager(memory_file)
        # Should create parent directory (file created on first add)
        assert memory_file.parent.exists()

    def test_memory_add_entry(self, tmp_path):
        """Test adding a memory entry."""
        from src.nano.helpers.memory.memory import MemoryManager
        
        memory_file = tmp_path / 'memory.jsonl'
        manager = MemoryManager(memory_file)
        
        entry = {'role': 'user', 'content': 'Hello world'}
        manager.add_entry(entry)
        
        entries = manager.get_all()
        assert len(entries) == 1
        assert entries[0]['content'] == 'Hello world'

    def test_memory_query_by_key(self, tmp_path):
        """Test querying memory entries by key."""
        from src.nano.helpers.memory.memory import MemoryManager
        
        memory_file = tmp_path / 'memory.jsonl'
        manager = MemoryManager(memory_file)
        
        manager.add_entry({'role': 'user', 'content': 'Hello'})
        manager.add_entry({'role': 'assistant', 'content': 'Hi there'})
        manager.add_entry({'role': 'user', 'content': 'Bye'})
        
        user_entries = manager.query('role', 'user')
        assert len(user_entries) == 2
        
        assistant_entries = manager.query('role', 'assistant')
        assert len(assistant_entries) == 1

    def test_memory_empty_file(self, tmp_path):
        """Test that empty memory file returns empty list."""
        from src.nano.helpers.memory.memory import MemoryManager
        
        memory_file = tmp_path / 'empty.jsonl'
        memory_file.touch()
        
        manager = MemoryManager(memory_file)
        entries = manager.get_all()
        assert entries == []


class TestToolLoader:
    """Test suite for tool loading."""

    def test_load_tool_returns_module(self):
        """Test that load_tool returns a module."""
        from src.nano.helpers.tool_loader import load_tool
        
        # This should work for actual tools
        tool = load_tool('response')
        assert tool is not None
        assert hasattr(tool, 'execute') or hasattr(tool, 'run')

    def test_load_tool_nonexistent_raises(self):
        """Test that loading a non-existent tool raises ImportError."""
        from src.nano.helpers.tool_loader import load_tool
        
        with pytest.raises(ImportError):
            load_tool('nonexistent_tool_xyz')


class TestAgentLoader:
    """Test suite for agent profile loading."""

    def test_load_default_agent(self):
        """Test loading the default agent profile."""
        from src.nano.helpers.agent_loader import load_agent
        
        agent = load_agent('default')
        assert isinstance(agent, dict)
        assert 'name' in agent
        assert 'context' in agent
        assert agent['name'] == 'Default Agent'

    def test_load_nonexistent_agent_raises(self):
        """Test that loading non-existent profile raises FileNotFoundError."""
        from src.nano.helpers.agent_loader import load_agent
        
        with pytest.raises(FileNotFoundError):
            load_agent('nonexistent_profile')


class TestToolsExist:
    """Verify that core tools are properly implemented."""

    def test_response_tool_exists(self):
        """Test that response tool module exists."""
        from src.nano.tools import response
        assert hasattr(response, 'execute') or hasattr(response, 'run')

    def test_search_engine_tool_exists(self):
        """Test that search_engine tool module exists."""
        from src.nano.tools import search_engine
        assert hasattr(search_engine, 'execute') or hasattr(search_engine, 'run')

    def test_code_execution_tool_exists(self):
        """Test that code_execution tool module exists."""
        from src.nano.tools import code_execution
        assert hasattr(code_execution, 'execute') or hasattr(code_execution, 'run')

    def test_text_editor_tool_exists(self):
        """Test that text_editor tool module exists."""
        from src.nano.tools import text_editor
        # Module has read/write/patch functions
        assert hasattr(text_editor, 'read')
        assert hasattr(text_editor, 'write')
        assert hasattr(text_editor, 'patch')
    def test_document_query_tool_exists(self):
        """Test that document_query tool module exists."""
        from src.nano.tools import document_query
        assert hasattr(document_query, 'execute') or hasattr(document_query, 'run')
