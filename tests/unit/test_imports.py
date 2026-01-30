"""Sanity tests for module imports."""


def test_import_code_agent() -> None:
    """Test that code_agent module can be imported."""
    import code_agent

    assert code_agent is not None


def test_import_agents() -> None:
    """Test that agent modules can be imported."""
    from code_agent.agents import code_agent, reviewer_agent

    assert code_agent is not None
    assert reviewer_agent is not None


def test_import_core() -> None:
    """Test that core modules can be imported."""
    from code_agent.core import github_client, llm

    assert github_client is not None
    assert llm is not None


def test_import_utils() -> None:
    """Test that utils modules can be imported."""
    from code_agent.utils import logger

    assert logger is not None


def test_import_config() -> None:
    """Test that config module can be imported."""
    from code_agent import config

    assert config is not None
    assert hasattr(config, "Settings")


def test_import_cli() -> None:
    """Test that CLI module can be imported."""
    from code_agent import cli

    assert cli is not None

