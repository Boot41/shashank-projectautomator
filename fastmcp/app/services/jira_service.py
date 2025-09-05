import httpx
from fastapi import HTTPException
from typing import List, Dict, Any

from ..config.settings import settings
from ..models.jira_models import JiraIssue, JiraProject, JiraIssueBasic, JiraSprint, CreateJiraIssue
from ..tools import tool

@tool(name="jira_fetch_issue")
async def fetch_jira_issue(ticket_id: str) -> JiraIssue:
    """Fetches a single Jira issue by its ticket ID."""
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
            r = await client.get(url, auth=auth, headers=headers, timeout=settings.http_timeout)
            if r.status_code == 404:
                raise HTTPException(status_code=404, detail="Ticket not found")
            r.raise_for_status()
            data = r.json()
            fields = data.get("fields", {}) or {}
            status = fields.get("status") or {}
            assignee = fields.get("assignee") or {}
            description = extract_description(fields.get("description")) or ""
            return JiraIssue(
                ticket=data.get("key", ticket_id),
                title=fields.get("summary", ""),
                status=status.get("name", ""),
                assignee=assignee.get("displayName", ""),
                description=description
            )
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Jira API error: {e}")

@tool(name="jira_get_projects")
async def get_jira_projects() -> List[JiraProject]:
    """Gets a list of all available Jira projects."""
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
            response = await client.get(url, auth=auth, headers=headers, timeout=settings.http_timeout)
            response.raise_for_status()
            projects = response.json()
            return [JiraProject(**p) for p in projects]
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Failed to fetch Jira projects: {e}")

@tool(name="jira_get_issues_for_project")
async def get_issues_for_project(project_key: str, status: str = None) -> List[JiraIssueBasic]:
    """Gets a list of issues for a specific project, optionally filtered by status."""
    if settings.jira_mock:
        return [
            JiraIssueBasic(
                key=f"{project_key}-1", 
                summary="Sample issue 1", 
                status="To Do", 
                assignee="John Doe", 
                priority="High",
                due_date="2025-09-15",
                reporter="Admin User",
                created="2025-09-01",
                updated="2025-09-01"
            ),
            JiraIssueBasic(
                key=f"{project_key}-2", 
                summary="Sample issue 2", 
                status="In Progress", 
                assignee="Jane Smith", 
                priority="Medium",
                due_date="2025-09-20",
                reporter="Admin User",
                created="2025-09-02",
                updated="2025-09-03"
            )
        ]

    jql = f"project = {project_key}"
    if status:
        jql += f" AND status = '{status}'"
    
    url = f"{settings.jira_base_url.rstrip('/')}/rest/api/3/search"
    auth = (settings.jira_email, settings.jira_api_token)
    headers = {"Accept": "application/json"}
    params = {
        "jql": jql,
        "fields": "summary,status,assignee,priority,duedate,reporter,created,updated",
        "maxResults": 50,
        "startAt": 0,
    }

    async with httpx.AsyncClient() as client:
        try:
            issues: List[JiraIssueBasic] = []
            while True:
                response = await client.get(url, auth=auth, headers=headers, params=params, timeout=settings.http_timeout)
                response.raise_for_status()
                data = response.json()
                for issue in data.get("issues", []):
                    fields = issue.get("fields", {})
                    status_data = fields.get("status", {})
                    assignee_data = fields.get("assignee", {})
                    priority_data = fields.get("priority", {})
                    reporter_data = fields.get("reporter", {})
                    
                    # Format dates for better readability
                    created_date = fields.get("created")
                    updated_date = fields.get("updated")
                    due_date = fields.get("duedate")
                    
                    if created_date:
                        created_date = created_date.split("T")[0]  # Extract just the date part
                    if updated_date:
                        updated_date = updated_date.split("T")[0]  # Extract just the date part
                    
                    issues.append(JiraIssueBasic(
                        key=issue.get("key"),
                        summary=fields.get("summary"),
                        status=status_data.get("name") if status_data else None,
                        assignee=assignee_data.get("displayName") if assignee_data else "Unassigned",
                        priority=priority_data.get("name") if priority_data else None,
                        due_date=due_date,
                        reporter=reporter_data.get("displayName") if reporter_data else None,
                        created=created_date,
                        updated=updated_date
                    ))
                if len(data.get("issues", [])) < params["maxResults"]:
                    break
                params["startAt"] += params["maxResults"]
            return issues
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Failed to fetch issues for project {project_key}: {str(e)}")

@tool(name="jira_create_issue")
async def create_issue(issue_data: CreateJiraIssue) -> Dict[str, Any]:
    """Creates a new issue in Jira."""
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
            response = await client.post(url, auth=auth, headers=headers, json=payload, timeout=settings.http_timeout)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Failed to create Jira issue: {e}")

@tool(name="jira_assign_issue")
async def assign_issue(issue_key: str, assignee_name: str) -> None:
    """Assigns a Jira issue to a user by their name."""
    if settings.jira_mock:
        return

    user_url = f"{settings.jira_base_url.rstrip('/')}/rest/api/3/user/search?query={assignee_name}"
    auth = (settings.jira_email, settings.jira_api_token)
    headers = {"Accept": "application/json"}
    
    async with httpx.AsyncClient() as client:
        try:
            user_response = await client.get(user_url, auth=auth, headers=headers, timeout=settings.http_timeout)
            user_response.raise_for_status()
            users = user_response.json()
            if not users:
                raise HTTPException(status_code=404, detail=f"User '{assignee_name}' not found in Jira.")
            
            account_id = users[0].get("accountId")
            if not account_id:
                raise HTTPException(status_code=404, detail=f"Could not find accountId for user '{assignee_name}'.")

            assign_url = f"{settings.jira_base_url.rstrip('/')}/rest/api/3/issue/{issue_key}/assignee"
            payload = {"accountId": account_id}
            
            response = await client.put(assign_url, auth=auth, headers=headers, json=payload, timeout=settings.http_timeout)
            response.raise_for_status()

        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Failed to assign issue {issue_key}: {e}")

@tool(name="jira_get_possible_transitions")
async def get_possible_transitions(issue_key: str) -> List[Dict[str, Any]]:
    """Gets the possible workflow transitions for a Jira issue."""
    if settings.jira_mock:
        return [{"id": "1", "name": "To Do"}, {"id": "2", "name": "In Progress"}, {"id": "3", "name": "Done"}]

    url = f"{settings.jira_base_url.rstrip('/')}/rest/api/3/issue/{issue_key}/transitions"
    auth = (settings.jira_email, settings.jira_api_token)
    headers = {"Accept": "application/json"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, auth=auth, headers=headers, timeout=settings.http_timeout)
            response.raise_for_status()
            return response.json().get("transitions", [])
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Failed to get transitions for issue {issue_key}: {e}")

@tool(name="jira_transition_issue")
async def transition_issue(issue_key: str, transition_id: str) -> Dict[str, Any]:
    """Transitions a Jira issue to a new status using a transition ID."""
    if settings.jira_mock:
        return {"status": "success", "message": f"Issue {issue_key} transitioned successfully", "transition_id": transition_id}

    url = f"{settings.jira_base_url.rstrip('/')}/rest/api/3/issue/{issue_key}/transitions"
    auth = (settings.jira_email, settings.jira_api_token)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    payload = {"transition": {"id": transition_id}}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, auth=auth, headers=headers, json=payload, timeout=settings.http_timeout)
            response.raise_for_status()
            return {"status": "success", "message": f"Issue {issue_key} transitioned successfully", "transition_id": transition_id}
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Failed to transition issue {issue_key}: {e}")

@tool(name="jira_get_issue_comments")
async def get_issue_comments(issue_key: str) -> List[Dict[str, Any]]:
    """Gets all comments for a Jira issue."""
    if settings.jira_mock:
        return [
            {"id": "12345", "body": "This is a mock comment", "author": {"displayName": "Test User"}, "created": "2023-01-01T00:00:00.000Z"}
        ]

    url = f"{settings.jira_base_url.rstrip('/')}/rest/api/3/issue/{issue_key}/comment"
    auth = (settings.jira_email, settings.jira_api_token)
    headers = {"Accept": "application/json"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, auth=auth, headers=headers, timeout=settings.http_timeout)
            response.raise_for_status()
            data = response.json()
            return data.get("comments", [])
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Failed to get comments for issue {issue_key}: {e}")

async def comment_issue(issue_key: str, comment_text: str) -> Dict[str, Any]:
    """Adds a comment to a Jira issue."""
    if settings.jira_mock:
        return {"id": "12345", "body": comment_text}

    url = f"{settings.jira_base_url.rstrip('/')}/rest/api/3/issue/{issue_key}/comment"
    auth = (settings.jira_email, settings.jira_api_token)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    payload = {
        "body": {
            "type": "doc", "version": 1,
            "content": [{"type": "paragraph", "content": [{"type": "text", "text": comment_text}]}]
        }
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, auth=auth, headers=headers, json=payload, timeout=settings.http_timeout)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Failed to add comment to issue {issue_key}: {e}")

async def get_board_id_for_project(project_key: str) -> int:
    """(Internal) Gets the board ID for a project. Not a tool for the AI."""
    url = f"{settings.jira_base_url.rstrip('/')}/rest/agile/1.0/board?projectKeyOrId={project_key}"
    auth = (settings.jira_email, settings.jira_api_token)
    headers = {"Accept": "application/json"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, auth=auth, headers=headers, timeout=settings.http_timeout)
            response.raise_for_status()
            boards = response.json().get("values", [])
            if not boards:
                raise HTTPException(status_code=404, detail=f"No board found for project {project_key}")
            return boards[0]['id']
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Failed to get board for project {project_key}: {e}")

@tool(name="jira_get_sprints")
async def get_sprints(project_key: str) -> List[JiraSprint]:
    """Gets a list of all sprints for a given project."""
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
            response = await client.get(url, auth=auth, headers=headers, timeout=settings.http_timeout)
            response.raise_for_status()
            sprints: List[JiraSprint] = []
            data = response.json()
            sprints.extend([JiraSprint(**s) for s in data.get("values", [])])
            # Jira Agile sprint list supports pagination with 'startAt' and 'maxResults' via query params; implement simple forward paging
            start_at = data.get("startAt", 0)
            max_results = data.get("maxResults", len(sprints))
            is_last = data.get("isLast", True)
            while not is_last:
                params = {"startAt": start_at + max_results}
                response = await client.get(url, auth=auth, headers=headers, params=params, timeout=settings.http_timeout)
                response.raise_for_status()
                data = response.json()
                sprints.extend([JiraSprint(**s) for s in data.get("values", [])])
                start_at = data.get("startAt", start_at + max_results)
                max_results = data.get("maxResults", max_results)
                is_last = data.get("isLast", True)
            return sprints
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Failed to get sprints for project {project_key}: {e}")

@tool(name="jira_move_issue_to_sprint")
async def move_issue_to_sprint(sprint_id: int, issue_key: str) -> None:
    """Moves a Jira issue to a specific sprint."""
    if settings.jira_mock:
        return

    url = f"{settings.jira_base_url.rstrip('/')}/rest/agile/1.0/sprint/{sprint_id}/issue"
    auth = (settings.jira_email, settings.jira_api_token)
    headers = {"Content-Type": "application/json"}
    payload = {"issues": [issue_key]}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, auth=auth, headers=headers, json=payload, timeout=settings.http_timeout)
            response.raise_for_status()
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Failed to move issue {issue_key} to sprint {sprint_id}: {e}")

def extract_description(description_doc: dict) -> str:
    """(Internal) Extracts text from Jira's description document. Not a tool for the AI."""
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