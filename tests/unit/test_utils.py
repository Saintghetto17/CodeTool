"""Tests for utility functions."""

import logging

from code_agent.utils.logger import setup_logger


def test_setup_logger_basic() -> None:
    """Test basic logger setup."""
    logger = setup_logger("test_logger")
    assert logger is not None
    assert logger.name == "test_logger"
    assert isinstance(logger, logging.Logger)


def test_setup_logger_level() -> None:
    """Test logger level setting."""
    logger = setup_logger("test_logger_level", level="DEBUG")
    assert logger.level == logging.DEBUG

    logger2 = setup_logger("test_logger_info", level="INFO")
    assert logger2.level == logging.INFO


def test_logger_has_handlers() -> None:
    """Test that logger has at least one handler."""
    logger = setup_logger("test_logger_handlers")
    assert len(logger.handlers) > 0

