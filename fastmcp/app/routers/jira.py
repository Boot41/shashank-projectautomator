
from fastapi import APIRouter, HTTPException, Body
from typing import List, Dict, Any
from ..services import jira_service
from ..models.jira_models import JiraIssue, JiraProject, JiraIssueBasic, CreateJiraIssue, JiraSprint

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

@router.post("/issue", response_model=Dict[str, Any], status_code=201)
async def create_issue(issue_data: CreateJiraIssue):
    try:
        return await jira_service.create_issue(issue_data)
    except HTTPException as e:
        raise e

@router.put("/issue/{issue_key}/assign", status_code=204)
async def assign_issue(issue_key: str, assignee_name: str = Body(..., embed=True)):
    try:
        await jira_service.assign_issue(issue_key, assignee_name)
        return
    except HTTPException as e:
        raise e

@router.get("/issue/{issue_key}/transitions", response_model=List[Dict[str, Any]])
async def get_transitions(issue_key: str):
    try:
        return await jira_service.get_possible_transitions(issue_key)
    except HTTPException as e:
        raise e

@router.post("/issue/{issue_key}/transition", status_code=204)
async def transition_issue(issue_key: str, transition_id: str = Body(..., embed=True)):
    try:
        await jira_service.transition_issue(issue_key, transition_id)
        return
    except HTTPException as e:
        raise e

@router.post("/issue/{issue_key}/comment", response_model=Dict[str, Any], status_code=201)
async def add_comment(issue_key: str, comment_text: str = Body(..., embed=True)):
    try:
        return await jira_service.comment_issue(issue_key, comment_text)
    except HTTPException as e:
        raise e

@router.get("/sprints/{project_key}", response_model=List[JiraSprint])
async def get_sprints(project_key: str):
    try:
        return await jira_service.get_sprints(project_key)
    except HTTPException as e:
        raise e

@router.post("/sprint/{sprint_id}/issue", status_code=204)
async def move_issue_to_sprint(sprint_id: int, issue_key: str = Body(..., embed=True)):
    try:
        await jira_service.move_issue_to_sprint(sprint_id, issue_key)
        return
    except HTTPException as e:
        raise e
