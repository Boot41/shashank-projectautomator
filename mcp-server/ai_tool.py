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
    system_prompt = """You are a helpful assistant that converts natural language requests into CLI commands for development tools.
    
    Available Jira commands:
    - jira get --id <ticket_id>: Get details of a Jira ticket
    - jira projects: List all Jira projects you have access to
    - jira list-issues --project <project_key> [--status <status>]: List issues in a project
    - jira summarize --id <ticket_id>: Get an AI summary of a Jira ticket
    
    Available GitHub commands:
    - github commits <owner>/<repo> [--branch <branch>] [--limit <number>]: Get commit history
    - github commits <owner>/<repo> --since <date> --until <date>: Get commits in date range
    - github commits <owner>/<repo> --branch main --limit 5: Get last 5 commits from main branch
    
    General commands:
    - help: Show help information
    
    Examples:
    - "What projects do I have access to?" -> jira projects
    - "Show me ticket ABC-123" -> jira get --id ABC-123
    - "Show commits from reactjs/react-app" -> github commits reactjs/react-app
    - "Show last 5 commits from main branch" -> github commits owner/repo --branch main --limit 5
    - "Show commits from last week" -> github commits owner/repo --since "1 week ago"
    - "Show commits between Jan 1 and Feb 1" -> github commits owner/repo --since "2023-01-01" --until "2023-02-01"
    - "List in-progress issues in project DEV" -> jira list-issues --project DEV --status "In Progress"
    - "Show me all bugs in project TEST" -> jira list-issues --project TEST --status "Bug"
    - "What's in the backlog for project ABC?" -> jira list-issues --project ABC --status "Backlog"
    
    The user will provide a natural language request. Convert it to the appropriate CLI command.
    If the request is unclear or ambiguous, respond with a help message.
    Only respond with the CLI command, nothing else.
    """
    
    patterns = [
        # Jira patterns
        (r'(?i)(?:show|get|what is|what\'s).*ticket\s+([A-Z]+-\d+)', 'jira get --id \1', 0.9),
        (r'(?i)(?:list|show).*projects', 'jira projects', 0.9),
        (r'(?i)(?:list|show).*issues.*project\s+([A-Z0-9]+)', 'jira list-issues --project \1', 0.85),
        (r'(?i)(?:list|show).*(?:open|in progress).*project\s+([A-Z0-9]+)', 'jira list-issues --project \1 --status "In Progress"', 0.9),
        (r'(?i)summar(?:y|ize).*ticket\s+([A-Z]+-\d+)', 'jira summarize --id \1', 0.9),
        
        # GitHub patterns - More specific patterns first
        (r'(?i)(?:show|list|get).*(\d+).*commits?.*(?:from|in|for)\s+([a-zA-Z0-9_-]+\/[a-zA-Z0-9_-]+).*branch\s+([^\s\n]+)', 'github commits \2 --branch \3 --limit \1', 0.95),
        (r'(?i)(?:show|list|get).*commits?.*(?:from|in|for)\s+([a-zA-Z0-9_-]+\/[a-zA-Z0-9_-]+).*branch\s+([^\s\n]+)', 'github commits \1 --branch \2', 0.9),
        (r'(?i)(?:show|list|get).*(\d+).*commits?.*(?:from|in|for)\s+([a-zA-Z0-9_-]+\/[a-zA-Z0-9_-]+)', 'github commits \2 --limit \1', 0.9),
        (r'(?i)(?:show|list|get).*commits?.*(?:from|in|for)\s+([a-zA-Z0-9_-]+\/[a-zA-Z0-9_-]+)', 'github commits \1', 0.85),
        (r'(?i)(?:commits?|changes).*since\s+(.*?)(?:\s+until|\s+to|\s+til|\s+before)?\s*([^\s\n]+)?', 'github commits \1 --since "\2" --until "\3"', 0.85),
        (r'(?i)last\s+(\d+)\s+commits?.*(?:on|from|in)?\s*([a-zA-Z0-9_-]+\/[a-zA-Z0-9_-]+)?', 'github commits \2 --limit \1', 0.9),
        
        # Help command
        (r'(?i)(?:help|what can you do|how to use)', 'help', 1.0),
    ]
    
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
        
        # Clean up the command - remove any leading/trailing spaces and quotes
        command = command.strip('"\'').strip()
        
        # If the response starts with a command we recognize, use it directly
        valid_commands = [
            'jira get --id',
            'jira projects',
            'jira list-issues',
            'jira summarize --id',
            'github commits',
            'help'
        ]
        
        # Check if the command starts with any valid prefix
        if any(command.startswith(cmd) for cmd in valid_commands):
            # Ensure github commits has the correct format
            if command.startswith('github commits'):
                # Remove any extra spaces between words
                parts = command.split()
                # Reconstruct the command with proper spacing
                command = f"{parts[0]} {parts[1]} {parts[2]} {' '.join(parts[3:])}"
            
            return {
                'status': 'success',
                'command': command,
                'explanation': f'Converted natural language to command: {command}'
            }
        
        return {
            "error": f"Generated command '{command}' is not a valid command. Try 'help' for available commands.",
            "status": "error",
            "error_type": "invalid_command",
            "confidence": 0.9,  # High confidence for now
            "explanation": f"Converted natural language to command: {command}"
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
