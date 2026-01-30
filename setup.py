"""Setup script for Code Agent (legacy support)."""

from setuptools import find_packages, setup

# This file is kept for backwards compatibility
# Modern configuration is in pyproject.toml

setup(
    name="code-agent",
    packages=find_packages(),
    python_requires=">=3.11",
)

