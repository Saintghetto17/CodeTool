"""Tests for LLM module."""

from unittest.mock import Mock, patch

from code_agent.core.llm import LLMService, OpenAIProvider


def test_llm_service_initialization() -> None:
    """Test LLM service initialization."""
    mock_provider = Mock()
    service = LLMService(provider=mock_provider)
    assert service.provider == mock_provider


@patch("code_agent.core.llm.OpenAI")
def test_openai_provider_generate(mock_openai: Mock) -> None:
    """Test OpenAI provider generation."""
    # Setup mock
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Test response"
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client

    # Test
    provider = OpenAIProvider()
    result = provider.generate([{"role": "user", "content": "test"}])

    assert result == "Test response"
    mock_client.chat.completions.create.assert_called_once()

