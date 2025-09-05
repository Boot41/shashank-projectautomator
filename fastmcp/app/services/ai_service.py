
import google.generativeai as genai
from fastapi import HTTPException

from ..config.settings import settings
from ..models.ai_models import ProcessedCommand, AIResponse

def configure_genai():
    if not settings.gemini_api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY environment variable not set")
    genai.configure(api_key=settings.gemini_api_key)

async def process_natural_language(natural_language: str) -> ProcessedCommand:
    configure_genai()
    
    system_prompt = """You are a helpful assistant that converts natural language requests into CLI commands for development tools.
    
    Available Jira commands:
    - jira get --id <ticket_id>: Get details of a Jira ticket
    - jira projects: List all Jira projects you have access to
    - jira list-issues --project <project_key> [--status <status>]: List issues in a project
    - jira summarize --id <ticket_id>: Get an AI summary of a Jira ticket
    
    Available GitHub commands:
    - github commits <owner>/<repo> [--branch <branch>] [--limit <number>]: Get commit history
    - github commits <owner>/<repo> --since <date> --until <date>: Get commits in date range
    
    General commands:
    - help: Show help information
    
    The user will provide a natural language request. Convert it to the appropriate CLI command.
    If the request is unclear or ambiguous, respond with a help message.
    Only respond with the CLI command, nothing else.
    """
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        response = await model.generate_content_async(
            f"{system_prompt}\n\nUser request: {natural_language}"
        )
        
        command = response.text.strip().strip('"\'')
        
        valid_commands = [
            'jira get --id', 'jira projects', 'jira list-issues', 'jira summarize --id',
            'github commits', 'help'
        ]
        
        if any(command.startswith(cmd) for cmd in valid_commands):
            return ProcessedCommand(
                command=command,
                explanation=f'Converted natural language to command: {command}'
            )
        
        raise HTTPException(status_code=400, detail=f"Generated command '{command}' is not a valid command.")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process natural language: {str(e)}")

async def generate_ai_response(prompt: str) -> AIResponse:
    configure_genai()
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        response = await model.generate_content_async(prompt)
        
        if not response.text:
            raise HTTPException(status_code=500, detail="Received empty response from AI service")
            
        return AIResponse(response=response.text)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")
