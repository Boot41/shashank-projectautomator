import os
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import requests
from fastapi import HTTPException
from requests.adapters import HTTPAdapter, Retry
from pydantic import BaseModel

# ---------------------------------------------------
# 🔹 Setup logging
# ---------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ---------------------------------------------------
# 🔹 GitHub API Setup
# ---------------------------------------------------
GITHUB_API_BASE = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    logging.warning("⚠️ GITHUB_TOKEN not set. You may hit rate limits.")

HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}" if GITHUB_TOKEN else None
}

# ---------------------------------------------------
# 🔹 Session with retries (handles timeouts, 5xx)
# ---------------------------------------------------
session = requests.Session()
retries = Retry(
    total=3,             # retry 3 times
    backoff_factor=1,    # wait 1s, 2s, 4s
    status_forcelist=[429, 500, 502, 503, 504]
)
session.mount("https://", HTTPAdapter(max_retries=retries))

# ---------------------------------------------------
# 🔹 Helper: Get default branch
# ---------------------------------------------------
def get_default_branch(owner: str, repo: str) -> str:
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
    logging.info(f"Fetching default branch for {owner}/{repo}")

    try:
        resp = session.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("default_branch", "main")
    except requests.RequestException as e:
        logging.error(f"Failed to fetch default branch: {e}")
        return "main"  # fallback

class CommitAuthor(BaseModel):
    name: str
    email: str
    date: str

class CommitInfo(BaseModel):
    sha: str
    message: str
    author: CommitAuthor
    url: str

# ---------------------------------------------------
# 🔹 GitHub Commands
# ---------------------------------------------------

def get_commit_history(
    owner: str,
    repo: str,
    branch: Optional[str] = None,
    since: Optional[Union[str, datetime]] = None,
    until: Optional[Union[str, datetime]] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Get commit history for a GitHub repository.
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        branch: Branch name (default: repository's default branch)
        since: Only show commits after this date (ISO 8601 format or datetime object)
        until: Only show commits before this date (ISO 8601 format or datetime object)
        limit: Maximum number of commits to return (1-100, default: 10)
        
    Returns:
        List of commit objects with details
    """
    if not owner or not repo:
        raise HTTPException(status_code=400, detail="Owner and repo are required")
        
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 100")
    
    # Get default branch if not specified
    if not branch:
        branch = get_default_branch(owner, repo)
    
    # Format dates if provided
    params = {"sha": branch, "per_page": min(limit, 100), "page": 1}
    
    if since:
        if isinstance(since, datetime):
            since = since.isoformat()
        params["since"] = since
        
    if until:
        if isinstance(until, datetime):
            until = until.isoformat()
        params["until"] = until
    
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/commits"
    
    try:
        response = session.get(url, headers=HEADERS, params=params, timeout=10)
        response.raise_for_status()
        
        commits = response.json()
        result = []
        
        for commit in commits[:limit]:
            commit_data = commit.get("commit", {})
            author_data = commit_data.get("author", {})
            
            result.append({
                "sha": commit.get("sha"),
                "message": commit_data.get("message", "").split("\n")[0],  # First line of commit message
                "author": {
                    "name": author_data.get("name", ""),
                    "email": author_data.get("email", ""),
                    "date": author_data.get("date", "")
                },
                "url": commit.get("html_url", ""),
                "commit_url": commit_data.get("url", ""),
                "verification": commit_data.get("verification", {}).get("verified", False)
            })
            
        return result
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Failed to fetch commit history: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            error_msg += f" (Status: {e.response.status_code})"
            if e.response.status_code == 404:
                error_msg = f"Repository {owner}/{repo} not found or access denied"
        logging.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

# ---------------------------------------------------
# 🔹 Fetch commits (legacy function)
# ---------------------------------------------------
def fetch_github_commits(
    owner: str,
    repo: str,
    branch: Optional[str] = None,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Fetch recent commits from a GitHub repo.

    Args:
        owner: Repository owner
        repo: Repository name
        branch: Branch to fetch (default: auto-detect)
        limit: Number of commits to return

    Returns:
        Dict with commits list
    """
    branch = branch or get_default_branch(owner, repo)
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/commits"
    params = {"sha": branch, "per_page": limit}

    logging.info(f"Fetching commits for {owner}/{repo} on branch {branch}")

    try:
        resp = session.get(url, headers=HEADERS, params=params, timeout=10)
        if resp.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Repo or branch not found: {owner}/{repo}@{branch}")

        resp.raise_for_status()
        commits = resp.json()

        parsed_commits: List[Dict[str, Any]] = []
        for c in commits:
            commit_data = c.get("commit", {})
            author = commit_data.get("author", {})
            parsed_commits.append({
                "sha": c.get("sha"),
                "message": commit_data.get("message", "").split("\n")[0],
                "author": author.get("name", "Unknown"),
                "date": author.get("date", ""),
                "url": c.get("html_url", "")
            })

        return {"status": "success", "branch": branch, "commits": parsed_commits}

    except requests.RequestException as e:
        logging.error(f"GitHub API error: {e}")
        raise HTTPException(status_code=502, detail=f"GitHub API error: {e}")
