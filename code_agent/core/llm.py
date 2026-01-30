"""LLM integration for Code Agent."""

from abc import ABC, abstractmethod
from typing import Any

import httpx
from openai import OpenAI

from code_agent.config import settings


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> str:
        """Generate text from messages."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider."""

    def __init__(self) -> None:
        """Initialize OpenAI provider."""
        self.client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )
        self.model = settings.openai_model

    def generate(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> str:
        """Generate text using OpenAI API."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,  # type: ignore
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""


class YandexGPTProvider(LLMProvider):
    """Yandex GPT provider."""

    def __init__(self) -> None:
        """Initialize Yandex GPT provider."""
        self.api_key = settings.yandex_api_key
        self.folder_id = settings.yandex_folder_id
        self.base_url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

    def generate(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> str:
        """Generate text using Yandex GPT API."""
        headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "Content-Type": "application/json",
        }

        payload: dict[str, Any] = {
            "modelUri": f"gpt://{self.folder_id}/yandexgpt-lite",
            "completionOptions": {
                "temperature": temperature,
                "maxTokens": max_tokens or 2000,
            },
            "messages": messages,
        }

        with httpx.Client() as client:
            response = client.post(self.base_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result["result"]["alternatives"][0]["message"]["text"]


def get_llm_provider() -> LLMProvider:
    """Get LLM provider based on configuration."""
    if settings.llm_provider == "yandex":
        return YandexGPTProvider()
    return OpenAIProvider()


class LLMService:
    """Service for LLM operations."""

    def __init__(self, provider: LLMProvider | None = None) -> None:
        """Initialize LLM service."""
        self.provider = provider or get_llm_provider()

    def generate_code_changes(
        self, issue_description: str, current_code: str, file_path: str
    ) -> str:
        """Generate code changes based on issue description."""
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert software developer. Your task is to analyze "
                    "the issue description and current code, then provide the updated "
                    "code that solves the issue. Return ONLY the complete updated code "
                    "without explanations."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Issue Description:\n{issue_description}\n\n"
                    f"File: {file_path}\n\n"
                    f"Current Code:\n{current_code}\n\n"
                    f"Please provide the updated code that solves this issue."
                ),
            },
        ]
        return self.provider.generate(messages, temperature=0.3)

    def analyze_issue(self, issue_description: str, repo_structure: str) -> dict[str, Any]:
        """Analyze issue and determine what files need to be changed."""
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert software architect. Analyze the issue and "
                    "determine which files need to be created or modified. "
                    "Respond in a structured format with file paths and actions."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Issue Description:\n{issue_description}\n\n"
                    f"Repository Structure:\n{repo_structure}\n\n"
                    "Please analyze what needs to be done and which files to modify."
                ),
            },
        ]
        response = self.provider.generate(messages, temperature=0.5)
        # Parse response and return structured data
        return {"analysis": response, "files_to_modify": []}

    def review_code_changes(
        self, diff: str, issue_description: str, ci_results: str | None = None
    ) -> dict[str, Any]:
        """Review code changes and provide feedback."""
        ci_context = f"\n\nCI/CD Results:\n{ci_results}" if ci_results else ""

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert code reviewer. Review the code changes and "
                    "provide constructive feedback. Check for: correctness, code quality, "
                    "potential bugs, security issues, and whether it solves the issue. "
                    "Return a JSON object with: approved (bool), feedback (str), "
                    "issues (list of strings)."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Issue Description:\n{issue_description}\n\n"
                    f"Code Changes (diff):\n{diff}{ci_context}\n\n"
                    "Please review these changes."
                ),
            },
        ]
        response = self.provider.generate(messages, temperature=0.3)

        # Parse response (simplified - in production, use JSON parsing)
        return {
            "approved": "approved" in response.lower() and "not approved" not in response.lower(),
            "feedback": response,
            "issues": [],
        }

