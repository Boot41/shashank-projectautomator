
from fastapi import APIRouter, HTTPException, Body
from ..services import ai_service
from ..models.ai_models import ProcessedCommand, AIResponse

router = APIRouter()

@router.post("/process-nl", response_model=ProcessedCommand)
async def process_nl(natural_language: str = Body(..., embed=True)):
    try:
        return await ai_service.process_natural_language(natural_language)
    except HTTPException as e:
        raise e

@router.post("/generate", response_model=AIResponse)
async def generate(prompt: str = Body(..., embed=True)):
    try:
        return await ai_service.generate_ai_response(prompt)
    except HTTPException as e:
        raise e
