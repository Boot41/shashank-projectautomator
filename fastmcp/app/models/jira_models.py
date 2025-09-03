
from pydantic import BaseModel
from typing import List, Optional

class JiraIssue(BaseModel):
    ticket: str
    title: str
    status: str
    assignee: str
    description: Optional[str] = None

class JiraProject(BaseModel):
    id: str
    key: str
    name: str
    projectTypeKey: Optional[str] = None

class JiraIssueBasic(BaseModel):
    key: str
    summary: str
    status: Optional[str] = None
    assignee: Optional[str] = "Unassigned"
    priority: Optional[str] = None
