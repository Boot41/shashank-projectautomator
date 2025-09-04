from pydantic import BaseModel
from typing import List, Optional

class GithubRepo(BaseModel):
    name: str
    full_name: str
    private: bool
    html_url: str
    description: Optional[str] = None

class GithubBranch(BaseModel):
    name: str
    commit_sha: str

class CreatePullRequest(BaseModel):
    title: str
    body: str
    head: str  # The name of the branch where your changes are implemented
    base: str  # The name of the branch you want the changes pulled into

class PullRequest(BaseModel):
    id: int
    number: int
    title: str
    state: str # e.g., "open", "closed"
    html_url: str

class GithubIssue(BaseModel):
    id: int
    number: int
    title: str
    state: str
    html_url: str
    body: Optional[str] = None

class CreateGithubIssue(BaseModel):
    title: str
    body: Optional[str] = None