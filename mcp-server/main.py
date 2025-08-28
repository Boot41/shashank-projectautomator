from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

class PromptRequest(BaseModel):
    prompt: str

class ProcessCommandRequest(BaseModel):
    natural_language: str = Field(..., description="Natural language input to be converted to CLI command")

# Optional: load .env if python-dotenv is installed
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

try:
    # Prefer absolute import when running via `uvicorn main:app`
    import jira_tool as jira_tool  # type: ignore
    import ai_tool as ai_tool  # type: ignore
except Exception:
    try:
        # Fallback for running as a module: `python -m mcp-server.main`
        from . import jira_tool as jira_tool  # type: ignore
        from . import ai_tool as ai_tool  # type: ignore
    except Exception:
        # If both fail, surface the original error
        raise

app = FastAPI(title="MCP Server", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/jira/projects")
def list_projects():
    """
    List all Jira projects that the user has permission to view.
    """
    return jira_tool.get_jira_projects()


@app.get("/jira/projects/{project_key}/issues")
def get_project_issues(project_key: str, status: str = None):
    """
    Get all issues for a specific Jira project.
    
    Args:
        project_key: The project key (e.g., 'TP')
        status: Optional status filter (e.g., 'Open', 'In Progress')
    """
    return jira_tool.get_issues_for_project(project_key, status)


@app.get("/jira/{ticket_id}")
def get_jira(ticket_id: str):
    return jira_tool.fetch_jira_issue(ticket_id)
    

@app.post("/ai/generate")
def generate_ai(request: PromptRequest):
    return ai_tool.generate_ai_response(request.prompt)

@app.post("/ai/process-command")
def process_command(request: ProcessCommandRequest):
    """
    Convert natural language input into a CLI command using AI.
    
    This endpoint takes a natural language input and returns the most likely
    CLI command that matches the user's intent.
    
    Example:
    {
        "natural_language": "show me ticket ABC-123"
    }
    """
    return ai_tool.process_natural_language(request.natural_language)