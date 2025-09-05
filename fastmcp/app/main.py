from fastapi import FastAPI, HTTPException, Body, Header
from typing import Optional, Any, Dict
from .config.settings import settings
from .routers import jira, github

app = FastAPI(title="FastMCP API")

@app.get("/")
async def root():
    return {"message": "FastMCP server running"}

if settings.expose_rest_endpoints:
    app.include_router(jira.router, prefix="/jira", tags=["Jira"])
    app.include_router(github.router, prefix="/github", tags=["GitHub"])

try:
    from .orchestration.coordinator import create_orchestrator_agent
    agent = create_orchestrator_agent()

    @app.post("/adk/agent")
    async def run_adk(
        prompt: Optional[str] = Body(None, embed=True),
        body: Optional[Dict[str, Any]] = Body(None),
        x_api_key: Optional[str] = Header(None, convert_underscores=False),
    ):
        """Run natural language input through orchestrator agent."""
        # API key guard (optional)
        if settings.api_key and x_api_key != settings.api_key:
            raise HTTPException(status_code=401, detail="Invalid API key")

        # Support both legacy {prompt} and new {prompt, context}
        final_prompt = prompt
        context: Dict[str, Any] = {}
        session_id = None
        if body and isinstance(body, dict):
            if final_prompt is None and "prompt" in body:
                final_prompt = body.get("prompt")
            if isinstance(body.get("context"), dict):
                context = body.get("context") or {}
            session_id = body.get("session_id")
        if not final_prompt:
            raise HTTPException(status_code=422, detail="Missing 'prompt'")

        # Handle clear context command
        if final_prompt.strip() == "/clearcontext":
            from app.services.context_service import context_service
            context_service.clear_context()
            return {
                "result": "Context cleared successfully. Starting fresh session.",
                "toolCalls": [],
                "model_summary": "Session context has been reset."
            }

        # Pass prompt with session ID for context management
        response = await agent.run(str(final_prompt), session_id=session_id)
        # Normalize agent responses into the stable schema
        if isinstance(response, dict) and ("result" in response or "error" in response or "toolCalls" in response):
            return response
        return {"result": response, "toolCalls": [], "model_summary": None}
except Exception as e:
    adk_error_detail = str(e)

    @app.post("/adk/agent")
    async def run_adk(
        prompt: Optional[str] = Body(None, embed=True),
        body: Optional[Dict[str, Any]] = Body(None),
        x_api_key: Optional[str] = Header(None, convert_underscores=False),
    ):
        if settings.api_key and x_api_key != settings.api_key:
            raise HTTPException(status_code=401, detail="Invalid API key")
        final_prompt = prompt
        if body and isinstance(body, dict):
            if final_prompt is None and "prompt" in body:
                final_prompt = body.get("prompt")
        if not final_prompt:
            raise HTTPException(status_code=422, detail="Missing 'prompt'")
        return {"result": None, "toolCalls": [], "model_summary": None, "adk_disabled": True, "detail": adk_error_detail}
