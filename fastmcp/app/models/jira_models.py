

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

class JiraSprint(BaseModel):
    id: int
    name: str
    state: str
    boardId: int

class CreateJiraIssue(BaseModel):
    project_key: str
    summary: str
    description: str
    issuetype_name: str = "Task"
