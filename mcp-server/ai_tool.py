import os
from typing import Dict, Any
import google.generativeai as genai
from fastapi import HTTPException

def generate_ai_response(prompt: str) -> Dict[str, Any]:
    """
    Generate a response using Google's Generative AI.
    
    Args:
        prompt: The input prompt for the AI
        
    Returns:
        Dict containing the AI's response
    """
    try:
        # Initialize the model
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Generate content
        response = model.generate_content(prompt)
        
        return {
            "response": response.text,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI generation failed: {str(e)}"
        )
