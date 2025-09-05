"""
Comprehensive unit tests for tool runners.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.adk_tools.runners import (
    run_github_get_repos, run_github_create_branch, run_github_create_issue,
    run_github_create_pull_request, run_github_get_pull_requests,
    run_github_merge_pull_request, run_github_close_pull_request,
    run_github_get_pr_files, run_jira_get_projects, run_jira_get_issues_for_project,
    run_jira_create_issue, run_jira_fetch_issue, run_jira_get_issue_comments,
    run_jira_comment_issue, run_jira_get_possible_transitions, run_jira_transition_issue,
    run_jira_summarize_and_email_issue, run_email_send, run_email_confirm_and_send,
    run_regenerate_email_summary
)


@pytest.mark.unit
class TestGitHubToolRunners:
    """Test cases for GitHub tool runners."""

    @pytest.mark.asyncio
    async def test_run_github_get_repos_success(self):
        """Test successful GitHub repos retrieval."""
        mock_repos = [{"name": "test-repo", "full_name": "owner/test-repo"}]
        
        with patch('app.adk_tools.runners.github_service.get_repos', return_value=mock_repos):
            result = await run_github_get_repos("testuser")
            
            assert result == mock_repos

    @pytest.mark.asyncio
    async def test_run_github_get_repos_error(self):
        """Test GitHub repos retrieval with error."""
        with patch('app.adk_tools.runners.github_service.get_repos', side_effect=Exception("API Error")):
            result = await run_github_get_repos("testuser")
            
            assert "error" in result

    @pytest.mark.asyncio
    async def test_run_github_create_branch_success(self):
        """Test successful GitHub branch creation."""
        mock_branch = {"ref": "refs/heads/feature-branch", "object": {"sha": "abc123"}}
        
        with patch('app.adk_tools.runners.github_service.create_branch', return_value=mock_branch):
            result = await run_github_create_branch("owner", "repo", "feature-branch", "main")
            
            assert result == mock_branch

    @pytest.mark.asyncio
    async def test_run_github_create_issue_success(self):
        """Test successful GitHub issue creation."""
        mock_issue = {"number": 1, "title": "Test Issue", "state": "open"}
        
        with patch('app.adk_tools.runners.github_service.create_issue', return_value=mock_issue):
            result = await run_github_create_issue("owner", "repo", "Test Issue", "Test description")
            
            assert result == mock_issue

    @pytest.mark.asyncio
    async def test_run_github_create_pull_request_success(self):
        """Test successful GitHub pull request creation."""
        mock_pr = {"number": 1, "title": "Test PR", "state": "open"}
        
        with patch('app.adk_tools.runners.github_service.create_pull_request', return_value=mock_pr):
            result = await run_github_create_pull_request("owner", "repo", "Test PR", "Test description", "feature-branch", "main")
            
            assert result == mock_pr

    @pytest.mark.asyncio
    async def test_run_github_get_pull_requests_success(self):
        """Test successful GitHub pull requests retrieval."""
        mock_prs = [{"number": 1, "title": "Test PR", "state": "open"}]
        
        with patch('app.adk_tools.runners.github_service.get_pull_requests', return_value=mock_prs):
            result = await run_github_get_pull_requests("owner", "repo", "open")
            
            assert result == mock_prs

    @pytest.mark.asyncio
    async def test_run_github_merge_pull_request_success(self):
        """Test successful GitHub pull request merge."""
        mock_merge = {"merged": True, "message": "Pull Request successfully merged", "sha": "abc123"}
        
        with patch('app.adk_tools.runners.github_service.merge_pull_request', return_value=mock_merge):
            result = await run_github_merge_pull_request("owner", "repo", 1, "Merge commit", "Merge message", "merge")
            
            assert result == mock_merge

    @pytest.mark.asyncio
    async def test_run_github_close_pull_request_success(self):
        """Test successful GitHub pull request closure."""
        mock_close = {"number": 1, "title": "Test PR", "state": "closed"}
        
        with patch('app.adk_tools.runners.github_service.close_pull_request', return_value=mock_close):
            result = await run_github_close_pull_request("owner", "repo", 1)
            
            assert result == mock_close

    @pytest.mark.asyncio
    async def test_run_github_get_pr_files_success(self):
        """Test successful GitHub pull request files retrieval."""
        mock_files = [{"filename": "test.py", "status": "modified", "additions": 10, "deletions": 5}]
        
        with patch('app.adk_tools.runners.github_service.get_pull_request_files', return_value=mock_files):
            result = await run_github_get_pr_files("owner", "repo", 1)
            
            assert result == mock_files


@pytest.mark.unit
class TestJiraToolRunners:
    """Test cases for Jira tool runners."""

    @pytest.mark.asyncio
    async def test_run_jira_get_projects_success(self):
        """Test successful Jira projects retrieval."""
        mock_projects = [{"key": "TEST", "name": "Test Project"}]
        
        with patch('app.adk_tools.runners.jira_service.get_jira_projects', return_value=mock_projects):
            result = await run_jira_get_projects()
            
            assert result == mock_projects

    @pytest.mark.asyncio
    async def test_run_jira_get_issues_for_project_success(self):
        """Test successful Jira issues retrieval for project."""
        mock_issues = [{"ticket": "TEST-1", "title": "Test Issue", "status": "To Do"}]
        
        with patch('app.adk_tools.runners.jira_service.get_issues_for_project', return_value=mock_issues):
            result = await run_jira_get_issues_for_project("TEST")
            
            assert result == mock_issues

    @pytest.mark.asyncio
    async def test_run_jira_create_issue_success(self):
        """Test successful Jira issue creation."""
        mock_issue = {"id": "10001", "key": "TEST-1"}
        
        with patch('app.adk_tools.runners.jira_service.create_issue', return_value=mock_issue):
            result = await run_jira_create_issue("TEST", "Test Issue", "Test description")
            
            assert result == mock_issue

    @pytest.mark.asyncio
    async def test_run_jira_fetch_issue_success(self):
        """Test successful Jira issue fetching."""
        mock_issue = {"ticket": "TEST-1", "title": "Test Issue", "status": "In Progress"}
        
        with patch('app.adk_tools.runners.jira_service.fetch_jira_issue', return_value=mock_issue):
            result = await run_jira_fetch_issue("TEST-1")
            
            assert result == mock_issue

    @pytest.mark.asyncio
    async def test_run_jira_get_issue_comments_success(self):
        """Test successful Jira issue comments retrieval."""
        mock_comments = [{"comment": "Test comment", "author": "John Doe"}]
        
        with patch('app.adk_tools.runners.jira_service.get_issue_comments', return_value=mock_comments):
            result = await run_jira_get_issue_comments("TEST-1")
            
            assert result == mock_comments

    @pytest.mark.asyncio
    async def test_run_jira_comment_issue_success(self):
        """Test successful Jira issue commenting."""
        mock_comment = {"id": "10001", "body": "Test comment"}
        
        with patch('app.adk_tools.runners.jira_service.comment_issue', return_value=mock_comment):
            result = await run_jira_comment_issue("TEST-1", "Test comment")
            
            assert result == mock_comment

    @pytest.mark.asyncio
    async def test_run_jira_get_possible_transitions_success(self):
        """Test successful Jira transitions retrieval."""
        mock_transitions = [{"id": "11", "name": "To Do"}, {"id": "21", "name": "In Progress"}]
        
        with patch('app.adk_tools.runners.jira_service.get_possible_transitions', return_value=mock_transitions):
            result = await run_jira_get_possible_transitions("TEST-1")
            
            assert result == mock_transitions

    @pytest.mark.asyncio
    async def test_run_jira_transition_issue_success(self):
        """Test successful Jira issue transition."""
        mock_transition = {"status": "success", "message": "Issue transitioned successfully", "transition_id": "21"}
        
        with patch('app.adk_tools.runners.jira_service.transition_issue', return_value=mock_transition):
            result = await run_jira_transition_issue("TEST-1", "21")
            
            assert result == mock_transition

    @pytest.mark.asyncio
    async def test_run_jira_summarize_and_email_issue_success(self):
        """Test successful Jira issue summarization and email."""
        mock_issue = {"ticket": "TEST-1", "title": "Test Issue", "description": "Test description"}
        
        with patch('app.adk_tools.runners.jira_service.fetch_jira_issue', return_value=mock_issue):
            with patch('app.adk_tools.runners.ai_service.generate_model_summary', return_value="Generated summary"):
                result = await run_jira_summarize_and_email_issue("TEST-1", "test@example.com", "Additional context")
                
                assert "email_preview" in result
                assert result["email_preview"]["to"] == "test@example.com"
                assert result["email_preview"]["subject"] == "Jira Issue Summary: TEST-1 - Test Issue"


@pytest.mark.unit
class TestEmailToolRunners:
    """Test cases for Email tool runners."""

    @pytest.mark.asyncio
    async def test_run_email_send_success(self):
        """Test successful email sending."""
        mock_result = {"status": "sent", "message": "Email sent successfully"}
        
        with patch('app.adk_tools.runners.email_service.send_email', return_value=mock_result):
            result = await run_email_send("test@example.com", "Test Subject", "Test Body")
            
            assert result == mock_result

    @pytest.mark.asyncio
    async def test_run_email_confirm_and_send_success(self):
        """Test successful email confirmation and sending."""
        result = await run_email_confirm_and_send("test@example.com", "Test Subject", "Test Body", "PR created")
        
        assert "email_preview" in result
        assert result["email_preview"]["to"] == "test@example.com"
        assert result["email_preview"]["subject"] == "Test Subject"
        assert result["email_preview"]["body"] == "Test Body"

    @pytest.mark.asyncio
    async def test_run_regenerate_email_summary_success(self):
        """Test successful email summary regeneration."""
        mock_summary = "Regenerated email summary"
        
        with patch('app.adk_tools.runners.ai_service.generate_model_summary', return_value=mock_summary):
            result = await run_regenerate_email_summary(
                "Initial summary",
                "User feedback",
                "Key points",
                {"title": "Test PR"},
                "test@example.com"
            )
            
            assert "email_preview" in result
            assert result["email_preview"]["to"] == "test@example.com"
            assert result["email_preview"]["body"] == mock_summary


@pytest.mark.unit
class TestToolRunnersIntegration:
    """Integration tests for tool runners."""

    @pytest.mark.asyncio
    async def test_tool_runners_with_mock_settings(self):
        """Test tool runners with mock settings enabled."""
        with patch('app.adk_tools.runners.settings') as mock_settings:
            mock_settings.github_mock = True
            mock_settings.jira_mock = True
            
            # Test GitHub tool runners with mock
            result = await run_github_get_repos("testuser")
            assert isinstance(result, list)
            
            result = await run_github_create_branch("owner", "repo", "branch", "main")
            assert "ref" in result
            
            result = await run_github_create_issue("owner", "repo", "title", "body")
            assert "number" in result
            
            result = await run_github_create_pull_request("owner", "repo", "title", "body", "head", "base")
            assert "number" in result
            
            result = await run_github_get_pull_requests("owner", "repo", "open")
            assert isinstance(result, list)
            
            result = await run_github_merge_pull_request("owner", "repo", 1)
            assert "merged" in result
            
            result = await run_github_close_pull_request("owner", "repo", 1)
            assert "number" in result
            
            result = await run_github_get_pr_files("owner", "repo", 1)
            assert isinstance(result, list)
            
            # Test Jira tool runners with mock
            result = await run_jira_get_projects()
            assert isinstance(result, list)
            
            result = await run_jira_get_issues_for_project("TEST")
            assert isinstance(result, list)
            
            result = await run_jira_create_issue("TEST", "title", "description")
            assert "id" in result
            
            result = await run_jira_fetch_issue("TEST-1")
            assert hasattr(result, 'ticket')
            
            result = await run_jira_get_issue_comments("TEST-1")
            assert isinstance(result, list)
            
            result = await run_jira_comment_issue("TEST-1", "comment")
            assert "id" in result
            
            result = await run_jira_get_possible_transitions("TEST-1")
            assert isinstance(result, list)
            
            result = await run_jira_transition_issue("TEST-1", "21")
            assert "status" in result

    @pytest.mark.asyncio
    async def test_tool_runners_parameter_validation(self):
        """Test tool runners parameter validation."""
        # Test with missing parameters
        result = await run_github_get_repos("")
        assert "error" in result or result == []
        
        result = await run_github_create_branch("", "repo", "branch", "main")
        assert "error" in result
        
        result = await run_jira_get_issues_for_project("")
        assert "error" in result or result == []
        
        result = await run_jira_create_issue("", "title", "description")
        assert "error" in result
        
        result = await run_email_send("", "subject", "body")
        assert "error" in result

    @pytest.mark.asyncio
    async def test_tool_runners_async_behavior(self):
        """Test tool runners async behavior."""
        import asyncio
        
        async def mock_async_call():
            await asyncio.sleep(0.1)  # Simulate async delay
            return {"result": "async response"}
        
        with patch('app.adk_tools.runners.github_service.get_repos', side_effect=mock_async_call):
            result = await run_github_get_repos("testuser")
            assert result["result"] == "async response"
        
        with patch('app.adk_tools.runners.jira_service.get_jira_projects', side_effect=mock_async_call):
            result = await run_jira_get_projects()
            assert result["result"] == "async response"

    def test_tool_runners_imports(self):
        """Test that all tool runner functions can be imported."""
        from app.adk_tools.runners import (
            run_github_get_repos, run_github_create_branch, run_github_create_issue,
            run_github_create_pull_request, run_github_get_pull_requests,
            run_github_merge_pull_request, run_github_close_pull_request,
            run_github_get_pr_files, run_jira_get_projects, run_jira_get_issues_for_project,
            run_jira_create_issue, run_jira_fetch_issue, run_jira_get_issue_comments,
            run_jira_comment_issue, run_jira_get_possible_transitions, run_jira_transition_issue,
            run_jira_summarize_and_email_issue, run_email_send, run_email_confirm_and_send,
            run_regenerate_email_summary
        )
        
        # All imports should work
        assert callable(run_github_get_repos)
        assert callable(run_github_create_branch)
        assert callable(run_github_create_issue)
        assert callable(run_github_create_pull_request)
        assert callable(run_github_get_pull_requests)
        assert callable(run_github_merge_pull_request)
        assert callable(run_github_close_pull_request)
        assert callable(run_github_get_pr_files)
        assert callable(run_jira_get_projects)
        assert callable(run_jira_get_issues_for_project)
        assert callable(run_jira_create_issue)
        assert callable(run_jira_fetch_issue)
        assert callable(run_jira_get_issue_comments)
        assert callable(run_jira_comment_issue)
        assert callable(run_jira_get_possible_transitions)
        assert callable(run_jira_transition_issue)
        assert callable(run_jira_summarize_and_email_issue)
        assert callable(run_email_send)
        assert callable(run_email_confirm_and_send)
        assert callable(run_regenerate_email_summary)
