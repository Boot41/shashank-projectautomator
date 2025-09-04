
from fastapi import APIRouter, Body
from .. import agent
from typing import Dict, Any

router = APIRouter()

@router.post("/invoke", response_model=Dict[str, Any])
async def invoke_agent(prompt: str = Body(..., embed=True)):
    """
    Processes a natural language prompt through the AI agent.
    """
    return await agent.process_prompt(prompt)
