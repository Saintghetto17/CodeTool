"""Configuration management for Code Agent."""


from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # GitHub settings
    github_token: str = Field("", description="GitHub Personal Access Token")
    github_repo: str = Field("", description="Repository in format owner/repo")

    # LLM settings
    openai_api_key: str | None = Field(None, description="OpenAI API key")
    openai_model: str = Field("gpt-4o-mini", description="OpenAI model to use")
    openai_base_url: str | None = Field(None, description="Custom OpenAI API base URL")

    yandex_api_key: str | None = Field(None, description="Yandex GPT API key")
    yandex_folder_id: str | None = Field(None, description="Yandex Cloud folder ID")

    # LLM provider selection
    llm_provider: str = Field("openai", description="LLM provider: openai or yandex")

    # Agent settings
    max_iterations: int = Field(5, description="Maximum number of fix iterations")
    agent_branch_prefix: str = Field("agent/", description="Prefix for agent branches")

    # Logging
    log_level: str = Field("INFO", description="Logging level")

    # Review settings
    enable_code_review: bool = Field(True, description="Enable AI code review")
    enable_ci_analysis: bool = Field(True, description="Enable CI/CD analysis")


# Global settings instance
settings = Settings()

