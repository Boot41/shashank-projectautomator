from google.ai.generativelanguage import Tool, FunctionDeclaration, Schema
from ..services import github_service
from ..services.email_service import send_email

# --- List repositories ---
github_get_repos_tool = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="github_get_repos",
            description="List repositories for the authenticated user",
            parameters=Schema(
                type=Schema.Type.OBJECT,
                properties={},
                required=[],
            ),
        )
    ]
)

async def run_github_get_repos():
    return await github_service.get_repos()

# --- List branches ---
github_get_branches_tool = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="github_get_branches",
            description="List branches for a repository",
            parameters=Schema(
                type=Schema.Type.OBJECT,
                properties={
                    "owner": Schema(type=Schema.Type.STRING, description="Repository owner"),
                    "repo": Schema(type=Schema.Type.STRING, description="Repository name"),
                },
                required=["owner", "repo"],
            ),
        )
    ]
)

async def run_github_get_branches(owner: str, repo: str):
    return await github_service.get_branches(owner, repo)

# --- Create branch ---
github_create_branch_tool = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="github_create_branch",
            description="Create a new branch from a source branch",
            parameters=Schema(
                type=Schema.Type.OBJECT,
                properties={
                    "owner": Schema(type=Schema.Type.STRING, description="Repository owner"),
                    "repo": Schema(type=Schema.Type.STRING, description="Repository name"),
                    "branch_name": Schema(type=Schema.Type.STRING, description="New branch name"),
                    "source_branch": Schema(type=Schema.Type.STRING, description="Source branch name (default main)"),
                },
                required=["owner", "repo", "branch_name"],
            ),
        )
    ]
)

async def run_github_create_branch(owner: str, repo: str, branch_name: str, source_branch: str = "main"):
    return await github_service.create_branch(owner, repo, branch_name, source_branch)

# --- Create pull request ---
github_create_pull_request_tool = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="github_create_pull_request",
            description="Create a pull request",
            parameters=Schema(
                type=Schema.Type.OBJECT,
                properties={
                    "owner": Schema(type=Schema.Type.STRING, description="Repository owner"),
                    "repo": Schema(type=Schema.Type.STRING, description="Repository name"),
                    "title": Schema(type=Schema.Type.STRING, description="PR title"),
                    "body": Schema(type=Schema.Type.STRING, description="PR description/body"),
                    "head": Schema(type=Schema.Type.STRING, description="Branch with changes"),
                    "base": Schema(type=Schema.Type.STRING, description="Target branch to merge into"),
                },
                required=["owner", "repo", "title", "head", "base"],
            ),
        )
    ]
)

async def run_github_create_pull_request(owner: str, repo: str, title: str, head: str, base: str, body: str = ""):
    from ..models.github_models import CreatePullRequest

    pr = CreatePullRequest(title=title, body=body, head=head, base=base)
    return await github_service.create_pull_request(owner, repo, pr)

# --- Merge pull request ---
github_merge_pull_request_tool = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="github_merge_pull_request",
            description="Merge a pull request by number",
            parameters=Schema(
                type=Schema.Type.OBJECT,
                properties={
                    "owner": Schema(type=Schema.Type.STRING, description="Repository owner"),
                    "repo": Schema(type=Schema.Type.STRING, description="Repository name"),
                    "pr_number": Schema(type=Schema.Type.INTEGER, description="Pull request number"),
                },
                required=["owner", "repo", "pr_number"],
            ),
        )
    ]
)

async def run_github_merge_pull_request(owner: str, repo: str, pr_number: int):
    return await github_service.merge_pull_request(owner, repo, pr_number)

# --- Close pull request ---
github_close_pull_request_tool = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="github_close_pull_request",
            description="Close a pull request without merging",
            parameters=Schema(
                type=Schema.Type.OBJECT,
                properties={
                    "owner": Schema(type=Schema.Type.STRING, description="Repository owner"),
                    "repo": Schema(type=Schema.Type.STRING, description="Repository name"),
                    "pr_number": Schema(type=Schema.Type.INTEGER, description="Pull request number"),
                },
                required=["owner", "repo", "pr_number"],
            ),
        )
    ]
)

async def run_github_close_pull_request(owner: str, repo: str, pr_number: int):
    return await github_service.close_pull_request(owner, repo, pr_number)

# --- List issues ---
github_get_issues_tool = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="github_get_issues",
            description="List issues for a repository",
            parameters=Schema(
                type=Schema.Type.OBJECT,
                properties={
                    "owner": Schema(type=Schema.Type.STRING, description="Repository owner"),
                    "repo": Schema(type=Schema.Type.STRING, description="Repository name"),
                },
                required=["owner", "repo"],
            ),
        )
    ]
)

async def run_github_get_issues(owner: str, repo: str):
    return await github_service.get_issues(owner, repo)

# --- Create issue ---
github_create_issue_tool = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="github_create_issue",
            description="Create a new issue in a repository",
            parameters=Schema(
                type=Schema.Type.OBJECT,
                properties={
                    "owner": Schema(type=Schema.Type.STRING, description="Repository owner"),
                    "repo": Schema(type=Schema.Type.STRING, description="Repository name"),
                    "title": Schema(type=Schema.Type.STRING, description="Issue title"),
                    "body": Schema(type=Schema.Type.STRING, description="Issue body/description"),
                },
                required=["owner", "repo", "title"],
            ),
        )
    ]
)

async def run_github_create_issue(owner: str, repo: str, title: str, body: str = ""):
    from ..models.github_models import CreateGithubIssue

    payload = CreateGithubIssue(title=title, body=body)
    return await github_service.create_issue(owner, repo, payload)

# --- Comment on issue ---
github_comment_issue_tool = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="github_comment_issue",
            description="Add a comment to a GitHub issue",
            parameters=Schema(
                type=Schema.Type.OBJECT,
                properties={
                    "owner": Schema(type=Schema.Type.STRING, description="Repository owner"),
                    "repo": Schema(type=Schema.Type.STRING, description="Repository name"),
                    "issue_number": Schema(type=Schema.Type.INTEGER, description="Issue number"),
                    "comment_body": Schema(type=Schema.Type.STRING, description="Comment text"),
                },
                required=["owner", "repo", "issue_number", "comment_body"],
            ),
        )
    ]
)

async def run_github_comment_issue(owner: str, repo: str, issue_number: int, comment_body: str):
    return await github_service.comment_issue(owner, repo, issue_number, comment_body)

# --- Send email (SMTP) ---
from google.generativeai import types as gen_types  # type: ignore

email_send_tool = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="email_send",
            description="Send an email via configured SMTP",
            parameters=Schema(
                type=Schema.Type.OBJECT,
                properties={
                    "to": Schema(type=Schema.Type.STRING, description="Recipient email address"),
                    "subject": Schema(type=Schema.Type.STRING, description="Email subject"),
                    "body": Schema(type=Schema.Type.STRING, description="Email body text"),
                },
                required=["to", "subject", "body"],
            ),
        )
    ]
)

async def run_email_send(to: str, subject: str, body: str):
    return await send_email(to_email=to, subject=subject, body=body)


