"""
Comprehensive unit tests for context service.
"""
import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open
from app.services.context_service import ContextService, SessionContext


@pytest.mark.unit
class TestContextService:
    """Test cases for context service functions."""

    def test_session_context_creation(self):
        """Test SessionContext creation and initialization."""
        context = SessionContext()
        
        assert context.current_repository is None
        assert context.current_jira_project is None
        assert context.recent_actions == []
        assert context.conversation_history == []
        assert context.jira_projects == []
        assert context.jira_issues == []
        assert context.jira_sprints == []
        assert context.github_repos == []
        assert context.github_branches == []
        assert context.github_issues == []
        assert context.github_prs == []

    def test_session_context_data_assignment(self):
        """Test assigning data to SessionContext."""
        context = SessionContext()
        
        context.current_repository = {"owner": "testuser", "repo": "testrepo"}
        context.current_jira_project = {"key": "TEST", "name": "Test Project"}
        context.recent_actions = [{"action": "created_issue", "details": "TEST-1"}]
        context.conversation_history = [{"role": "user", "content": "Hello"}]
        
        assert context.current_repository["owner"] == "testuser"
        assert context.current_jira_project["key"] == "TEST"
        assert len(context.recent_actions) == 1
        assert len(context.conversation_history) == 1

    def test_session_context_to_dict(self):
        """Test SessionContext to_dict method."""
        context = SessionContext()
        context.current_repository = {"owner": "testuser", "repo": "testrepo"}
        context.recent_actions = [{"action": "created_issue", "details": "TEST-1"}]
        
        context_dict = context.to_dict()
        
        assert isinstance(context_dict, dict)
        assert context_dict["current_repository"]["owner"] == "testuser"
        assert len(context_dict["recent_actions"]) == 1

    def test_session_context_from_dict(self):
        """Test SessionContext from_dict method."""
        context_data = {
            "current_repository": {"owner": "testuser", "repo": "testrepo"},
            "current_jira_project": {"key": "TEST", "name": "Test Project"},
            "recent_actions": [{"action": "created_issue", "details": "TEST-1"}],
            "conversation_history": [{"role": "user", "content": "Hello"}],
            "jira_projects": [],
            "jira_issues": [],
            "jira_sprints": [],
            "github_repos": [],
            "github_branches": [],
            "github_issues": [],
            "github_prs": []
        }
        
        context = SessionContext.from_dict(context_data)
        
        assert context.current_repository["owner"] == "testuser"
        assert context.current_jira_project["key"] == "TEST"
        assert len(context.recent_actions) == 1
        assert len(context.conversation_history) == 1

    def test_context_service_initialization(self, temp_dir):
        """Test ContextService initialization."""
        service = ContextService(temp_dir)
        
        assert service.storage_dir == Path(temp_dir)
        assert service.context_file == Path(temp_dir) / "context.json"

    def test_context_service_get_or_create_context_new(self, temp_dir):
        """Test getting or creating context when none exists."""
        service = ContextService(temp_dir)
        context = service.get_or_create_context()
        
        assert isinstance(context, SessionContext)
        assert context.current_repository is None
        assert context.recent_actions == []

    def test_context_service_get_or_create_context_existing(self, temp_dir):
        """Test getting existing context."""
        service = ContextService(temp_dir)
        
        # Create initial context
        initial_context = SessionContext()
        initial_context.current_repository = {"owner": "testuser", "repo": "testrepo"}
        service.save_context(initial_context)
        
        # Get context
        retrieved_context = service.get_or_create_context()
        
        assert retrieved_context.current_repository["owner"] == "testuser"

    def test_context_service_save_context(self, temp_dir):
        """Test saving context to file."""
        service = ContextService(temp_dir)
        context = SessionContext()
        context.current_repository = {"owner": "testuser", "repo": "testrepo"}
        
        service.save_context(context)
        
        # Verify file was created
        assert service.context_file.exists()
        
        # Verify content
        with open(service.context_file, 'r') as f:
            saved_data = json.load(f)
        
        assert saved_data["current_repository"]["owner"] == "testuser"

    def test_context_service_clear_context(self, temp_dir):
        """Test clearing context."""
        service = ContextService(temp_dir)
        context = SessionContext()
        context.current_repository = {"owner": "testuser", "repo": "testrepo"}
        service.save_context(context)
        
        # Clear context
        service.clear_context()
        
        # Verify file still exists but is empty
        assert service.context_file.exists()
        
        with open(service.context_file, 'r') as f:
            content = f.read().strip()
        
        assert content == "{}"

    def test_context_service_get_context_for_prompt(self, temp_dir):
        """Test getting context for prompt."""
        service = ContextService(temp_dir)
        context = SessionContext()
        context.current_repository = {"owner": "testuser", "repo": "testrepo"}
        context.current_jira_project = {"key": "TEST", "name": "Test Project"}
        context.recent_actions = [{"action": "created_issue", "details": "TEST-1"}]
        context.conversation_history = [{"role": "user", "content": "Hello"}]
        service.save_context(context)
        
        context_for_prompt = service.get_context_for_prompt()
        
        assert isinstance(context_for_prompt, dict)
        assert context_for_prompt["current_repository"]["owner"] == "testuser"
        assert context_for_prompt["current_jira_project"]["key"] == "TEST"
        assert len(context_for_prompt["recent_actions"]) == 1
        assert len(context_for_prompt["conversation_history"]) == 1

    def test_context_service_get_context_summary(self, temp_dir):
        """Test getting context summary."""
        service = ContextService(temp_dir)
        context = SessionContext()
        context.current_repository = {"owner": "testuser", "repo": "testrepo"}
        context.current_jira_project = {"key": "TEST", "name": "Test Project"}
        context.recent_actions = [{"action": "created_issue", "details": "TEST-1"}]
        service.save_context(context)
        
        summary = service.get_context_summary()
        
        assert isinstance(summary, str)
        assert "testuser/testrepo" in summary
        assert "TEST" in summary
        assert "created_issue" in summary

    def test_context_service_make_serializable(self, temp_dir):
        """Test _make_serializable method."""
        service = ContextService(temp_dir)
        
        # Test with various data types
        test_data = {
            "string": "test",
            "int": 123,
            "float": 123.45,
            "bool": True,
            "list": [1, 2, 3],
            "dict": {"key": "value"},
            "none": None
        }
        
        serializable_data = service._make_serializable(test_data)
        
        assert serializable_data == test_data

    def test_context_service_make_serializable_with_objects(self, temp_dir):
        """Test _make_serializable with non-serializable objects."""
        service = ContextService(temp_dir)
        
        class NonSerializable:
            def __init__(self):
                self.value = "test"
        
        test_data = {
            "serializable": "test",
            "non_serializable": NonSerializable()
        }
        
        serializable_data = service._make_serializable(test_data)
        
        assert serializable_data["serializable"] == "test"
        assert "non_serializable" in serializable_data

    def test_context_service_error_handling(self, temp_dir):
        """Test error handling in context service."""
        service = ContextService(temp_dir)
        
        # Test with invalid JSON file
        with open(service.context_file, 'w') as f:
            f.write("invalid json")
        
        # Should create new context when file is corrupted
        context = service.get_or_create_context()
        assert isinstance(context, SessionContext)

    def test_context_service_file_operations(self, temp_dir):
        """Test file operations in context service."""
        service = ContextService(temp_dir)
        
        # Test initial state
        assert not service.context_file.exists()
        
        # Create and save context
        context = SessionContext()
        context.current_repository = {"owner": "testuser", "repo": "testrepo"}
        service.save_context(context)
        
        assert service.context_file.exists()
        
        # Load context
        loaded_context = service.get_or_create_context()
        assert loaded_context.current_repository["owner"] == "testuser"
        
        # Clear context
        service.clear_context()
        assert service.context_file.exists()
        
        # Load cleared context
        cleared_context = service.get_or_create_context()
        assert cleared_context.current_repository is None

    def test_context_service_with_large_data(self, temp_dir):
        """Test context service with large amounts of data."""
        service = ContextService(temp_dir)
        context = SessionContext()
        
        # Add large amounts of data
        context.recent_actions = [{"action": f"action_{i}", "details": f"details_{i}"} for i in range(1000)]
        context.conversation_history = [{"role": "user", "content": f"message_{i}"} for i in range(1000)]
        
        service.save_context(context)
        
        # Load and verify
        loaded_context = service.get_or_create_context()
        assert len(loaded_context.recent_actions) == 1000
        assert len(loaded_context.conversation_history) == 1000

    def test_context_service_concurrent_access(self, temp_dir):
        """Test context service with concurrent access simulation."""
        service = ContextService(temp_dir)
        
        # Simulate multiple contexts
        contexts = []
        for i in range(10):
            context = SessionContext()
            context.current_repository = {"owner": f"user{i}", "repo": f"repo{i}"}
            contexts.append(context)
        
        # Save all contexts
        for context in contexts:
            service.save_context(context)
        
        # Load final context
        final_context = service.get_or_create_context()
        assert final_context.current_repository["owner"] == "user9"
