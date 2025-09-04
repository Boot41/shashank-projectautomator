from fastapi import FastAPI, HTTPException, Body
from .routers import jira, github

app = FastAPI(title="FastMCP API")

@app.get("/")
async def root():
    return {"message": "FastMCP server running"}

# REST endpoints still work
app.include_router(jira.router, prefix="/jira", tags=["Jira"])
app.include_router(github.router, prefix="/github", tags=["GitHub"])

try:
    from .orchestration.coordinator import create_orchestrator_agent
    agent = create_orchestrator_agent()

    @app.post("/adk/agent")
    async def run_adk(prompt: str = Body(..., embed=True)):
        """Run natural language input through orchestrator agent."""
        response = await agent.run(prompt)
        return {"response": response}
except Exception as e:
    adk_error_detail = str(e)

    @app.post("/adk/agent")
    async def run_adk(prompt: str = Body(..., embed=True)):
        # Fallback stub: echo prompt so clients can continue development/testing
        return {"response": prompt, "adk_disabled": True, "detail": adk_error_detail}
