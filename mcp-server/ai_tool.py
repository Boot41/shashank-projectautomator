from dotenv import load_dotenv
import os
import re
from typing import Dict, Any, List, Optional, Union
import google.generativeai as genai
from fastapi import HTTPException
from pydantic import BaseModel

class ProcessedCommand(BaseModel):
    command: str
    confidence: float
    explanation: str

load_dotenv()

def process_natural_language(prompt: str) -> Dict[str, Any]:
    """
    Process natural language input and convert it to a CLI command using Gemini.
    
    Args:
        prompt: Natural language input from user
        
    Returns:
        Dict containing the processed command or error
    """
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(f"""
        Convert this natural language request into a CLI command.
        Available commands:
        - jira get --id <TICKET_ID>
        - jira summarize --id <TICKET_ID>
        - /help
        - /quit

        Input: {prompt}
        
        Respond ONLY with the command, no explanations.
        """)
        
        return {
            "command": response.text.strip(),
            "status": "success"
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }

def process_natural_language(natural_language: str) -> Dict[str, Any]:
    """
    Convert natural language input into a CLI command using Gemini AI.
    
    Args:
        natural_language: The natural language input from the user
        
    Returns:
        Dict containing the processed command, confidence score, and explanation
    """
    if not os.getenv("GEMINI_API_KEY"):
        return {
            "error": "GEMINI_API_KEY environment variable not set",
            "status": "error",
            "error_type": "auth"
        }
    
    # System prompt to guide the AI in converting natural language to CLI commands
    system_prompt = """You are a helpful assistant that converts natural language requests into CLI commands for a Jira management tool.
    
    Available commands:
    - jira get --id <ticket_id>: Get details of a Jira ticket
    - jira summarize --id <ticket_id>: Get an AI summary of a Jira ticket
    - help: Show help information
    
    The user will provide a natural language request. Convert it to the appropriate CLI command.
    If the request is unclear or ambiguous, ask for clarification.
    Only respond with the CLI command, nothing else.
    """
    
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Generate the command
        response = model.generate_content(
            f"{system_prompt}\n\nUser request: {natural_language}"
        )
        
        if not response.text:
            return {
                "error": "Received empty response from AI service",
                "status": "error",
                "error_type": "api"
            }
        
        # Clean up and validate the response
        command = response.text.strip()
        
        # Basic validation of the command
        if not command.startswith(('jira get', 'jira summarize', 'help')):
            return {
                "error": f"Generated command '{command}' is not a valid command",
                "status": "error",
                "error_type": "invalid_command"
            }
        
        return {
            "command": command,
            "confidence": 0.9,  # High confidence for now
            "explanation": f"Converted natural language to command: {command}",
            "status": "success"
        }
        
    except Exception as e:
        return {
            "error": f"Failed to process natural language: {str(e)}",
            "status": "error",
            "error_type": "processing_error"
        }


def generate_ai_response(prompt: str) -> Dict[str, Any]:
    """
    Generate a response using Google's Generative AI.
    
    Args:
        prompt: The input prompt for the AI
        
    Returns:
        Dict containing the AI's response
    """
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    if not os.getenv("GEMINI_API_KEY"):
        return {
            "error": "GEMINI_API_KEY environment variable not set",
            "status": "error",
            "error_type": "auth"
        }
    

    try:
        # Initialize the model
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Generate content
        response = model.generate_content(prompt)

        if not response.text:
            return {
                "error": "Received empty response from AI service",
                "status": "error",
                "error_type": "api"
            }
        
        return {
            "response": response.text,
            "status": "success"
        }
    #Exceptions handler
    except genai.errors.APIError as e:
        error_type = "rate_limit" if "quota" in str(e).lower() or "rate" in str(e).lower() else "api"
        return {
            "error": f"API Error: {str(e)}",
            "status": "error",
            "error_type": error_type
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI generation failed: {str(e)}"
        )
