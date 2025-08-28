import os
from typing import Any, Dict, List

import requests
from fastapi import HTTPException
from requests.auth import HTTPBasicAuth

def fetch_jira_issue(ticket_id: str) -> Dict[str, Any]:
    """
    Fetch a Jira issue using either mock data or the real Jira Cloud REST API v3
    based on environment configuration.

    Env vars:
    - JIRA_MOCK: 'true' (default) to return mock data, 'false' to call Jira
    - JIRA_BASE_URL: e.g., https://your-domain.atlassian.net
    - JIRA_EMAIL: account email used for API token auth
    - JIRA_API_TOKEN: API token generated in Atlassian account
    """

    if os.getenv("JIRA_MOCK", "true").lower() == "true":
        return {
            "ticket": ticket_id,
            "title": "Login bug",
            "status": "Open",
            "assignee": "alex",
            "url": f"https://jira.example.com/browse/{ticket_id}",
        }

    base = os.getenv("JIRA_BASE_URL")
    email = os.getenv("JIRA_EMAIL")
    token = os.getenv("JIRA_API_TOKEN")

    if not base or not email or not token:
        raise HTTPException(status_code=500, detail="Jira credentials not configured")

    url = f"{base.rstrip('/')}/rest/api/3/issue/{ticket_id}"
    auth = HTTPBasicAuth(email, token)
    headers = {"Accept": "application/json"}

    try:
        r = requests.get(url, auth=auth, headers=headers, timeout=10)
        if r.status_code == 404:
            raise HTTPException(status_code=404, detail="Ticket not found")
        r.raise_for_status()
        data = r.json()
        fields = data.get("fields", {}) or {}
        status = fields.get("status") or {}
        assignee = fields.get("assignee") or {}
        description = extract_description(fields.get("description")) or {}
        return {
            "ticket": data.get("key", ticket_id),
            "title": fields.get("summary", ""),
            "status": status.get("name", ""),
            "assignee": assignee.get("displayName", ""),
            # "url": f"{base.rstrip('/')}/browse/{ticket_id}",
            "description": description
        }
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Jira API error: {e}")

def get_jira_projects() -> list[dict]:
    """
    Fetch all Jira projects that the user has permission to view.
    
    Returns:
        List of projects with id, key, name, and other details
    """
    if os.getenv("JIRA_MOCK", "true").lower() == "true":
        return [
            {"id": "10000", "key": "TP", "name": "Test Project", "projectTypeKey": "software"},
            {"id": "10001", "key": "DEV", "name": "Development", "projectTypeKey": "software"}
        ]

    base = os.getenv("JIRA_BASE_URL")
    email = os.getenv("JIRA_EMAIL")
    token = os.getenv("JIRA_API_TOKEN")

    if not all([base, email, token]):
        raise HTTPException(status_code=500, detail="Jira credentials not configured")

    url = f"{base.rstrip('/')}/rest/api/3/project"
    auth = HTTPBasicAuth(email, token)
    headers = {"Accept": "application/json"}

    try:
        response = requests.get(url, auth=auth, headers=headers, timeout=10)
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Projects endpoint not found. Please check your Jira URL.")
        if response.status_code == 401:
            raise HTTPException(status_code=401, detail="Authentication failed. Please check your Jira credentials.")
        if response.status_code == 403:
            raise HTTPException(status_code=403, detail="Permission denied. You don't have access to view projects.")
            
        response.raise_for_status()
        projects = response.json()
        return [
            {
                "id": p["id"],
                "key": p["key"],
                "name": p["name"],
                "projectTypeKey": p.get("projectTypeKey", None)
            }
            for p in projects
        ]
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch Jira projects: {e}")

def get_issues_for_project(project_key: str, status: str = None) -> List[Dict[str, Any]]:
    """
    Fetch all issues for a specific Jira project.
    
    Args:
        project_key: The project key (e.g., 'TP')
        status: Optional status filter (e.g., 'Open', 'In Progress')
        
    Returns:
        List of issues with their details
    """
    if os.getenv("JIRA_MOCK", "true").lower() == "true":
        return [
            {
                "key": f"{project_key}-1",
                "summary": "Sample issue 1",
                "status": "To Do",
                "assignee": "John Doe",
                "priority": "High"
            },
            {
                "key": f"{project_key}-2",
                "summary": "Sample issue 2",
                "status": "In Progress",
                "assignee": "Jane Smith",
                "priority": "Medium"
            }
        ]

    base = os.getenv("JIRA_BASE_URL")
    email = os.getenv("JIRA_EMAIL")
    token = os.getenv("JIRA_API_TOKEN")

    if not all([base, email, token]):
        raise HTTPException(status_code=500, detail="Jira credentials not configured")

    # Build JQL query
    jql = f"project = {project_key}"
    if status:
        jql += f" AND status = '{status}'"
    
    url = f"{base.rstrip('/')}/rest/api/3/search"
    auth = HTTPBasicAuth(email, token)
    headers = {"Accept": "application/json"}
    params = {
        "jql": jql,
        "fields": "summary,status,assignee,priority",
        "maxResults": 50
    }

    try:
        response = requests.get(
            url, 
            auth=auth, 
            headers=headers, 
            params=params,
            timeout=10
        )
        
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Project {project_key} not found")
            
        response.raise_for_status()
        
        issues = []
        for issue in response.json().get("issues", []):
            fields = issue.get("fields", {})
            status = fields.get("status", {})
            assignee = fields.get("assignee", {})
            priority = fields.get("priority", {})
            
            issues.append({
                "key": issue.get("key"),
                "summary": fields.get("summary"),
                "status": status.get("name") if status else None,
                "assignee": assignee.get("displayName") if assignee else "Unassigned",
                "priority": priority.get("name") if priority else None
            })
            
        return issues
        
    except requests.RequestException as e:
        raise HTTPException(
            status_code=502, 
            detail=f"Failed to fetch issues for project {project_key}: {str(e)}"
        )


def extract_description(description_doc: dict) -> str:
    """
    Extract plain text from Jira's document format description.
    
    Args:
        description_doc: The description field from Jira API response
        
    Returns:
        str: Plain text description
    """
    if not description_doc or not isinstance(description_doc, dict):
        return ""
        
    try:
        # Handle case where description is already a string
        if isinstance(description_doc, str):
            return description_doc
            
        # Handle Atlassian Document Format (ADF)
        if 'content' in description_doc:
            text_parts = []
            for content in description_doc.get('content', []):
                if content.get('type') == 'paragraph' and 'content' in content:
                    for item in content['content']:
                        if item.get('type') == 'text':
                            text_parts.append(item.get('text', ''))
            return ' '.join(text_parts).strip()
            
        # Fallback to string representation if format is unexpected
        return str(description_doc)
    except Exception as e:
        print(f"Error parsing description: {e}")
        return str(description_doc)
