
from fastapi import APIRouter, HTTPException
from typing import List
from ..services import jira_service
from ..models.jira_models import JiraIssue, JiraProject, JiraIssueBasic

router = APIRouter()

@router.get("/issue/{ticket_id}", response_model=JiraIssue)
async def get_issue(ticket_id: str):
    try:
        return await jira_service.fetch_jira_issue(ticket_id)
    except HTTPException as e:
        raise e

@router.get("/projects", response_model=List[JiraProject])
async def list_projects():
    try:
        return await jira_service.get_jira_projects()
    except HTTPException as e:
        raise e

@router.get("/issues/{project_key}", response_model=List[JiraIssueBasic])
async def list_issues(project_key: str, status: str = None):
    try:
        return await jira_service.get_issues_for_project(project_key, status)
    except HTTPException as e:
        raise e
