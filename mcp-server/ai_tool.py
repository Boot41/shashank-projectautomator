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
    - jira projects: List all Jira projects you have access to
    - jira list-issues --project <project_key> [--status <status>]: List issues in a project
    - jira summarize --id <ticket_id>: Get an AI summary of a Jira ticket
    - help: Show help information
    
    Examples:
    - "What projects do I have access to?" -> jira projects
    - "List all my Jira projects" -> jira projects
    - "Show me projects" -> jira projects
    - "What's the status of ticket ABC-123?" -> jira get --id ABC-123
    - "Summarize ticket TP-1" -> jira summarize --id TP-1
    - "Show me all issues in project ABC" -> jira list-issues --project ABC
    - "What's open in project XYZ?" -> jira list-issues --project XYZ --status "Open"
    - "List in-progress issues in project DEV" -> jira list-issues --project DEV --status "In Progress"
    - "Show me all bugs in project TEST" -> jira list-issues --project TEST --status "Bug"
    - "What's in the backlog for project ABC?" -> jira list-issues --project ABC --status "Backlog"
    
    The user will provide a natural language request. Convert it to the appropriate CLI command.
    If the request is unclear or ambiguous, respond with a help message.
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
        valid_commands = [
            'jira get', 
            'jira projects', 
            'jira summarize', 
            'jira list-issues',
            'help',
            '/help',
            '/quit'
        ]
        if not any(command.startswith(cmd) for cmd in valid_commands):
            return {
                "error": f"Generated command '{command}' is not a valid command. Try 'help' for available commands.",
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
