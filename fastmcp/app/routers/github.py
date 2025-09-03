
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from ..services import github_service
from ..models.github_models import CommitInfo

router = APIRouter()

@router.get("/commits/{owner}/{repo}", response_model=List[CommitInfo])
async def get_commits(
    owner: str,
    repo: str,
    branch: Optional[str] = None,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
    limit: int = Query(10, ge=1, le=100)
):
    try:
        return await github_service.get_commit_history(owner, repo, branch, since, until, limit)
    except HTTPException as e:
        raise e
