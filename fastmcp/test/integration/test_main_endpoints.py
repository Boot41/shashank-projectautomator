"""
Comprehensive integration tests for main endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from app.main import app


@pytest.mark.integration
class TestMainEndpoints:
    """Test cases for main.py endpoints."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)

    def test_health_endpoint(self):
        """Test health endpoint."""
        response = self.client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_adk_agent_endpoint_success(self):
        """Test successful ADK agent endpoint."""
        mock_agent_response = {
            "response": "Test response",
            "toolCalls": [],
            "model_summary": "Test summary"
        }
        
        with patch('app.main.agent') as mock_agent:
            mock_agent.process_prompt = AsyncMock(return_value=mock_agent_response)
            
            response = self.client.post(
                "/adk/agent",
                json={"prompt": "Test prompt", "session_id": "test-session"}
            )
            
            assert response.status_code == 200
            assert response.json() == mock_agent_response

    def test_adk_agent_endpoint_missing_prompt(self):
        """Test ADK agent endpoint with missing prompt."""
        response = self.client.post(
            "/adk/agent",
            json={"session_id": "test-session"}
        )
        
        assert response.status_code == 400
        assert "prompt" in response.json()["detail"]

    def test_adk_agent_endpoint_missing_session_id(self):
        """Test ADK agent endpoint with missing session_id."""
        response = self.client.post(
            "/adk/agent",
            json={"prompt": "Test prompt"}
        )
        
        assert response.status_code == 400
        assert "session_id" in response.json()["detail"]

    def test_adk_agent_endpoint_invalid_json(self):
        """Test ADK agent endpoint with invalid JSON."""
        response = self.client.post(
            "/adk/agent",
            data="invalid json"
        )
        
        assert response.status_code == 422

    def test_adk_agent_endpoint_agent_error(self):
        """Test ADK agent endpoint with agent error."""
        with patch('app.main.agent') as mock_agent:
            mock_agent.process_prompt = AsyncMock(side_effect=Exception("Agent error"))
            
            response = self.client.post(
                "/adk/agent",
                json={"prompt": "Test prompt", "session_id": "test-session"}
            )
            
            assert response.status_code == 500
            assert "error" in response.json()

    def test_adk_agent_endpoint_with_tool_calls(self):
        """Test ADK agent endpoint with tool calls."""
        mock_agent_response = {
            "response": "Test response",
            "toolCalls": [
                {
                    "name": "github_get_repos",
                    "args": {"username": "testuser"},
                    "result": {"repos": [{"name": "test-repo"}]}
                }
            ],
            "model_summary": "Test summary"
        }
        
        with patch('app.main.agent') as mock_agent:
            mock_agent.process_prompt = AsyncMock(return_value=mock_agent_response)
            
            response = self.client.post(
                "/adk/agent",
                json={"prompt": "Get my repos", "session_id": "test-session"}
            )
            
            assert response.status_code == 200
            assert response.json() == mock_agent_response
            assert len(response.json()["toolCalls"]) == 1

    def test_adk_agent_endpoint_with_context(self):
        """Test ADK agent endpoint with context."""
        mock_agent_response = {
            "response": "Test response with context",
            "toolCalls": [],
            "model_summary": "Test summary"
        }
        
        with patch('app.main.agent') as mock_agent:
            mock_agent.process_prompt = AsyncMock(return_value=mock_agent_response)
            
            response = self.client.post(
                "/adk/agent",
                json={
                    "prompt": "What was my previous project?",
                    "session_id": "test-session"
                }
            )
            
            assert response.status_code == 200
            assert response.json() == mock_agent_response

    def test_adk_agent_endpoint_clear_context(self):
        """Test ADK agent endpoint with clear context command."""
        mock_agent_response = {
            "response": "Context cleared successfully",
            "toolCalls": [],
            "model_summary": "Context cleared"
        }
        
        with patch('app.main.agent') as mock_agent:
            mock_agent.process_prompt = AsyncMock(return_value=mock_agent_response)
            
            response = self.client.post(
                "/adk/agent",
                json={
                    "prompt": "/clearcontext",
                    "session_id": "test-session"
                }
            )
            
            assert response.status_code == 200
            assert response.json() == mock_agent_response

    def test_adk_agent_endpoint_help_command(self):
        """Test ADK agent endpoint with help command."""
        mock_agent_response = {
            "response": "Available commands: /help, /clearcontext, /quit",
            "toolCalls": [],
            "model_summary": "Help information"
        }
        
        with patch('app.main.agent') as mock_agent:
            mock_agent.process_prompt = AsyncMock(return_value=mock_agent_response)
            
            response = self.client.post(
                "/adk/agent",
                json={
                    "prompt": "/help",
                    "session_id": "test-session"
                }
            )
            
            assert response.status_code == 200
            assert response.json() == mock_agent_response

    def test_adk_agent_endpoint_github_commands(self):
        """Test ADK agent endpoint with GitHub commands."""
        mock_agent_response = {
            "response": "GitHub command executed",
            "toolCalls": [
                {
                    "name": "github_get_repos",
                    "args": {"username": "testuser"},
                    "result": {"repos": [{"name": "test-repo"}]}
                }
            ],
            "model_summary": "GitHub operation completed"
        }
        
        with patch('app.main.agent') as mock_agent:
            mock_agent.process_prompt = AsyncMock(return_value=mock_agent_response)
            
            response = self.client.post(
                "/adk/agent",
                json={
                    "prompt": "list my repositories",
                    "session_id": "test-session"
                }
            )
            
            assert response.status_code == 200
            assert response.json() == mock_agent_response

    def test_adk_agent_endpoint_jira_commands(self):
        """Test ADK agent endpoint with Jira commands."""
        mock_agent_response = {
            "response": "Jira command executed",
            "toolCalls": [
                {
                    "name": "jira_get_projects",
                    "args": {},
                    "result": {"projects": [{"name": "TEST"}]}
                }
            ],
            "model_summary": "Jira operation completed"
        }
        
        with patch('app.main.agent') as mock_agent:
            mock_agent.process_prompt = AsyncMock(return_value=mock_agent_response)
            
            response = self.client.post(
                "/adk/agent",
                json={
                    "prompt": "list jira projects",
                    "session_id": "test-session"
                }
            )
            
            assert response.status_code == 200
            assert response.json() == mock_agent_response

    def test_adk_agent_endpoint_email_commands(self):
        """Test ADK agent endpoint with email commands."""
        mock_agent_response = {
            "response": "Email command executed",
            "toolCalls": [
                {
                    "name": "email_send",
                    "args": {
                        "to": "test@example.com",
                        "subject": "Test Subject",
                        "body": "Test Body"
                    },
                    "result": {"status": "sent"}
                }
            ],
            "model_summary": "Email sent successfully"
        }
        
        with patch('app.main.agent') as mock_agent:
            mock_agent.process_prompt = AsyncMock(return_value=mock_agent_response)
            
            response = self.client.post(
                "/adk/agent",
                json={
                    "prompt": "send email to test@example.com",
                    "session_id": "test-session"
                }
            )
            
            assert response.status_code == 200
            assert response.json() == mock_agent_response

    def test_adk_agent_endpoint_mixed_commands(self):
        """Test ADK agent endpoint with mixed commands."""
        mock_agent_response = {
            "response": "Mixed commands executed",
            "toolCalls": [
                {
                    "name": "github_get_repos",
                    "args": {"username": "testuser"},
                    "result": {"repos": [{"name": "test-repo"}]}
                },
                {
                    "name": "jira_get_projects",
                    "args": {},
                    "result": {"projects": [{"name": "TEST"}]}
                }
            ],
            "model_summary": "Multiple operations completed"
        }
        
        with patch('app.main.agent') as mock_agent:
            mock_agent.process_prompt = AsyncMock(return_value=mock_agent_response)
            
            response = self.client.post(
                "/adk/agent",
                json={
                    "prompt": "get my repos and jira projects",
                    "session_id": "test-session"
                }
            )
            
            assert response.status_code == 200
            assert response.json() == mock_agent_response
            assert len(response.json()["toolCalls"]) == 2

    def test_adk_agent_endpoint_large_prompt(self):
        """Test ADK agent endpoint with large prompt."""
        large_prompt = "Test prompt " * 1000  # Large prompt
        
        mock_agent_response = {
            "response": "Large prompt processed",
            "toolCalls": [],
            "model_summary": "Large prompt handled"
        }
        
        with patch('app.main.agent') as mock_agent:
            mock_agent.process_prompt = AsyncMock(return_value=mock_agent_response)
            
            response = self.client.post(
                "/adk/agent",
                json={
                    "prompt": large_prompt,
                    "session_id": "test-session"
                }
            )
            
            assert response.status_code == 200
            assert response.json() == mock_agent_response

    def test_adk_agent_endpoint_special_characters(self):
        """Test ADK agent endpoint with special characters."""
        special_prompt = "Test prompt with special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        
        mock_agent_response = {
            "response": "Special characters processed",
            "toolCalls": [],
            "model_summary": "Special characters handled"
        }
        
        with patch('app.main.agent') as mock_agent:
            mock_agent.process_prompt = AsyncMock(return_value=mock_agent_response)
            
            response = self.client.post(
                "/adk/agent",
                json={
                    "prompt": special_prompt,
                    "session_id": "test-session"
                }
            )
            
            assert response.status_code == 200
            assert response.json() == mock_agent_response

    def test_adk_agent_endpoint_unicode_characters(self):
        """Test ADK agent endpoint with unicode characters."""
        unicode_prompt = "Test prompt with unicode: 你好世界 🌍"
        
        mock_agent_response = {
            "response": "Unicode characters processed",
            "toolCalls": [],
            "model_summary": "Unicode characters handled"
        }
        
        with patch('app.main.agent') as mock_agent:
            mock_agent.process_prompt = AsyncMock(return_value=mock_agent_response)
            
            response = self.client.post(
                "/adk/agent",
                json={
                    "prompt": unicode_prompt,
                    "session_id": "test-session"
                }
            )
            
            assert response.status_code == 200
            assert response.json() == mock_agent_response

    def test_adk_agent_endpoint_empty_prompt(self):
        """Test ADK agent endpoint with empty prompt."""
        mock_agent_response = {
            "response": "Empty prompt handled",
            "toolCalls": [],
            "model_summary": "Empty prompt processed"
        }
        
        with patch('app.main.agent') as mock_agent:
            mock_agent.process_prompt = AsyncMock(return_value=mock_agent_response)
            
            response = self.client.post(
                "/adk/agent",
                json={
                    "prompt": "",
                    "session_id": "test-session"
                }
            )
            
            assert response.status_code == 200
            assert response.json() == mock_agent_response

    def test_adk_agent_endpoint_whitespace_prompt(self):
        """Test ADK agent endpoint with whitespace-only prompt."""
        mock_agent_response = {
            "response": "Whitespace prompt handled",
            "toolCalls": [],
            "model_summary": "Whitespace prompt processed"
        }
        
        with patch('app.main.agent') as mock_agent:
            mock_agent.process_prompt = AsyncMock(return_value=mock_agent_response)
            
            response = self.client.post(
                "/adk/agent",
                json={
                    "prompt": "   \n\t   ",
                    "session_id": "test-session"
                }
            )
            
            assert response.status_code == 200
            assert response.json() == mock_agent_response

    def test_adk_agent_endpoint_concurrent_requests(self):
        """Test ADK agent endpoint with concurrent requests."""
        mock_agent_response = {
            "response": "Concurrent request processed",
            "toolCalls": [],
            "model_summary": "Concurrent request handled"
        }
        
        with patch('app.main.agent') as mock_agent:
            mock_agent.process_prompt = AsyncMock(return_value=mock_agent_response)
            
            # Simulate concurrent requests
            responses = []
            for i in range(5):
                response = self.client.post(
                    "/adk/agent",
                    json={
                        "prompt": f"Test prompt {i}",
                        "session_id": f"test-session-{i}"
                    }
                )
                responses.append(response)
            
            # All requests should succeed
            for response in responses:
                assert response.status_code == 200
                assert response.json() == mock_agent_response
