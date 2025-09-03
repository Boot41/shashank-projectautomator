
import httpx
from fastapi import HTTPException
from typing import List, Dict, Any

from ..config.settings import settings
from ..models.jira_models import JiraIssue, JiraProject, JiraIssueBasic

async def fetch_jira_issue(ticket_id: str) -> JiraIssue:
    if settings.jira_mock:
        return JiraIssue(
            ticket=ticket_id,
            title="Login bug",
            status="Open",
            assignee="alex",
            description="A mock description"
        )

    url = f"{settings.jira_base_url.rstrip('/')}/rest/api/3/issue/{ticket_id}"
    auth = (settings.jira_email, settings.jira_api_token)
    headers = {"Accept": "application/json"}

    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(url, auth=auth, headers=headers, timeout=10)
            if r.status_code == 404:
                raise HTTPException(status_code=404, detail="Ticket not found")
            r.raise_for_status()
            data = r.json()
            fields = data.get("fields", {}) or {}
            status = fields.get("status") or {}
            assignee = fields.get("assignee") or {}
            description = extract_description(fields.get("description")) or {}
            return JiraIssue(
                ticket=data.get("key", ticket_id),
                title=fields.get("summary", ""),
                status=status.get("name", ""),
                assignee=assignee.get("displayName", ""),
                description=description
            )
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Jira API error: {e}")

async def get_jira_projects() -> List[JiraProject]:
    if settings.jira_mock:
        return [
            JiraProject(id="10000", key="TP", name="Test Project", projectTypeKey="software"),
            JiraProject(id="10001", key="DEV", name="Development", projectTypeKey="software")
        ]

    url = f"{settings.jira_base_url.rstrip('/')}/rest/api/3/project"
    auth = (settings.jira_email, settings.jira_api_token)
    headers = {"Accept": "application/json"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, auth=auth, headers=headers, timeout=10)
            response.raise_for_status()
            projects = response.json()
            return [JiraProject(**p) for p in projects]
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Failed to fetch Jira projects: {e}")

async def get_issues_for_project(project_key: str, status: str = None) -> List[JiraIssueBasic]:
    if settings.jira_mock:
        return [
            JiraIssueBasic(key=f"{project_key}-1", summary="Sample issue 1", status="To Do", assignee="John Doe", priority="High"),
            JiraIssueBasic(key=f"{project_key}-2", summary="Sample issue 2", status="In Progress", assignee="Jane Smith", priority="Medium")
        ]

    jql = f"project = {project_key}"
    if status:
        jql += f" AND status = '{status}'"
    
    url = f"{settings.jira_base_url.rstrip('/')}/rest/api/3/search"
    auth = (settings.jira_email, settings.jira_api_token)
    headers = {"Accept": "application/json"}
    params = {
        "jql": jql,
        "fields": "summary,status,assignee,priority",
        "maxResults": 50
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, auth=auth, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            issues = []
            for issue in response.json().get("issues", []):
                fields = issue.get("fields", {})
                status_data = fields.get("status", {})
                assignee_data = fields.get("assignee", {})
                priority_data = fields.get("priority", {})
                
                issues.append(JiraIssueBasic(
                    key=issue.get("key"),
                    summary=fields.get("summary"),
                    status=status_data.get("name") if status_data else None,
                    assignee=assignee_data.get("displayName") if assignee_data else "Unassigned",
                    priority=priority_data.get("name") if priority_data else None
                ))
            return issues
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Failed to fetch issues for project {project_key}: {str(e)}")

def extract_description(description_doc: dict) -> str:
    if not description_doc or not isinstance(description_doc, dict):
        return ""
    if 'content' in description_doc:
        text_parts = []
        for content in description_doc.get('content', []):
            if content.get('type') == 'paragraph' and 'content' in content:
                for item in content['content']:
                    if item.get('type') == 'text':
                        text_parts.append(item.get('text', ''))
        return ' '.join(text_parts).strip()
    return str(description_doc)
