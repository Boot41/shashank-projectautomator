"""
Pytest configuration and fixtures for the test suite.
"""
import pytest
import asyncio
import tempfile
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    with patch('app.config.settings.settings') as mock:
        mock.github_mock = True
        mock.jira_mock = True
        mock.github_token = "test-token"
        mock.github_api_url = "https://api.github.com"
        mock.github_user_agent = "test-agent"
        mock.jira_base_url = "https://test.atlassian.net"
        mock.jira_email = "test@example.com"
        mock.jira_api_token = "test-token"
        mock.gemini_api_key = "test-api-key"
        mock.gemini_model = "gemini-2.5-flash-lite"
        mock.http_timeout = 30
        mock.smtp_server = "smtp.gmail.com"
        mock.smtp_port = 587
        mock.smtp_username = "test@example.com"
        mock.smtp_password = "test-password"
        mock.api_key = "test-api-key"
        yield mock


@pytest.fixture
def mock_httpx_client():
    """Mock httpx.AsyncClient for testing."""
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = AsyncMock()
        mock_response.json.return_value = {"test": "data"}
        mock_response.raise_for_status.return_value = None
        mock_response.status_code = 200
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value.put.return_value = mock_response
        mock_client.return_value.__aenter__.return_value.patch.return_value = mock_response
        yield mock_client


@pytest.fixture
def mock_genai():
    """Mock Google Generative AI for testing."""
    with patch('app.services.ai_service.genai') as mock_genai:
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Test response"
        mock_response.function_calls = []
        mock_model.generate_content_async.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        mock_genai.configure.return_value = None
        yield mock_genai


@pytest.fixture
def sample_github_repo():
    """Sample GitHub repository data."""
    return {
        "name": "test-repo",
        "full_name": "owner/test-repo",
        "private": False,
        "html_url": "https://github.com/owner/test-repo",
        "description": "Test repository"
    }


@pytest.fixture
def sample_jira_project():
    """Sample Jira project data."""
    return {
        "id": "10000",
        "key": "TEST",
        "name": "Test Project",
        "projectTypeKey": "software"
    }


@pytest.fixture
def sample_jira_issue():
    """Sample Jira issue data."""
    return {
        "ticket": "TEST-1",
        "title": "Test Issue",
        "status": "To Do",
        "assignee": "John Doe",
        "description": "Test description"
    }


@pytest.fixture
def sample_context_data():
    """Sample context data for testing."""
    return {
        "current_repository": {"owner": "testuser", "repo": "testrepo"},
        "current_jira_project": {"key": "TEST", "name": "Test Project"},
        "recent_actions": [
            {"action": "created_issue", "details": "TEST-1"},
            {"action": "created_pr", "details": "PR #1"}
        ],
        "conversation_history": [
            {"role": "user", "content": "Create an issue"},
            {"role": "assistant", "content": "Issue created successfully"}
        ]
    }
