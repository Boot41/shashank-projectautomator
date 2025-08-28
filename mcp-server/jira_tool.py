import os
from typing import Any, Dict
import google.generativeai as genai

import requests
from fastapi import HTTPException
from requests.auth import HTTPBasicAuth

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

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

def extract_description(description_doc: dict) -> str:
    """
    Extract plain text from Jira's document format description.
    
    Args:
        description_doc: The description field from Jira API response
        
    Returns:
        str: Plain text description
    """
    if not description_doc:
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
