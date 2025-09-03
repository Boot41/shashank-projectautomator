

from fastapi import FastAPI
from .routers import jira, github, ai

app = FastAPI(title="FastMCP API")

@app.get("/")
async def read_root():
    return {"message": "Welcome to FastMCP"}

app.include_router(jira.router, prefix="/jira", tags=["Jira"])
app.include_router(github.router, prefix="/github", tags=["GitHub"])
app.include_router(ai.router, prefix="/ai", tags=["AI"])
