"""
Comprehensive unit tests for Jira service.
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import httpx
from app.services.jira_service import (
    get_jira_projects, get_issues_for_project, create_issue,
    fetch_jira_issue, get_issue_comments, comment_issue,
    get_possible_transitions, transition_issue, assign_issue,
    get_board_id_for_project, get_sprints, move_issue_to_sprint
)
from app.models.jira_models import (
    JiraProject, JiraIssue, JiraIssueBasic, CreateJiraIssue, JiraSprint
)


@pytest.mark.unit
class TestJiraService:
    """Test cases for Jira service functions."""

    @pytest.mark.asyncio
    async def test_get_jira_projects_with_mock_settings(self, mock_settings):
        """Test get_jira_projects with mock settings enabled."""
        result = await get_jira_projects()
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], JiraProject)
        assert result[0].key == "TEST"

    @pytest.mark.asyncio
    async def test_get_jira_projects_with_real_api(self, mock_httpx_client):
        """Test get_jira_projects with real API call."""
        mock_response_data = {
            "values": [
                {
                    "id": "10000",
                    "key": "REAL",
                    "name": "Real Project",
                    "projectTypeKey": "software"
                }
            ]
        }
        
        mock_httpx_client.return_value.__aenter__.return_value.get.return_value.json.return_value = mock_response_data
        
        with patch('app.services.jira_service.settings') as mock_settings:
            mock_settings.jira_mock = False
            mock_settings.jira_base_url = "https://real.atlassian.net"
            mock_settings.jira_email = "real@example.com"
            mock_settings.jira_api_token = "real-token"
            mock_settings.http_timeout = 30
            
            result = await get_jira_projects()
            
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0].key == "REAL"

    @pytest.mark.asyncio
    async def test_get_issues_for_project_with_mock_settings(self, mock_settings):
        """Test get_issues_for_project with mock settings enabled."""
        result = await get_issues_for_project("TEST")
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], JiraIssueBasic)

    @pytest.mark.asyncio
    async def test_get_issues_for_project_with_status_filter(self, mock_settings):
        """Test get_issues_for_project with status filter."""
        result = await get_issues_for_project("TEST", "To Do")
        
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_create_issue_with_mock_settings(self, mock_settings):
        """Test create_issue with mock settings enabled."""
        issue_data = CreateJiraIssue(
            project_key="TEST", 
            summary="Test Issue", 
            description="Test description"
        )
        result = await create_issue(issue_data)
        
        assert isinstance(result, dict)
        assert "key" in result
        assert "summary" in result

    @pytest.mark.asyncio
    async def test_create_issue_with_real_api(self, mock_httpx_client):
        """Test create_issue with real API call."""
        mock_response_data = {
            "id": "10001",
            "key": "REAL-1",
            "self": "https://real.atlassian.net/rest/api/3/issue/10001"
        }
        
        mock_httpx_client.return_value.__aenter__.return_value.post.return_value.json.return_value = mock_response_data
        
        with patch('app.services.jira_service.settings') as mock_settings:
            mock_settings.jira_mock = False
            mock_settings.jira_base_url = "https://real.atlassian.net"
            mock_settings.jira_email = "real@example.com"
            mock_settings.jira_api_token = "real-token"
            mock_settings.http_timeout = 30
            
            issue_data = CreateJiraIssue(
                project_key="REAL", 
                summary="Real Issue", 
                description="Real description"
            )
            result = await create_issue(issue_data)
            
            assert isinstance(result, dict)
            assert result["key"] == "REAL-1"

    @pytest.mark.asyncio
    async def test_fetch_jira_issue_with_mock_settings(self, mock_settings):
        """Test fetch_jira_issue with mock settings enabled."""
        result = await fetch_jira_issue("TEST-1")
        
        assert isinstance(result, JiraIssue)
        assert result.ticket == "TEST-1"
        assert result.title == "Test Issue"

    @pytest.mark.asyncio
    async def test_get_issue_comments_with_mock_settings(self, mock_settings):
        """Test get_issue_comments with mock settings enabled."""
        result = await get_issue_comments("TEST-1")
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert "comment" in result[0]

    @pytest.mark.asyncio
    async def test_comment_issue_with_mock_settings(self, mock_settings):
        """Test comment_issue with mock settings enabled."""
        result = await comment_issue("TEST-1", "Test comment")
        
        assert isinstance(result, dict)
        assert "id" in result
        assert "body" in result

    @pytest.mark.asyncio
    async def test_get_possible_transitions_with_mock_settings(self, mock_settings):
        """Test get_possible_transitions with mock settings enabled."""
        result = await get_possible_transitions("TEST-1")
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert "id" in result[0]
        assert "name" in result[0]

    @pytest.mark.asyncio
    async def test_transition_issue_with_mock_settings(self, mock_settings):
        """Test transition_issue with mock settings enabled."""
        result = await transition_issue("TEST-1", "21")
        
        assert isinstance(result, dict)
        assert result["status"] == "success"
        assert result["transition_id"] == "21"

    @pytest.mark.asyncio
    async def test_assign_issue_with_mock_settings(self, mock_settings):
        """Test assign_issue with mock settings enabled."""
        # This function returns None, so we just test it doesn't raise an exception
        await assign_issue("TEST-1", "John Doe")

    @pytest.mark.asyncio
    async def test_get_board_id_for_project_with_mock_settings(self, mock_settings):
        """Test get_board_id_for_project with mock settings enabled."""
        result = await get_board_id_for_project("TEST")
        
        assert isinstance(result, int)
        assert result == 1

    @pytest.mark.asyncio
    async def test_get_sprints_with_mock_settings(self, mock_settings):
        """Test get_sprints with mock settings enabled."""
        result = await get_sprints("TEST")
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], JiraSprint)

    @pytest.mark.asyncio
    async def test_move_issue_to_sprint_with_mock_settings(self, mock_settings):
        """Test move_issue_to_sprint with mock settings enabled."""
        # This function returns None, so we just test it doesn't raise an exception
        await move_issue_to_sprint(1, "TEST-1")

    @pytest.mark.asyncio
    async def test_jira_service_error_handling(self, mock_httpx_client):
        """Test error handling in Jira service functions."""
        mock_httpx_client.return_value.__aenter__.return_value.get.side_effect = httpx.RequestError("Network error")
        
        with patch('app.services.jira_service.settings') as mock_settings:
            mock_settings.jira_mock = False
            mock_settings.jira_base_url = "https://invalid.atlassian.net"
            mock_settings.jira_email = "invalid@example.com"
            mock_settings.jira_api_token = "invalid-token"
            mock_settings.http_timeout = 30
            
            with pytest.raises(Exception):
                await get_jira_projects()

    @pytest.mark.asyncio
    async def test_jira_service_http_status_error(self, mock_httpx_client):
        """Test HTTP status error handling."""
        mock_response = AsyncMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Unauthorized", request=MagicMock(), response=MagicMock()
        )
        mock_httpx_client.return_value.__aenter__.return_value.get.return_value = mock_response
        
        with patch('app.services.jira_service.settings') as mock_settings:
            mock_settings.jira_mock = False
            mock_settings.jira_base_url = "https://invalid.atlassian.net"
            mock_settings.jira_email = "invalid@example.com"
            mock_settings.jira_api_token = "invalid-token"
            mock_settings.http_timeout = 30
            
            with pytest.raises(Exception):
                await get_jira_projects()

    def test_jira_service_imports(self):
        """Test that all Jira service functions can be imported."""
        from app.services.jira_service import (
            get_jira_projects, get_issues_for_project, create_issue,
            fetch_jira_issue, get_issue_comments, comment_issue,
            get_possible_transitions, transition_issue, assign_issue,
            get_board_id_for_project, get_sprints, move_issue_to_sprint
        )
        
        assert callable(get_jira_projects)
        assert callable(get_issues_for_project)
        assert callable(create_issue)
        assert callable(fetch_jira_issue)
        assert callable(get_issue_comments)
        assert callable(comment_issue)
        assert callable(get_possible_transitions)
        assert callable(transition_issue)
        assert callable(assign_issue)
        assert callable(get_board_id_for_project)
        assert callable(get_sprints)
        assert callable(move_issue_to_sprint)

    @pytest.mark.asyncio
    async def test_jira_issue_parsing_with_complex_data(self, mock_httpx_client):
        """Test Jira issue parsing with complex field data."""
        mock_response_data = {
            "issues": [
                {
                    "id": "10001",
                    "key": "TEST-1",
                    "fields": {
                        "summary": "Complex Issue",
                        "description": "Complex description",
                        "status": {"name": "In Progress"},
                        "assignee": {"displayName": "Jane Doe"},
                        "reporter": {"displayName": "John Doe"},
                        "created": "2023-01-01T00:00:00.000+0000",
                        "updated": "2023-01-02T00:00:00.000+0000",
                        "duedate": "2023-01-15",
                        "priority": {"name": "High"}
                    }
                }
            ]
        }
        
        mock_httpx_client.return_value.__aenter__.return_value.get.return_value.json.return_value = mock_response_data
        
        with patch('app.services.jira_service.settings') as mock_settings:
            mock_settings.jira_mock = False
            mock_settings.jira_base_url = "https://test.atlassian.net"
            mock_settings.jira_email = "test@example.com"
            mock_settings.jira_api_token = "test-token"
            mock_settings.http_timeout = 30
            
            result = await get_issues_for_project("TEST")
            
            assert len(result) == 1
            assert result[0].key == "TEST-1"
            assert result[0].summary == "Complex Issue"
            assert result[0].assignee == "Jane Doe"
            assert result[0].due_date == "2023-01-15"
