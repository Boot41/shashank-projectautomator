

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    gemini_api_key: str
    github_token: str
    jira_base_url: str
    jira_email: str
    jira_api_token: str
    jira_mock: bool = True

    class Config:
        env_file = ".env"

settings = Settings()
