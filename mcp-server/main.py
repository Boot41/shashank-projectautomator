from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
    return {
        "ticket": ticket_id,
        "title": "Login bug",
        "status": "Open",
        "assignee": "alex",
        "url": f"https://jira.example.com/browse/{ticket_id}",
    }