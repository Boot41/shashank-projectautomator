

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    gemini_api_key: str
    github_token: str
    github_api_url: str = "https://api.github.com"
    github_mock: bool = False
    github_user_agent: str = "project-automator"
    jira_base_url: str
    jira_email: str
    jira_api_token: str
    jira_mock: bool = False
    http_timeout: float = 15.0
    jira_default_project_key: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()
