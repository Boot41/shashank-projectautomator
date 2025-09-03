
from pydantic import BaseModel

class ProcessedCommand(BaseModel):
    command: str
    explanation: str

class AIResponse(BaseModel):
    response: str
