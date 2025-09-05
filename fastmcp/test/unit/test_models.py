"""
Comprehensive unit tests for Pydantic models.
"""
import pytest
from datetime import datetime
from app.models.github_models import (
    GithubRepo, GithubBranch, CreateGithubIssue, CreatePullRequest,
    PullRequest, GithubIssue
)
from app.models.jira_models import (
    JiraProject, JiraIssue, JiraIssueBasic, CreateJiraIssue, JiraSprint
)
from app.models.ai_models import ProcessedCommand, AIResponse


@pytest.mark.unit
class TestGitHubModels:
    """Test cases for GitHub models."""

    def test_github_repo_creation(self):
        """Test GithubRepo model creation."""
        repo_data = {
            "name": "test-repo",
            "full_name": "owner/test-repo",
            "private": False,
            "html_url": "https://github.com/owner/test-repo",
            "description": "Test repository"
        }
        
        repo = GithubRepo(**repo_data)
        
        assert repo.name == "test-repo"
        assert repo.full_name == "owner/test-repo"
        assert repo.private is False
        assert repo.html_url == "https://github.com/owner/test-repo"
        assert repo.description == "Test repository"

    def test_github_repo_optional_description(self):
        """Test GithubRepo with optional description."""
        repo_data = {
            "name": "test-repo",
            "full_name": "owner/test-repo",
            "private": False,
            "html_url": "https://github.com/owner/test-repo"
        }
        
        repo = GithubRepo(**repo_data)
        
        assert repo.name == "test-repo"
        assert repo.description is None

    def test_github_branch_creation(self):
        """Test GithubBranch model creation."""
        branch_data = {
            "name": "feature-branch",
            "commit_sha": "abc123def456"
        }
        
        branch = GithubBranch(**branch_data)
        
        assert branch.name == "feature-branch"
        assert branch.commit_sha == "abc123def456"

    def test_create_github_issue_creation(self):
        """Test CreateGithubIssue model creation."""
        issue_data = {
            "title": "Test Issue",
            "body": "Test description"
        }
        
        issue = CreateGithubIssue(**issue_data)
        
        assert issue.title == "Test Issue"
        assert issue.body == "Test description"

    def test_create_github_issue_optional_body(self):
        """Test CreateGithubIssue with optional body."""
        issue_data = {
            "title": "Test Issue"
        }
        
        issue = CreateGithubIssue(**issue_data)
        
        assert issue.title == "Test Issue"
        assert issue.body is None

    def test_create_pull_request_creation(self):
        """Test CreatePullRequest model creation."""
        pr_data = {
            "title": "Test PR",
            "body": "Test description",
            "head": "feature-branch",
            "base": "main"
        }
        
        pr = CreatePullRequest(**pr_data)
        
        assert pr.title == "Test PR"
        assert pr.body == "Test description"
        assert pr.head == "feature-branch"
        assert pr.base == "main"

    def test_pull_request_creation(self):
        """Test PullRequest model creation."""
        pr_data = {
            "id": 1,
            "number": 1,
            "title": "Test PR",
            "state": "open",
            "html_url": "https://github.com/owner/repo/pull/1"
        }
        
        pr = PullRequest(**pr_data)
        
        assert pr.id == 1
        assert pr.number == 1
        assert pr.title == "Test PR"
        assert pr.state == "open"
        assert pr.html_url == "https://github.com/owner/repo/pull/1"

    def test_github_issue_creation(self):
        """Test GithubIssue model creation."""
        issue_data = {
            "id": 1,
            "number": 1,
            "title": "Test Issue",
            "state": "open",
            "html_url": "https://github.com/owner/repo/issues/1",
            "body": "Test description"
        }
        
        issue = GithubIssue(**issue_data)
        
        assert issue.id == 1
        assert issue.number == 1
        assert issue.title == "Test Issue"
        assert issue.state == "open"
        assert issue.html_url == "https://github.com/owner/repo/issues/1"
        assert issue.body == "Test description"

    def test_github_issue_optional_body(self):
        """Test GithubIssue with optional body."""
        issue_data = {
            "id": 1,
            "number": 1,
            "title": "Test Issue",
            "state": "open",
            "html_url": "https://github.com/owner/repo/issues/1"
        }
        
        issue = GithubIssue(**issue_data)
        
        assert issue.title == "Test Issue"
        assert issue.body is None


@pytest.mark.unit
class TestJiraModels:
    """Test cases for Jira models."""

    def test_jira_project_creation(self):
        """Test JiraProject model creation."""
        project_data = {
            "id": "10000",
            "key": "TEST",
            "name": "Test Project",
            "projectTypeKey": "software"
        }
        
        project = JiraProject(**project_data)
        
        assert project.id == "10000"
        assert project.key == "TEST"
        assert project.name == "Test Project"
        assert project.projectTypeKey == "software"

    def test_jira_project_optional_type(self):
        """Test JiraProject with optional projectTypeKey."""
        project_data = {
            "id": "10000",
            "key": "TEST",
            "name": "Test Project"
        }
        
        project = JiraProject(**project_data)
        
        assert project.key == "TEST"
        assert project.projectTypeKey is None

    def test_jira_issue_creation(self):
        """Test JiraIssue model creation."""
        issue_data = {
            "ticket": "TEST-1",
            "title": "Test Issue",
            "status": "To Do",
            "assignee": "John Doe",
            "description": "Test description"
        }
        
        issue = JiraIssue(**issue_data)
        
        assert issue.ticket == "TEST-1"
        assert issue.title == "Test Issue"
        assert issue.status == "To Do"
        assert issue.assignee == "John Doe"
        assert issue.description == "Test description"

    def test_jira_issue_optional_description(self):
        """Test JiraIssue with optional description."""
        issue_data = {
            "ticket": "TEST-1",
            "title": "Test Issue",
            "status": "To Do",
            "assignee": "John Doe"
        }
        
        issue = JiraIssue(**issue_data)
        
        assert issue.ticket == "TEST-1"
        assert issue.description is None

    def test_jira_issue_basic_creation(self):
        """Test JiraIssueBasic model creation."""
        issue_data = {
            "key": "TEST-1",
            "summary": "Test Issue",
            "status": "To Do",
            "assignee": "John Doe",
            "priority": "High",
            "due_date": "2023-12-31",
            "reporter": "Jane Doe",
            "created": "2023-01-01T00:00:00.000+0000",
            "updated": "2023-01-02T00:00:00.000+0000"
        }
        
        issue = JiraIssueBasic(**issue_data)
        
        assert issue.key == "TEST-1"
        assert issue.summary == "Test Issue"
        assert issue.status == "To Do"
        assert issue.assignee == "John Doe"
        assert issue.priority == "High"
        assert issue.due_date == "2023-12-31"
        assert issue.reporter == "Jane Doe"
        assert issue.created == "2023-01-01T00:00:00.000+0000"
        assert issue.updated == "2023-01-02T00:00:00.000+0000"

    def test_jira_issue_basic_defaults(self):
        """Test JiraIssueBasic with default values."""
        issue_data = {
            "key": "TEST-1",
            "summary": "Test Issue"
        }
        
        issue = JiraIssueBasic(**issue_data)
        
        assert issue.key == "TEST-1"
        assert issue.summary == "Test Issue"
        assert issue.status is None
        assert issue.assignee == "Unassigned"
        assert issue.priority is None
        assert issue.due_date is None
        assert issue.reporter is None
        assert issue.created is None
        assert issue.updated is None

    def test_create_jira_issue_creation(self):
        """Test CreateJiraIssue model creation."""
        issue_data = {
            "project_key": "TEST",
            "summary": "Test Issue",
            "description": "Test description",
            "issuetype_name": "Task"
        }
        
        issue = CreateJiraIssue(**issue_data)
        
        assert issue.project_key == "TEST"
        assert issue.summary == "Test Issue"
        assert issue.description == "Test description"
        assert issue.issuetype_name == "Task"

    def test_create_jira_issue_default_type(self):
        """Test CreateJiraIssue with default issuetype_name."""
        issue_data = {
            "project_key": "TEST",
            "summary": "Test Issue",
            "description": "Test description"
        }
        
        issue = CreateJiraIssue(**issue_data)
        
        assert issue.project_key == "TEST"
        assert issue.issuetype_name == "Task"

    def test_jira_sprint_creation(self):
        """Test JiraSprint model creation."""
        sprint_data = {
            "id": 1,
            "name": "Sprint 1",
            "state": "active",
            "boardId": 100
        }
        
        sprint = JiraSprint(**sprint_data)
        
        assert sprint.id == 1
        assert sprint.name == "Sprint 1"
        assert sprint.state == "active"
        assert sprint.boardId == 100


@pytest.mark.unit
class TestAIModels:
    """Test cases for AI models."""

    def test_processed_command_creation(self):
        """Test ProcessedCommand model creation."""
        command_data = {
            "command": "create_issue",
            "parameters": {"title": "Test Issue", "description": "Test description"}
        }
        
        command = ProcessedCommand(**command_data)
        
        assert command.command == "create_issue"
        assert command.parameters["title"] == "Test Issue"
        assert command.parameters["description"] == "Test description"

    def test_processed_command_empty_parameters(self):
        """Test ProcessedCommand with empty parameters."""
        command_data = {
            "command": "list_repos",
            "parameters": {}
        }
        
        command = ProcessedCommand(**command_data)
        
        assert command.command == "list_repos"
        assert command.parameters == {}

    def test_ai_response_creation(self):
        """Test AIResponse model creation."""
        response_data = {
            "response": "I'll help you with that"
        }
        
        response = AIResponse(**response_data)
        
        assert response.response == "I'll help you with that"

    def test_ai_response_empty_response(self):
        """Test AIResponse with empty response."""
        response_data = {
            "response": ""
        }
        
        response = AIResponse(**response_data)
        
        assert response.response == ""


@pytest.mark.unit
class TestModelValidation:
    """Test cases for model validation."""

    def test_github_repo_validation(self):
        """Test GithubRepo validation with invalid data."""
        with pytest.raises(ValueError):
            GithubRepo(
                name="",  # Empty name should fail
                full_name="owner/repo",
                private=False,
                html_url="https://github.com/owner/repo"
            )

    def test_jira_issue_validation(self):
        """Test JiraIssue validation with invalid data."""
        with pytest.raises(ValueError):
            JiraIssue(
                ticket="",  # Empty ticket should fail
                title="Test Issue",
                status="To Do",
                assignee="John Doe"
            )

    def test_model_serialization(self):
        """Test model serialization to dict."""
        repo = GithubRepo(
            name="test-repo",
            full_name="owner/test-repo",
            private=False,
            html_url="https://github.com/owner/test-repo"
        )
        
        repo_dict = repo.dict()
        
        assert isinstance(repo_dict, dict)
        assert repo_dict["name"] == "test-repo"
        assert repo_dict["full_name"] == "owner/test-repo"

    def test_model_json_serialization(self):
        """Test model JSON serialization."""
        issue = JiraIssue(
            ticket="TEST-1",
            title="Test Issue",
            status="To Do",
            assignee="John Doe"
        )
        
        issue_json = issue.json()
        
        assert isinstance(issue_json, str)
        assert "TEST-1" in issue_json
        assert "Test Issue" in issue_json

    def test_model_from_dict(self):
        """Test creating model from dictionary."""
        data = {
            "name": "test-repo",
            "full_name": "owner/test-repo",
            "private": False,
            "html_url": "https://github.com/owner/test-repo"
        }
        
        repo = GithubRepo(**data)
        
        assert repo.name == "test-repo"
        assert repo.full_name == "owner/test-repo"
