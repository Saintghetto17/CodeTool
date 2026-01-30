"""Tests for agent modules."""

from unittest.mock import Mock, patch

from code_agent.agents.code_agent import CodeAgent
from code_agent.agents.reviewer_agent import ReviewerAgent


def test_reviewer_agent_initialization() -> None:
    """Test ReviewerAgent initialization with mocks."""
    mock_github = Mock()
    mock_llm = Mock()

    agent = ReviewerAgent(github_client=mock_github, llm_service=mock_llm)

    assert agent.github_client == mock_github
    assert agent.llm_service == mock_llm


def test_reviewer_agent_has_review_pull_request_method() -> None:
    """Test that ReviewerAgent has review_pull_request method."""
    mock_github = Mock()
    mock_llm = Mock()

    agent = ReviewerAgent(github_client=mock_github, llm_service=mock_llm)

    assert hasattr(agent, "review_pull_request")
    assert callable(agent.review_pull_request)


@patch("code_agent.agents.code_agent.GitRepo")
def test_code_agent_initialization(mock_git_repo: Mock) -> None:
    """Test CodeAgent initialization with mocks."""
    mock_github = Mock()
    mock_llm = Mock()

    agent = CodeAgent(github_client=mock_github, llm_service=mock_llm)

    assert agent.github_client == mock_github
    assert agent.llm_service == mock_llm


@patch("code_agent.agents.code_agent.GitRepo")
def test_code_agent_has_process_issue_method(mock_git_repo: Mock) -> None:
    """Test that CodeAgent has process_issue method."""
    mock_github = Mock()
    mock_llm = Mock()

    agent = CodeAgent(github_client=mock_github, llm_service=mock_llm)

    assert hasattr(agent, "process_issue")
    assert callable(agent.process_issue)

