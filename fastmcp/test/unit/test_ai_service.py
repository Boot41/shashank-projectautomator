"""
Comprehensive unit tests for AI service.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.ai_service import process_natural_language, generate_ai_response
from app.models.ai_models import ProcessedCommand, AIResponse


@pytest.mark.unit
class TestAIService:
    """Test cases for AI service functions."""

    @pytest.mark.asyncio
    async def test_process_natural_language_with_mock(self, mock_genai):
        """Test process_natural_language with mocked genai."""
        result = await process_natural_language("Create an issue")
        
        assert isinstance(result, ProcessedCommand)
        assert result.command == "create_issue"
        assert result.parameters is not None

    @pytest.mark.asyncio
    async def test_process_natural_language_with_function_calls(self, mock_genai):
        """Test process_natural_language with function calls."""
        mock_function_call = MagicMock()
        mock_function_call.name = "jira_create_issue"
        mock_function_call.args = {"summary": "Test Issue", "description": "Test description"}
        
        mock_response = MagicMock()
        mock_response.text = "I'll create an issue for you"
        mock_response.function_calls = [mock_function_call]
        
        mock_model = MagicMock()
        mock_model.generate_content_async.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        result = await process_natural_language("Create an issue with title Test Issue")
        
        assert isinstance(result, ProcessedCommand)
        assert result.command == "jira_create_issue"
        assert result.parameters["summary"] == "Test Issue"

    @pytest.mark.asyncio
    async def test_generate_ai_response_with_mock(self, mock_genai):
        """Test generate_ai_response with mocked genai."""
        result = await generate_ai_response("Test prompt")
        
        assert isinstance(result, AIResponse)
        assert result.response == "Test response"

    @pytest.mark.asyncio
    async def test_ai_service_with_mock_settings(self, mock_genai):
        """Test AI service with mock settings."""
        with patch('app.services.ai_service.settings') as mock_settings:
            mock_settings.gemini_api_key = "test-api-key"
            mock_settings.gemini_model = "gemini-2.5-flash-lite"
            
            result = await process_natural_language("Test prompt")
            assert isinstance(result, ProcessedCommand)
            
            result = await generate_ai_response("Test prompt")
            assert isinstance(result, AIResponse)

    @pytest.mark.asyncio
    async def test_ai_service_model_configuration(self, mock_genai):
        """Test AI service model configuration."""
        with patch('app.services.ai_service.settings') as mock_settings:
            mock_settings.gemini_api_key = "test-api-key"
            mock_settings.gemini_model = "gemini-2.5-flash-lite"
            
            await process_natural_language("Test prompt")
            
            # Verify genai.configure was called with correct API key
            mock_genai.configure.assert_called_with(api_key="test-api-key")
            
            # Verify GenerativeModel was called with correct model
            mock_genai.GenerativeModel.assert_called_with("gemini-2.5-flash-lite")

    @pytest.mark.asyncio
    async def test_ai_service_error_handling(self):
        """Test error handling in AI service functions."""
        with patch('app.services.ai_service.genai') as mock_genai:
            mock_genai.GenerativeModel.side_effect = Exception("API Error")
            
            with pytest.raises(Exception):
                await process_natural_language("Test prompt")
            
            with pytest.raises(Exception):
                await generate_ai_response("Test prompt")

    @pytest.mark.asyncio
    async def test_ai_service_with_different_prompts(self, mock_genai):
        """Test AI service with different types of prompts."""
        test_cases = [
            "Create an issue",
            "List my repositories",
            "Merge pull request #1",
            "Send email to user@example.com",
            "What are my recent actions?"
        ]
        
        for prompt in test_cases:
            result = await process_natural_language(prompt)
            assert isinstance(result, ProcessedCommand)
            assert result.command is not None

    @pytest.mark.asyncio
    async def test_ai_service_with_complex_prompts(self, mock_genai):
        """Test AI service with complex prompts."""
        complex_prompts = [
            "Create an issue in project TEST with title 'Bug Fix' and assign it to John Doe",
            "List all open pull requests in the main repository and show their status",
            "Merge pull request #5 with squash method and custom commit message",
            "Send a summary email of issue TEST-1 to stakeholder@company.com"
        ]
        
        for prompt in complex_prompts:
            result = await process_natural_language(prompt)
            assert isinstance(result, ProcessedCommand)
            assert result.command is not None
            assert result.parameters is not None

    @pytest.mark.asyncio
    async def test_ai_service_response_generation(self, mock_genai):
        """Test AI response generation with different contexts."""
        test_cases = [
            ("Simple prompt", "Simple context"),
            ("Complex prompt", "Complex context with multiple items"),
            ("Empty context", ""),
            ("Long context", "A" * 1000)
        ]
        
        for prompt, context in test_cases:
            result = await generate_ai_response(prompt)
            assert isinstance(result, AIResponse)
            assert result.response is not None

    def test_ai_service_imports(self):
        """Test that AI service functions can be imported."""
        from app.services.ai_service import process_natural_language, generate_ai_response
        
        assert callable(process_natural_language)
        assert callable(generate_ai_response)

    @pytest.mark.asyncio
    async def test_ai_service_async_behavior(self):
        """Test AI service async behavior."""
        import asyncio
        
        async def mock_ai_call():
            await asyncio.sleep(0.1)  # Simulate async delay
            return ProcessedCommand(command="test", parameters={})
        
        with patch('app.services.ai_service.process_natural_language', side_effect=mock_ai_call):
            result = await process_natural_language("Test prompt")
            assert isinstance(result, ProcessedCommand)
        
        async def mock_response_call():
            await asyncio.sleep(0.1)  # Simulate async delay
            return AIResponse(response="async response")
        
        with patch('app.services.ai_service.generate_ai_response', side_effect=mock_response_call):
            result = await generate_ai_response("Test prompt")
            assert isinstance(result, AIResponse)

    @pytest.mark.asyncio
    async def test_ai_service_with_empty_prompts(self, mock_genai):
        """Test AI service with empty or whitespace prompts."""
        empty_prompts = ["", "   ", "\n\t", "   \n   "]
        
        for prompt in empty_prompts:
            result = await process_natural_language(prompt)
            assert isinstance(result, ProcessedCommand)
            
            result = await generate_ai_response(prompt)
            assert isinstance(result, AIResponse)

    @pytest.mark.asyncio
    async def test_ai_service_with_special_characters(self, mock_genai):
        """Test AI service with special characters in prompts."""
        special_prompts = [
            "Test prompt with special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?",
            "Test prompt with unicode: 你好世界 🌍",
            "Test prompt with newlines:\nLine 1\nLine 2",
            "Test prompt with tabs:\tTabbed content"
        ]
        
        for prompt in special_prompts:
            result = await process_natural_language(prompt)
            assert isinstance(result, ProcessedCommand)
            
            result = await generate_ai_response(prompt)
            assert isinstance(result, AIResponse)
