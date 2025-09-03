
import httpx
from fastapi import HTTPException
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

from ..config.settings import settings
from ..models.github_models import CommitInfo

GITHUB_API_BASE = "https://api.github.com"

async def get_default_branch(owner: str, repo: str, client: httpx.AsyncClient) -> str:
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
    try:
        resp = await client.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("default_branch", "main")
    except httpx.RequestError:
        return "main"  # fallback

async def get_commit_history(
    owner: str,
    repo: str,
    branch: Optional[str] = None,
    since: Optional[Union[str, datetime]] = None,
    until: Optional[Union[str, datetime]] = None,
    limit: int = 10
) -> List[CommitInfo]:
    if not owner or not repo:
        raise HTTPException(status_code=400, detail="Owner and repo are required")
        
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 100")

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {settings.github_token}"
    }

    async with httpx.AsyncClient(headers=headers) as client:
        if not branch:
            branch = await get_default_branch(owner, repo, client)
        
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
            response = await client.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            commits = response.json()
            result = []
            
            for commit in commits[:limit]:
                commit_data = commit.get("commit", {})
                author_data = commit_data.get("author", {})
                
                result.append(CommitInfo(
                    sha=commit.get("sha"),
                    message=commit_data.get("message", "").split("\n")[0],
                    author={
                        "name": author_data.get("name", ""),
                        "email": author_data.get("email", ""),
                        "date": author_data.get("date", "")
                    },
                    url=commit.get("html_url", ""),
                    commit_url=commit_data.get("url", ""),
                    verification=commit_data.get("verification", {}).get("verified", False)
                ))
                
            return result
            
        except httpx.RequestError as e:
            error_msg = f"Failed to fetch commit history: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f" (Status: {e.response.status_code})"
                if e.response.status_code == 404:
                    error_msg = f"Repository {owner}/{repo} not found or access denied"
            raise HTTPException(status_code=500, detail=error_msg)
