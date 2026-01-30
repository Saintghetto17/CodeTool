# Changelog

All notable changes to Code Agent will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-29

### Added
- Initial release of Code Agent
- Code Agent CLI for processing GitHub Issues
- AI Reviewer Agent for automated code review
- Support for OpenAI GPT-4o-mini
- Support for YandexGPT
- GitHub Actions workflows:
  - Issue Handler (automatic PR creation)
  - PR Review (CI checks + AI review)
  - CI Pipeline
- Iterative fix mechanism (up to configurable max iterations)
- Docker and Docker Compose support
- Comprehensive documentation:
  - Installation guide
  - Architecture documentation
  - Usage examples
  - Contributing guidelines
- Test suite with unit and integration tests
- Code quality tools integration (ruff, black, mypy, pytest)
- Configuration management with Pydantic Settings
- Rich CLI interface with colored output
- Detailed logging system

### Features
- **Code Agent**:
  - Automatic issue analysis
  - Code generation using LLM
  - Git branch management
  - Pull request creation
  - Iterative fixes based on review feedback

- **Reviewer Agent**:
  - Automated code review
  - CI/CD results analysis
  - Review posting to GitHub PR
  - Approval/request changes decision making

- **LLM Integration**:
  - Multiple provider support (OpenAI, YandexGPT)
  - Customizable prompts via YAML
  - Context-aware code generation

- **GitHub Integration**:
  - Issue management
  - Pull request operations
  - CI checks analysis
  - Comment and review posting

### Technical Details
- Python 3.11+ support
- Type hints throughout codebase
- Pydantic for configuration validation
- GitPython for git operations
- PyGithub for GitHub API
- Typer for CLI
- Rich for terminal formatting
- pytest for testing
- Docker containerization

### Documentation
- Comprehensive README with quick start
- Detailed installation instructions
- Architecture documentation
- Usage examples
- Contributing guidelines
- API documentation via docstrings

### CI/CD
- Automated linting (ruff, black)
- Type checking (mypy)
- Test execution (pytest)
- Docker image building
- GitHub Actions integration

## [Unreleased]

### Planned
- Webhook server for real-time processing
- Database for metrics and history
- Web dashboard for monitoring
- Multi-repository support
- Advanced prompt templates with few-shot examples
- Code search integration
- LLM response caching
- Streaming LLM responses
- Fine-tuned models support

---

For more details, see [GitHub Releases](https://github.com/your-username/code-agent/releases)

