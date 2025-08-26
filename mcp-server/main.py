from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Optional: load .env if python-dotenv is installed
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

try:
    # Prefer absolute import when running via `uvicorn main:app`
    import jira_tool as jira_tool  # type: ignore
except Exception:
    try:
        # Fallback for running as a module: `python -m mcp-server.main`
        from . import jira_tool as jira_tool  # type: ignore
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

@app.get("/jira/{ticket_id}")
def get_jira(ticket_id: str):
    return jira_tool.fetch_jira_issue(ticket_id)