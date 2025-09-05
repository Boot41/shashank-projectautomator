"""
Comprehensive unit tests for GitHub service.
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import httpx
from app.services.github_service import (
    get_repos, get_branches, create_branch, create_issue, 
    create_pull_request, get_pull_requests, merge_pull_request,
    close_pull_request, get_pull_request_files
)
from app.models.github_models import (
    GithubRepo, GithubBranch, CreateGithubIssue, CreatePullRequest,
    PullRequest, GithubIssue
)


@pytest.mark.unit
class TestGitHubService:
    """Test cases for GitHub service functions."""

    @pytest.mark.asyncio
    async def test_get_repos_with_mock_settings(self, mock_settings):
        """Test get_repos with mock settings enabled."""
        result = await get_repos()
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], GithubRepo)
        assert result[0].name == "test-repo"

    @pytest.mark.asyncio
    async def test_get_repos_with_real_api(self, mock_httpx_client):
        """Test get_repos with real API call."""
        mock_response_data = [
            {
                "name": "real-repo",
                "full_name": "user/real-repo",
                "private": False,
                "html_url": "https://github.com/user/real-repo",
                "description": "Real repository"
            }
        ]
        
        mock_httpx_client.return_value.__aenter__.return_value.get.return_value.json.return_value = mock_response_data
        
        with patch('app.services.github_service.settings') as mock_settings:
            mock_settings.github_mock = False
            mock_settings.github_token = "real-token"
            mock_settings.github_api_url = "https://api.github.com"
            mock_settings.github_user_agent = "test-agent"
            mock_settings.http_timeout = 30
            
            result = await get_repos()
            
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0].name == "real-repo"

    @pytest.mark.asyncio
    async def test_get_branches_with_mock_settings(self, mock_settings):
        """Test get_branches with mock settings enabled."""
        result = await get_branches("owner", "repo")
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], GithubBranch)

    @pytest.mark.asyncio
    async def test_create_branch_with_mock_settings(self, mock_settings):
        """Test create_branch with mock settings enabled."""
        result = await create_branch("owner", "repo", "feature-branch", "main")
        
        assert isinstance(result, GithubBranch)
        assert result.name == "feature-branch"
        assert result.commit_sha == "xyz"

    @pytest.mark.asyncio
    async def test_create_branch_with_real_api(self, mock_httpx_client):
        """Test create_branch with real API call."""
        mock_response_data = {
            "ref": "refs/heads/feature-branch",
            "object": {"sha": "abc123"}
        }
        
        mock_httpx_client.return_value.__aenter__.return_value.post.return_value.json.return_value = mock_response_data
        
        with patch('app.services.github_service.settings') as mock_settings:
            mock_settings.github_mock = False
            mock_settings.github_token = "real-token"
            mock_settings.github_api_url = "https://api.github.com"
            mock_settings.github_user_agent = "test-agent"
            mock_settings.http_timeout = 30
            
            result = await create_branch("owner", "repo", "feature-branch", "main")
            
            assert isinstance(result, GithubBranch)
            assert result.name == "feature-branch"

    @pytest.mark.asyncio
    async def test_create_issue_with_mock_settings(self, mock_settings):
        """Test create_issue with mock settings enabled."""
        issue_data = CreateGithubIssue(title="Test Issue", body="Test description")
        result = await create_issue("owner", "repo", issue_data)
        
        assert isinstance(result, GithubIssue)
        assert result.title == "Test Issue"
        assert result.state == "open"

    @pytest.mark.asyncio
    async def test_create_pull_request_with_mock_settings(self, mock_settings):
        """Test create_pull_request with mock settings enabled."""
        pr_data = CreatePullRequest(
            title="Test PR", 
            body="Test description", 
            head="feature-branch", 
            base="main"
        )
        result = await create_pull_request("owner", "repo", pr_data)
        
        assert isinstance(result, PullRequest)
        assert result.title == "Test PR"
        assert result.state == "open"

    @pytest.mark.asyncio
    async def test_get_pull_requests_with_mock_settings(self, mock_settings):
        """Test get_pull_requests with mock settings enabled."""
        result = await get_pull_requests("owner", "repo", "open")
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], PullRequest)

    @pytest.mark.asyncio
    async def test_merge_pull_request_with_mock_settings(self, mock_settings):
        """Test merge_pull_request with mock settings enabled."""
        result = await merge_pull_request("owner", "repo", 1, "Merge commit", "Merge message", "merge")
        
        assert isinstance(result, dict)
        assert result["merged"] is True
        assert "commit_sha" in result

    @pytest.mark.asyncio
    async def test_merge_pull_request_with_defaults(self, mock_settings):
        """Test merge_pull_request with default parameters."""
        result = await merge_pull_request("owner", "repo", 1)
        
        assert isinstance(result, dict)
        assert result["merged"] is True
        assert "commit_title" in result
        assert "commit_message" in result

    @pytest.mark.asyncio
    async def test_close_pull_request_with_mock_settings(self, mock_settings):
        """Test close_pull_request with mock settings enabled."""
        result = await close_pull_request("owner", "repo", 1)
        
        assert isinstance(result, dict)
        assert result["number"] == 1
        assert result["state"] == "closed"

    @pytest.mark.asyncio
    async def test_get_pull_request_files_with_mock_settings(self, mock_settings):
        """Test get_pull_request_files with mock settings enabled."""
        result = await get_pull_request_files("owner", "repo", 1)
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert "filename" in result[0]

    @pytest.mark.asyncio
    async def test_github_service_error_handling(self, mock_httpx_client):
        """Test error handling in GitHub service functions."""
        mock_httpx_client.return_value.__aenter__.return_value.get.side_effect = httpx.RequestError("Network error")
        
        with patch('app.services.github_service.settings') as mock_settings:
            mock_settings.github_mock = False
            mock_settings.github_token = "invalid-token"
            mock_settings.github_api_url = "https://api.github.com"
            mock_settings.github_user_agent = "test-agent"
            mock_settings.http_timeout = 30
            
            with pytest.raises(Exception):
                await get_repos()

    @pytest.mark.asyncio
    async def test_github_service_http_status_error(self, mock_httpx_client):
        """Test HTTP status error handling."""
        mock_response = AsyncMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Not Found", request=MagicMock(), response=MagicMock()
        )
        mock_httpx_client.return_value.__aenter__.return_value.get.return_value = mock_response
        
        with patch('app.services.github_service.settings') as mock_settings:
            mock_settings.github_mock = False
            mock_settings.github_token = "invalid-token"
            mock_settings.github_api_url = "https://api.github.com"
            mock_settings.github_user_agent = "test-agent"
            mock_settings.http_timeout = 30
            
            with pytest.raises(Exception):
                await get_repos()

    def test_github_service_imports(self):
        """Test that all GitHub service functions can be imported."""
        from app.services.github_service import (
            get_repos, get_branches, create_branch, create_issue,
            create_pull_request, get_pull_requests, merge_pull_request,
            close_pull_request, get_pull_request_files
        )
        
        assert callable(get_repos)
        assert callable(get_branches)
        assert callable(create_branch)
        assert callable(create_issue)
        assert callable(create_pull_request)
        assert callable(get_pull_requests)
        assert callable(merge_pull_request)
        assert callable(close_pull_request)
        assert callable(get_pull_request_files)

    @pytest.mark.asyncio
    async def test_github_service_pagination(self, mock_httpx_client):
        """Test pagination in get_repos."""
        # First page
        mock_response_1 = AsyncMock()
        mock_response_1.json.return_value = [{"name": "repo1", "full_name": "user/repo1", "private": False, "html_url": "http://example.com"}]
        mock_response_1.raise_for_status.return_value = None
        
        # Second page (empty)
        mock_response_2 = AsyncMock()
        mock_response_2.json.return_value = []
        mock_response_2.raise_for_status.return_value = None
        
        mock_httpx_client.return_value.__aenter__.return_value.get.side_effect = [mock_response_1, mock_response_2]
        
        with patch('app.services.github_service.settings') as mock_settings:
            mock_settings.github_mock = False
            mock_settings.github_token = "real-token"
            mock_settings.github_api_url = "https://api.github.com"
            mock_settings.github_user_agent = "test-agent"
            mock_settings.http_timeout = 30
            
            result = await get_repos()
            
            assert len(result) == 1
            assert result[0].name == "repo1"
