import httpx
from fastapi import HTTPException
from typing import List, Dict, Any

from ..config.settings import settings
from ..models.github_models import (
    GithubRepo, GithubBranch, CreatePullRequest, PullRequest, 
    GithubIssue, CreateGithubIssue
)
from ..tools import tool

# Common headers for GitHub API
def _get_github_headers():
    return {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {settings.github_token}",
        "User-Agent": settings.github_user_agent,
    }

@tool(name="github_get_repos")
async def get_repos() -> List[GithubRepo]:
    """Gets a list of repositories for the authenticated user."""
    if settings.github_mock:
        return [
            GithubRepo(name="test-repo", full_name="user/test-repo", private=False, html_url="http://example.com")
        ]

    url = f"{settings.github_api_url}/user/repos"
    headers = _get_github_headers()

    async with httpx.AsyncClient() as client:
        try:
            repos: List[GithubRepo] = []
            page = 1
            per_page = 100
            while True:
                params = {"per_page": per_page, "page": page}
                response = await client.get(url, headers=headers, params=params, timeout=settings.http_timeout)
                response.raise_for_status()
                data = response.json()
                if not data:
                    break
                repos.extend([GithubRepo(**repo) for repo in data])
                page += 1
            return repos
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"GitHub API error: {e}")

@tool(name="github_get_branches")
async def get_branches(owner: str, repo: str) -> List[GithubBranch]:
    """Gets a list of all branches for a specific repository."""
    if settings.github_mock:
        return [GithubBranch(name="main", commit_sha="abc"), GithubBranch(name="dev", commit_sha="def")]

    url = f"{settings.github_api_url}/repos/{owner}/{repo}/branches"
    headers = _get_github_headers()
    all_branches = []
    page = 1
    per_page = 100  # Max per page

    async with httpx.AsyncClient() as client:
        while True:
            try:
                params = {"per_page": per_page, "page": page}
                response = await client.get(url, headers=headers, params=params, timeout=settings.http_timeout)
                response.raise_for_status()
                branches_on_page = response.json()

                if not branches_on_page:
                    break  # No more branches

                all_branches.extend([
                    GithubBranch(name=branch['name'], commit_sha=branch['commit']['sha'])
                    for branch in branches_on_page
                ])
                page += 1

            except httpx.RequestError as e:
                raise HTTPException(status_code=502, detail=f"GitHub API error: {e}")
    return all_branches

@tool(name="github_create_branch")
async def create_branch(owner: str, repo: str, branch_name: str, source_branch: str = "main") -> GithubBranch:
    """Creates a new branch in a repository from a source branch."""
    if settings.github_mock:
        return GithubBranch(name=branch_name, commit_sha="xyz")

    headers = _get_github_headers()
    async with httpx.AsyncClient() as client:
        try:
            # 1. Get the SHA of the source branch
            source_branch_url = f"{settings.github_api_url}/repos/{owner}/{repo}/git/refs/heads/{source_branch}"
            response = await client.get(source_branch_url, headers=headers, timeout=settings.http_timeout)
            response.raise_for_status()
            source_sha = response.json()["object"]["sha"]

            # 2. Create the new branch
            create_branch_url = f"{settings.github_api_url}/repos/{owner}/{repo}/git/refs"
            payload = {
                "ref": f"refs/heads/{branch_name}",
                "sha": source_sha
            }
            response = await client.post(create_branch_url, headers=headers, json=payload, timeout=settings.http_timeout)
            response.raise_for_status()
            
            new_branch_data = response.json()
            return GithubBranch(name=branch_name, commit_sha=new_branch_data["object"]["sha"])

        except httpx.HTTPStatusError as e:
            # Surface GitHub's error message and status code (commonly 403 for insufficient scopes)
            message = None
            try:
                message = e.response.json().get("message")
            except Exception:
                message = e.response.text
            raise HTTPException(status_code=e.response.status_code, detail=f"GitHub error: {message}")
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"GitHub API error: {e}")

@tool(name="github_create_pull_request")
async def create_pull_request(owner: str, repo: str, pr_data: CreatePullRequest) -> PullRequest:
    """Creates a new pull request."""
    if settings.github_mock:
        return PullRequest(id=1, number=1, title=pr_data.title, state="open", html_url="http://example.com/pr/1")

    url = f"{settings.github_api_url}/repos/{owner}/{repo}/pulls"
    headers = _get_github_headers()
    payload = pr_data.dict()

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=payload, timeout=settings.http_timeout)
            response.raise_for_status()
            return PullRequest(**response.json())
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"GitHub API error: {e}")

@tool(name="github_merge_pull_request")
async def merge_pull_request(owner: str, repo: str, pr_number: int, commit_title: str = None, commit_message: str = None, merge_method: str = "merge") -> Dict[str, Any]:
    """Merges a pull request with optional commit message and merge method."""
    if settings.github_mock:
        return {
            "merged": True, 
            "message": "Pull Request successfully merged",
            "commit_sha": "abc123def456",
            "merge_method": merge_method,
            "commit_title": commit_title or f"Merge PR #{pr_number}",
            "commit_message": commit_message or f"Merge pull request #{pr_number}"
        }

    # If no commit title/message provided, try to get them from the PR
    if not commit_title or not commit_message:
        try:
            pr_url = f"{settings.github_api_url}/repos/{owner}/{repo}/pulls/{pr_number}"
            async with httpx.AsyncClient() as client:
                pr_response = await client.get(pr_url, headers=_get_github_headers(), timeout=settings.http_timeout)
                pr_response.raise_for_status()
                pr_data = pr_response.json()
                
                if not commit_title:
                    commit_title = f"Merge PR #{pr_number}: {pr_data.get('title', '')}"
                if not commit_message:
                    commit_message = pr_data.get('body', f"Merge pull request #{pr_number}")
        except:
            # Fallback if we can't fetch PR details
            if not commit_title:
                commit_title = f"Merge PR #{pr_number}"
            if not commit_message:
                commit_message = f"Merge pull request #{pr_number}"

    url = f"{settings.github_api_url}/repos/{owner}/{repo}/pulls/{pr_number}/merge"
    headers = _get_github_headers()
    
    # Prepare merge data
    merge_data = {
        "merge_method": merge_method  # merge, squash, or rebase
    }
    
    if commit_title:
        merge_data["commit_title"] = commit_title
    if commit_message:
        merge_data["commit_message"] = commit_message

    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(url, headers=headers, json=merge_data, timeout=settings.http_timeout)
            response.raise_for_status()
            result = response.json()
            result["commit_title"] = commit_title
            result["commit_message"] = commit_message
            return result
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"GitHub API error: {e}")

@tool(name="github_close_pull_request")
async def close_pull_request(owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
    """Closes a pull request without merging."""
    if settings.github_mock:
        return {"closed": True, "message": "Pull Request successfully closed"}

    url = f"{settings.github_api_url}/repos/{owner}/{repo}/pulls/{pr_number}"
    headers = _get_github_headers()
    data = {"state": "closed"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.patch(url, headers=headers, json=data, timeout=settings.http_timeout)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"GitHub API error: {e}")

@tool(name="github_get_pr_files")
async def get_pull_request_files(owner: str, repo: str, pr_number: int) -> List[Dict[str, Any]]:
    """Gets the list of files changed in a pull request."""
    if settings.github_mock:
        return [
            {
                "filename": "src/main.py",
                "status": "modified",
                "additions": 10,
                "deletions": 5,
                "changes": 15,
                "patch": "@@ -1,3 +1,8 @@\n def main():\n-    print('Hello')\n+    print('Hello World')\n+    print('New feature')\n"
            },
            {
                "filename": "README.md",
                "status": "added",
                "additions": 20,
                "deletions": 0,
                "changes": 20,
                "patch": "@@ -0,0 +1,20 @@\n+# Project Documentation\n+This is a new README file.\n"
            }
        ]

    url = f"{settings.github_api_url}/repos/{owner}/{repo}/pulls/{pr_number}/files"
    headers = _get_github_headers()

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=settings.http_timeout)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"GitHub API error: {e}")

@tool(name="github_get_issues")
async def get_issues(owner: str, repo: str) -> List[GithubIssue]:
    """Gets a list of issues for a repository."""
    if settings.github_mock:
        return [GithubIssue(id=1, number=1, title="Test Issue", state="open", html_url="http://example.com/issue/1")]

    url = f"{settings.github_api_url}/repos/{owner}/{repo}/issues"
    headers = _get_github_headers()

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=settings.http_timeout)
            response.raise_for_status()
            raw = response.json()
            # Filter out PRs (issues API includes PRs when 'pull_request' key exists)
            only_issues = [issue for issue in raw if "pull_request" not in issue]
            return [GithubIssue(**issue) for issue in only_issues]
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"GitHub API error: {e}")

@tool(name="github_get_pull_requests")
async def get_pull_requests(owner: str, repo: str, state: str = "open") -> List[PullRequest]:
    """Gets a list of pull requests for a repository."""
    if settings.github_mock:
        return [
            PullRequest(
                id=1, 
                number=1, 
                title="Test PR", 
                state=state, 
                html_url="http://example.com/pull/1",
                head={"ref": "feature-branch"},
                base={"ref": "main"}
            )
        ]

    url = f"{settings.github_api_url}/repos/{owner}/{repo}/pulls"
    headers = _get_github_headers()
    params = {"state": state}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params, timeout=settings.http_timeout)
            response.raise_for_status()
            raw = response.json()
            return [PullRequest(**pr) for pr in raw]
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"GitHub API error: {e}")

@tool(name="github_create_issue")
async def create_issue(owner: str, repo: str, issue_data: CreateGithubIssue) -> GithubIssue:
    """Creates a new issue in a repository."""
    if settings.github_mock:
        return GithubIssue(id=2, number=2, title=issue_data.title, state="open", html_url="http://example.com/issue/2")

    url = f"{settings.github_api_url}/repos/{owner}/{repo}/issues"
    headers = _get_github_headers()
    payload = issue_data.dict()

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=payload, timeout=settings.http_timeout)
            response.raise_for_status()
            return GithubIssue(**response.json())
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"GitHub API error: {e}")

@tool(name="github_comment_issue")
async def comment_issue(owner: str, repo: str, issue_number: int, comment_body: str) -> Dict[str, Any]:
    """Adds a comment to a GitHub issue."""
    if settings.github_mock:
        return {"id": 123, "body": comment_body}

    url = f"{settings.github_api_url}/repos/{owner}/{repo}/issues/{issue_number}/comments"
    headers = _get_github_headers()
    payload = {"body": comment_body}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=payload, timeout=settings.http_timeout)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"GitHub API error: {e}")