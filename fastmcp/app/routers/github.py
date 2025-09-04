
from fastapi import APIRouter, HTTPException, Body, status
from typing import List, Dict, Any

from ..services import github_service
from ..models.github_models import (
    GithubRepo, GithubBranch, CreatePullRequest, PullRequest, 
    GithubIssue, CreateGithubIssue
)

router = APIRouter()

@router.get("/repos", response_model=List[GithubRepo])
async def get_repos():
    try:
        return await github_service.get_repos()
    except HTTPException as e:
        raise e

@router.get("/{owner}/{repo}/branches", response_model=List[GithubBranch])
async def get_branches(owner: str, repo: str):
    try:
        return await github_service.get_branches(owner, repo)
    except HTTPException as e:
        raise e

@router.post("/{owner}/{repo}/branches", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_branch(
    owner: str, 
    repo: str, 
    branch_name: str = Body(..., embed=True),
    source_branch: str = Body("main", embed=True)
):
    try:
        new_branch = await github_service.create_branch(owner, repo, branch_name, source_branch)
        return {
            "message": f"Branch '{new_branch.name}' created successfully.",
            "data": new_branch
        }
    except HTTPException as e:
        raise e

@router.post("/{owner}/{repo}/pulls", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_pull_request(owner: str, repo: str, pr_data: CreatePullRequest):
    try:
        new_pr = await github_service.create_pull_request(owner, repo, pr_data)
        return {
            "message": f"Pull request #{new_pr.number} created successfully.",
            "data": new_pr
        }
    except HTTPException as e:
        raise e

@router.put("/{owner}/{repo}/pulls/{pr_number}/merge", response_model=Dict[str, str])
async def merge_pull_request(owner: str, repo: str, pr_number: int):
    try:
        result = await github_service.merge_pull_request(owner, repo, pr_number)
        return {"message": result.get("message", "Pull request merged successfully.")}
    except HTTPException as e:
        raise e

@router.get("/{owner}/{repo}/issues", response_model=List[GithubIssue])
async def get_issues(owner: str, repo: str):
    try:
        return await github_service.get_issues(owner, repo)
    except HTTPException as e:
        raise e

@router.post("/{owner}/{repo}/issues", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_issue(owner: str, repo: str, issue_data: CreateGithubIssue):
    try:
        new_issue = await github_service.create_issue(owner, repo, issue_data)
        return {
            "message": f"Issue #{new_issue.number} created successfully.",
            "data": new_issue
        }
    except HTTPException as e:
        raise e

@router.post("/{owner}/{repo}/issues/{issue_number}/comments", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def comment_issue(
    owner: str, 
    repo: str, 
    issue_number: int, 
    comment_body: str = Body(..., embed=True, alias="body")
):
    try:
        new_comment = await github_service.comment_issue(owner, repo, issue_number, comment_body)
        return {
            "message": "Comment added successfully.",
            "data": new_comment
        }
    except HTTPException as e:
        raise e
