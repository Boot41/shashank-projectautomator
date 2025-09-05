"""
Comprehensive unit tests for coordinator.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.orchestration.coordinator import GeminiToolsAgent


@pytest.mark.unit
class TestGeminiToolsAgent:
    """Test cases for GeminiToolsAgent."""

    def setup_method(self):
        """Set up test fixtures."""
        self.agent = GeminiToolsAgent()

    def test_agent_initialization(self):
        """Test agent initialization."""
        assert self.agent is not None
        assert hasattr(self.agent, 'process_prompt')

    def test_build_tool_declarations(self):
        """Test tool declarations building."""
        declarations = self.agent._build_tool_declarations()
        
        assert isinstance(declarations, list)
        assert len(declarations) > 0
        
        # Check for specific tools
        tool_names = [tool["name"] for tool in declarations]
        assert "github_get_repos" in tool_names
        assert "jira_get_projects" in tool_names
        assert "email_send" in tool_names

    def test_tool_declarations_structure(self):
        """Test that tool declarations have proper structure."""
        declarations = self.agent._build_tool_declarations()
        
        for tool in declarations:
            assert "name" in tool
            assert "description" in tool
            assert "parameters" in tool
            assert "type" in tool["parameters"]
            assert "properties" in tool["parameters"]

    def test_system_instructions(self):
        """Test that system instructions are properly formatted."""
        system_instructions = self.agent._get_system_instructions()
        
        assert isinstance(system_instructions, str)
        assert len(system_instructions) > 0
        assert "GitHub" in system_instructions
        assert "Jira" in system_instructions
        assert "Email" in system_instructions

    @pytest.mark.asyncio
    async def test_process_prompt_success(self):
        """Test successful prompt processing."""
        mock_response = {
            "text": "Test response",
            "function_calls": []
        }
        
        with patch.object(self.agent, '_call_gemini_with_tools', return_value=mock_response):
            result = await self.agent.process_prompt("Test prompt", "test-session")
            
            assert result is not None
            assert "response" in result

    @pytest.mark.asyncio
    async def test_process_prompt_with_function_calls(self):
        """Test prompt processing with function calls."""
        mock_function_call = {
            "name": "github_get_repos",
            "args": {"username": "testuser"}
        }
        
        mock_response = {
            "text": "Test response",
            "function_calls": [mock_function_call]
        }
        
        mock_tool_result = {"repos": [{"name": "test-repo"}]}
        
        with patch.object(self.agent, '_call_gemini_with_tools', return_value=mock_response):
            with patch.object(self.agent, '_execute_tool_call', return_value=mock_tool_result):
                with patch.object(self.agent, '_generate_model_summary', return_value="Summary"):
                    result = await self.agent.process_prompt("Get my repos", "test-session")
                    
                    assert result is not None
                    assert "response" in result
                    assert "toolCalls" in result

    @pytest.mark.asyncio
    async def test_execute_tool_call_success(self):
        """Test successful tool execution."""
        tool_call = {
            "name": "github_get_repos",
            "args": {"username": "testuser"}
        }
        
        mock_result = {"repos": [{"name": "test-repo"}]}
        
        with patch('app.orchestration.coordinator.ALL_TOOL_RUNNERS') as mock_runners:
            mock_runners.get.return_value = AsyncMock(return_value=mock_result)
            
            result = await self.agent._execute_tool_call(tool_call)
            
            assert result == mock_result

    @pytest.mark.asyncio
    async def test_execute_tool_call_error(self):
        """Test tool execution with error."""
        tool_call = {
            "name": "nonexistent_tool",
            "args": {}
        }
        
        with patch('app.orchestration.coordinator.ALL_TOOL_RUNNERS') as mock_runners:
            mock_runners.get.return_value = None
            
            result = await self.agent._execute_tool_call(tool_call)
            
            assert "error" in result

    @pytest.mark.asyncio
    async def test_execute_tool_call_exception(self):
        """Test tool execution with exception."""
        tool_call = {
            "name": "github_get_repos",
            "args": {"username": "testuser"}
        }
        
        with patch('app.orchestration.coordinator.ALL_TOOL_RUNNERS') as mock_runners:
            mock_runners.get.return_value = AsyncMock(side_effect=Exception("Tool error"))
            
            result = await self.agent._execute_tool_call(tool_call)
            
            assert "error" in result
            assert "Tool error" in result["error"]

    @pytest.mark.asyncio
    async def test_generate_model_summary_success(self):
        """Test successful model summary generation."""
        tool_results = [
            {"repos": [{"name": "test-repo"}]},
            {"issues": [{"title": "test-issue"}]}
        ]
        
        with patch('app.services.ai_service.generate_model_summary', return_value="Generated summary"):
            result = await self.agent._generate_model_summary("Test prompt", tool_results)
            
            assert result == "Generated summary"

    @pytest.mark.asyncio
    async def test_generate_model_summary_error(self):
        """Test model summary generation with error."""
        tool_results = [{"error": "Tool failed"}]
        
        with patch('app.services.ai_service.generate_model_summary', side_effect=Exception("AI Error")):
            result = await self.agent._generate_model_summary("Test prompt", tool_results)
            
            assert "error" in result

    @pytest.mark.asyncio
    async def test_call_gemini_with_tools_success(self):
        """Test successful Gemini API call with tools."""
        mock_response = {
            "text": "Test response",
            "function_calls": []
        }
        
        with patch('app.services.ai_service.process_prompt_with_tools', return_value=mock_response):
            result = await self.agent._call_gemini_with_tools("Test prompt", [])
            
            assert result == mock_response

    @pytest.mark.asyncio
    async def test_call_gemini_with_tools_error(self):
        """Test Gemini API call with error."""
        with patch('app.services.ai_service.process_prompt_with_tools', side_effect=Exception("API Error")):
            result = await self.agent._call_gemini_with_tools("Test prompt", [])
            
            assert "error" in result

    def test_normalize_tool_arguments(self):
        """Test tool argument normalization."""
        tool_call = {
            "name": "github_create_issue",
            "args": {
                "owner": "testuser",
                "repo": "testrepo",
                "title": "Test Issue",
                "body": "Test description"
            }
        }
        
        normalized = self.agent._normalize_tool_arguments(tool_call)
        
        assert normalized["name"] == "github_create_issue"
        assert normalized["args"]["owner"] == "testuser"
        assert normalized["args"]["repo"] == "testrepo"

    @pytest.mark.asyncio
    async def test_process_prompt_with_context(self):
        """Test prompt processing with context."""
        mock_context = {
            "current_repository": {"owner": "testuser", "repo": "testrepo"},
            "recent_actions": [{"action": "created_issue", "details": "TEST-1"}]
        }
        
        with patch('app.services.context_service.ContextService') as mock_context_service:
            mock_context_service.return_value.get_context_for_prompt.return_value = mock_context
            
            mock_response = {
                "text": "Test response",
                "function_calls": []
            }
            
            with patch.object(self.agent, '_call_gemini_with_tools', return_value=mock_response):
                result = await self.agent.process_prompt("Test prompt", "test-session")
                
                assert result is not None
                assert "response" in result

    @pytest.mark.asyncio
    async def test_process_prompt_iterative_tool_calling(self):
        """Test iterative tool calling."""
        mock_function_calls = [
            {
                "name": "github_get_repos",
                "args": {"username": "testuser"}
            },
            {
                "name": "jira_get_projects",
                "args": {}
            }
        ]
        
        mock_response = {
            "text": "Test response",
            "function_calls": mock_function_calls
        }
        
        mock_tool_results = [
            {"repos": [{"name": "test-repo"}]},
            {"projects": [{"name": "TEST"}]}
        ]
        
        with patch.object(self.agent, '_call_gemini_with_tools', return_value=mock_response):
            with patch.object(self.agent, '_execute_tool_call', side_effect=mock_tool_results):
                with patch.object(self.agent, '_generate_model_summary', return_value="Summary"):
                    result = await self.agent.process_prompt("Get repos and projects", "test-session")
                    
                    assert result is not None
                    assert "response" in result
                    assert "toolCalls" in result
                    assert len(result["toolCalls"]) == 2

    @pytest.mark.asyncio
    async def test_process_prompt_malformed_function_call(self):
        """Test handling of malformed function calls."""
        mock_response = {
            "text": "Test response",
            "function_calls": [
                {
                    "name": "github_get_repos",
                    # Missing args
                }
            ]
        }
        
        with patch.object(self.agent, '_call_gemini_with_tools', return_value=mock_response):
            with patch.object(self.agent, '_generate_model_summary', return_value="Summary"):
                result = await self.agent.process_prompt("Get repos", "test-session")
                
                assert result is not None
                assert "response" in result
                assert "toolCalls" in result
                assert len(result["toolCalls"]) == 1
                assert "error" in result["toolCalls"][0]

    @pytest.mark.asyncio
    async def test_process_prompt_empty_response(self):
        """Test handling of empty response."""
        mock_response = {
            "text": "",
            "function_calls": []
        }
        
        with patch.object(self.agent, '_call_gemini_with_tools', return_value=mock_response):
            result = await self.agent.process_prompt("Test prompt", "test-session")
            
            assert result is not None
            assert "response" in result
            assert result["response"] == "I apologize, but I couldn't generate a response. Please try again."

    @pytest.mark.asyncio
    async def test_process_prompt_with_tool_errors(self):
        """Test handling of tool execution errors."""
        mock_function_call = {
            "name": "github_get_repos",
            "args": {"username": "testuser"}
        }
        
        mock_response = {
            "text": "Test response",
            "function_calls": [mock_function_call]
        }
        
        mock_tool_result = {"error": "Tool execution failed"}
        
        with patch.object(self.agent, '_call_gemini_with_tools', return_value=mock_response):
            with patch.object(self.agent, '_execute_tool_call', return_value=mock_tool_result):
                with patch.object(self.agent, '_generate_model_summary', return_value="Summary"):
                    result = await self.agent.process_prompt("Get repos", "test-session")
                    
                    assert result is not None
                    assert "response" in result
                    assert "toolCalls" in result
                    assert result["toolCalls"][0]["result"]["error"] == "Tool execution failed"

    @pytest.mark.asyncio
    async def test_process_prompt_with_context_service_error(self):
        """Test handling of context service errors."""
        with patch('app.services.context_service.ContextService') as mock_context_service:
            mock_context_service.side_effect = Exception("Context service error")
            
            mock_response = {
                "text": "Test response",
                "function_calls": []
            }
            
            with patch.object(self.agent, '_call_gemini_with_tools', return_value=mock_response):
                result = await self.agent.process_prompt("Test prompt", "test-session")
                
                assert result is not None
                assert "response" in result

    @pytest.mark.asyncio
    async def test_process_prompt_with_special_characters(self):
        """Test prompt processing with special characters."""
        special_prompt = "Test prompt with special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        
        mock_response = {
            "text": "Test response",
            "function_calls": []
        }
        
        with patch.object(self.agent, '_call_gemini_with_tools', return_value=mock_response):
            result = await self.agent.process_prompt(special_prompt, "test-session")
            
            assert result is not None
            assert "response" in result

    @pytest.mark.asyncio
    async def test_process_prompt_with_unicode(self):
        """Test prompt processing with unicode characters."""
        unicode_prompt = "Test prompt with unicode: 你好世界 🌍"
        
        mock_response = {
            "text": "Test response",
            "function_calls": []
        }
        
        with patch.object(self.agent, '_call_gemini_with_tools', return_value=mock_response):
            result = await self.agent.process_prompt(unicode_prompt, "test-session")
            
            assert result is not None
            assert "response" in result
