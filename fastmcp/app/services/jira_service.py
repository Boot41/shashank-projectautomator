
import httpx
from fastapi import HTTPException
from typing import List, Dict, Any

from ..config.settings import settings
from ..models.jira_models import JiraIssue, JiraProject, JiraIssueBasic, JiraSprint, CreateJiraIssue

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

async def create_issue(issue_data: CreateJiraIssue) -> Dict[str, Any]:
    if settings.jira_mock:
        return {"key": f"{issue_data.project_key}-123", "summary": issue_data.summary}

    url = f"{settings.jira_base_url.rstrip('/')}/rest/api/3/issue"
    auth = (settings.jira_email, settings.jira_api_token)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    
    payload = {
        "fields": {
            "project": {"key": issue_data.project_key},
            "summary": issue_data.summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": issue_data.description}]}]
            },
            "issuetype": {"name": issue_data.issuetype_name}
        }
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, auth=auth, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Failed to create Jira issue: {e}")

async def assign_issue(issue_key: str, assignee_name: str) -> None:
    if settings.jira_mock:
        return

    # First, get user accountId from email or name
    user_url = f"{settings.jira_base_url.rstrip('/')}/rest/api/3/user/search?query={assignee_name}"
    auth = (settings.jira_email, settings.jira_api_token)
    headers = {"Accept": "application/json"}
    
    async with httpx.AsyncClient() as client:
        try:
            user_response = await client.get(user_url, auth=auth, headers=headers, timeout=10)
            user_response.raise_for_status()
            users = user_response.json()
            if not users:
                raise HTTPException(status_code=404, detail=f"User '{assignee_name}' not found in Jira.")
            
            account_id = users[0].get("accountId")
            if not account_id:
                raise HTTPException(status_code=404, detail=f"Could not find accountId for user '{assignee_name}'.")

            # Then, assign issue
            assign_url = f"{settings.jira_base_url.rstrip('/')}/rest/api/3/issue/{issue_key}/assignee"
            payload = {"accountId": account_id}
            
            response = await client.put(assign_url, auth=auth, headers=headers, json=payload, timeout=10)
            response.raise_for_status()

        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Failed to assign issue {issue_key}: {e}")

async def get_possible_transitions(issue_key: str) -> List[Dict[str, Any]]:
    if settings.jira_mock:
        return [
            {"id": "1", "name": "To Do"},
            {"id": "2", "name": "In Progress"},
            {"id": "3", "name": "Done"}
        ]

    url = f"{settings.jira_base_url.rstrip('/')}/rest/api/3/issue/{issue_key}/transitions"
    auth = (settings.jira_email, settings.jira_api_token)
    headers = {"Accept": "application/json"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, auth=auth, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json().get("transitions", [])
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Failed to get transitions for issue {issue_key}: {e}")

async def transition_issue(issue_key: str, transition_id: str) -> None:
    if settings.jira_mock:
        return

    url = f"{settings.jira_base_url.rstrip('/')}/rest/api/3/issue/{issue_key}/transitions"
    auth = (settings.jira_email, settings.jira_api_token)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    payload = {"transition": {"id": transition_id}}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, auth=auth, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Failed to transition issue {issue_key}: {e}")

async def comment_issue(issue_key: str, comment_text: str) -> Dict[str, Any]:
    if settings.jira_mock:
        return {"id": "12345", "body": comment_text}

    url = f"{settings.jira_base_url.rstrip('/')}/rest/api/3/issue/{issue_key}/comment"
    auth = (settings.jira_email, settings.jira_api_token)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    payload = {
        "body": {
            "type": "doc",
            "version": 1,
            "content": [{"type": "paragraph", "content": [{"type": "text", "text": comment_text}]}]
        }
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, auth=auth, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Failed to add comment to issue {issue_key}: {e}")

async def get_board_id_for_project(project_key: str) -> int:
    url = f"{settings.jira_base_url.rstrip('/')}/rest/agile/1.0/board?projectKeyOrId={project_key}"
    auth = (settings.jira_email, settings.jira_api_token)
    headers = {"Accept": "application/json"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, auth=auth, headers=headers, timeout=10)
            response.raise_for_status()
            boards = response.json().get("values", [])
            if not boards:
                raise HTTPException(status_code=404, detail=f"No board found for project {project_key}")
            return boards[0]['id']
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Failed to get board for project {project_key}: {e}")

async def get_sprints(project_key: str) -> List[JiraSprint]:
    if settings.jira_mock:
        return [
            JiraSprint(id=1, name="Sprint 1", state="active", boardId=1),
            JiraSprint(id=2, name="Sprint 2", state="future", boardId=1)
        ]
    
    board_id = await get_board_id_for_project(project_key)
    url = f"{settings.jira_base_url.rstrip('/')}/rest/agile/1.0/board/{board_id}/sprint"
    auth = (settings.jira_email, settings.jira_api_token)
    headers = {"Accept": "application/json"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, auth=auth, headers=headers, timeout=10)
            response.raise_for_status()
            sprints = response.json().get("values", [])
            return [JiraSprint(**s) for s in sprints]
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Failed to get sprints for project {project_key}: {e}")

async def move_issue_to_sprint(sprint_id: int, issue_key: str) -> None:
    if settings.jira_mock:
        return

    url = f"{settings.jira_base_url.rstrip('/')}/rest/agile/1.0/sprint/{sprint_id}/issue"
    auth = (settings.jira_email, settings.jira_api_token)
    headers = {"Content-Type": "application/json"}
    payload = {"issues": [issue_key]}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, auth=auth, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Failed to move issue {issue_key} to sprint {sprint_id}: {e}")

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
