"""Tests for configuration module."""

from code_agent.config import Settings


def test_settings_default_values() -> None:
    """Test default settings values."""
    # This will fail without proper env vars, but shows the structure
    assert Settings.model_fields["openai_model"].default == "gpt-4o-mini"
    assert Settings.model_fields["max_iterations"].default == 5
    assert Settings.model_fields["llm_provider"].default == "openai"


def test_settings_validation() -> None:
    """Test settings validation."""
    # Test with minimal required fields
    settings = Settings(
        github_token="test_token",
        github_repo="owner/repo",
    )
    assert settings.github_token == "test_token"
    assert settings.github_repo == "owner/repo"
    assert settings.max_iterations == 5

