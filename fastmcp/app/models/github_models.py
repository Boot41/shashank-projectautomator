
from pydantic import BaseModel
from typing import List, Optional

class CommitAuthor(BaseModel):
    name: str
    email: str
    date: str

class CommitInfo(BaseModel):
    sha: str
    message: str
    author: CommitAuthor
    url: str
    commit_url: str
    verification: bool
