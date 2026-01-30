"""Code Agent - analyzes issues and creates pull requests."""

import json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from code_agent.config import settings
from code_agent.core.github_client import GitHubClient, GitRepo
from code_agent.core.llm import LLMService

logger = logging.getLogger(__name__)


class CodeAgent:
    """Agent that reads issues, modifies code, and creates pull requests."""

    def __init__(
        self,
        github_client: GitHubClient | None = None,
        llm_service: LLMService | None = None,
        repo_path: str | None = None,
    ) -> None:
        """Initialize Code Agent."""
        self.github_client = github_client or GitHubClient()
        self.llm_service = llm_service or LLMService()
        self.repo_path = repo_path or os.getcwd()
        self.git_repo = GitRepo(self.repo_path)

    def process_issue(self, issue_number: int) -> dict[str, Any]:
        """Process an issue and create a pull request."""
        logger.info(f"Processing issue #{issue_number}")

        # Get issue details
        issue_details = self.github_client.get_issue_details(issue_number)
        issue_description = f"{issue_details['title']}\n\n{issue_details['body']}"

        logger.info(f"Issue: {issue_details['title']}")

        # Analyze issue and determine what needs to be done
        repo_structure = self.git_repo.get_repo_structure()
        analysis = self.llm_service.analyze_issue(issue_description, repo_structure)

        logger.info(f"Analysis: {analysis['analysis'][:200]}...")

        # Create branch
        base_branch = "main"
        branch_name = f"{settings.agent_branch_prefix}issue-{issue_number}"
        try:
            self.git_repo.create_branch(branch_name, base_branch=base_branch)
            logger.info(f"Created branch: {branch_name}")
        except Exception as e:
            msg = f"git create_branch failed: {type(e).__name__}: {e}"
            if settings.demo_mode:
                logger.warning("DEMO_MODE enabled: %s. Continuing on current branch.", msg)
            else:
                logger.error(msg)
                return {"success": False, "error": msg}

        # Identify and modify files
        files_modified = self._modify_files(issue_description, analysis)

        if not files_modified:
            logger.warning("No files were modified")
            return {
                "success": False,
                "error": "No changes were made",
            }

        # Commit changes
        commit_message = f"Fix #{issue_number}: {issue_details['title']}"
        try:
            self.git_repo.commit_changes(commit_message, files_modified)
            logger.info(f"Committed changes: {len(files_modified)} files")
        except Exception as e:
            msg = f"git commit failed: {type(e).__name__}: {e}"
            if settings.demo_mode:
                logger.warning("DEMO_MODE enabled: %s. Will continue with uncommitted diff.", msg)
            else:
                logger.error(msg)
                return {"success": False, "error": msg}

        # Push branch
        try:
            self.git_repo.push_branch(branch_name)
            logger.info(f"Pushed branch: {branch_name}")
        except Exception as e:
            if not settings.demo_mode:
                msg = f"git push failed: {type(e).__name__}: {e}"
                logger.error(msg)
                return {"success": False, "error": msg}

            # Demo fallback: save diff + metadata and return a pseudo PR result.
            demo_dir = Path(self.repo_path) / ".code_agent_demo"
            demo_dir.mkdir(parents=True, exist_ok=True)
            diff_path = demo_dir / f"issue-{issue_number}.diff"
            last_run_path = demo_dir / "last_run.json"

            diff = ""
            try:
                diff = self.git_repo.repo.git.diff(f"{base_branch}...HEAD")
            except Exception as diff_err:
                diff = f"# Failed to compute git diff: {type(diff_err).__name__}: {diff_err}\n"
            diff_path.write_text(diff, encoding="utf-8")

            pr_title = f"Fix #{issue_number}: {issue_details['title']}"
            pr_body = (
                f"Fixes #{issue_number}\n\n{issue_details['body']}\n\n---\n"
                "*This PR was automatically created by Code Agent.*"
            )

            # Store paths relative to the repo root to keep artifacts portable.
            repo_root = Path(self.repo_path)
            diff_rel_path = str(Path(".code_agent_demo") / diff_path.name)
            last_run = {
                "demo_mode": True,
                "timestamp": datetime.now(UTC).isoformat(),
                "repo_path": str(repo_root.resolve()),
                "issue_number": issue_number,
                "branch": branch_name,
                "base_branch": base_branch,
                "pr_title": pr_title,
                "pr_body": pr_body,
                "files_modified": files_modified,
                "diff_path": diff_rel_path,
                "push_error": f"{type(e).__name__}: {e}",
            }
            last_run_path.write_text(json.dumps(last_run, indent=2), encoding="utf-8")

            logger.warning(
                "DEMO_MODE enabled: push failed (%s). Saved diff to %s",
                last_run["push_error"],
                diff_path,
            )

            return {
                "success": True,
                "demo_mode": True,
                "issue_number": issue_number,
                "pr_number": 0,
                "pr_url": "DEMO_MODE: PR creation skipped (no push permissions)",
                "branch": branch_name,
                "files_modified": files_modified,
                "diff_path": diff_rel_path,
            }

        # Create pull request
        pr_body = f"Fixes #{issue_number}\n\n{issue_details['body']}\n\n---\n*This PR was automatically created by Code Agent.*"
        try:
            pr = self.github_client.create_pull_request(
                title=f"Fix #{issue_number}: {issue_details['title']}",
                body=pr_body,
                head=branch_name,
            )

            logger.info(f"Created PR #{pr.number}")

            return {
                "success": True,
                "issue_number": issue_number,
                "pr_number": pr.number,
                "branch": branch_name,
                "files_modified": files_modified,
            }
        except Exception as e:
            if not settings.demo_mode:
                msg = f"create PR failed: {type(e).__name__}: {e}"
                logger.error(msg)
                return {"success": False, "error": msg}

            demo_dir = Path(self.repo_path) / ".code_agent_demo"
            demo_dir.mkdir(parents=True, exist_ok=True)
            last_run_path = demo_dir / "last_run.json"

            pr_title = f"Fix #{issue_number}: {issue_details['title']}"
            repo_root = Path(self.repo_path)
            last_run = {
                "demo_mode": True,
                "timestamp": datetime.now(UTC).isoformat(),
                "repo_path": str(repo_root.resolve()),
                "issue_number": issue_number,
                "branch": branch_name,
                "base_branch": base_branch,
                "pr_title": pr_title,
                "pr_body": pr_body,
                "files_modified": files_modified,
                "pr_create_error": f"{type(e).__name__}: {e}",
            }
            last_run_path.write_text(json.dumps(last_run, indent=2), encoding="utf-8")

            logger.warning(
                "DEMO_MODE enabled: PR creation failed (%s). Returning pseudo PR result.",
                last_run["pr_create_error"],
            )

            return {
                "success": True,
                "demo_mode": True,
                "issue_number": issue_number,
                "pr_number": 0,
                "pr_url": "DEMO_MODE: PR creation failed (permissions). Showing local artifacts instead.",
                "branch": branch_name,
                "files_modified": files_modified,
            }

    def _modify_files(
        self, issue_description: str, analysis: dict[str, Any]
    ) -> list[str]:
        """Modify files based on issue description and analysis."""
        files_modified = []

        # Extract file paths from analysis (simplified)
        # In production, parse the LLM response more carefully
        analysis_text = analysis.get("analysis", "")

        # Try to identify files to modify
        # This is a simplified approach - in production, use structured LLM output
        potential_files = self._extract_file_paths(analysis_text)

        if not potential_files:
            # Fallback: try to infer from issue description
            potential_files = self._infer_files_from_issue(issue_description)

        for file_path in potential_files:
            try:
                current_content = self.git_repo.get_file_content(file_path)

                # Generate updated code
                updated_content = self.llm_service.generate_code_changes(
                    issue_description, current_content, file_path
                )

                # Clean up the response (remove markdown code blocks if present)
                updated_content = self._clean_code_response(updated_content)

                # Write updated content
                self.git_repo.write_file(file_path, updated_content)
                files_modified.append(file_path)

                logger.info(f"Modified file: {file_path}")

            except Exception as e:
                logger.error(f"Error modifying {file_path}: {e}")
                continue

        return files_modified

    def _extract_file_paths(self, text: str) -> list[str]:
        """Extract file paths from text."""
        # Simplified extraction - look for common file patterns
        import re

        patterns = [
            r"(?:file|path):\s*([^\s]+\.py)",
            r"`([^`]+\.py)`",
            r"([a-zA-Z_][a-zA-Z0-9_/]*\.py)",
        ]

        files = set()
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for m in matches:
                # Some LLM outputs include punctuation/backticks around paths.
                cleaned = m.strip().strip("`'\"").strip(",:);.")
                if cleaned.endswith(".py"):
                    files.add(cleaned)

        return list(files)

    def _infer_files_from_issue(self, issue_description: str) -> list[str]:
        """Infer which files to modify from issue description."""
        # Simple heuristic - in production, use better logic
        files = []

        text = issue_description.lower()

        # If user mentions specific files explicitly
        if "naivebayes.py" in text:
            files.append("NaiveBayes.py")
        if "cli" in text:
            files.append("cli.py")
        if "test" in text:
            files.append("test_cli.py")

        # Generic fallback for many repos
        if "main.py" in text:
            files.append("main.py")

        return files

    def _clean_code_response(self, response: str) -> str:
        """Clean LLM response to extract just the code."""
        # Remove markdown code blocks
        if "```" in response:
            # Extract content between code blocks
            parts = response.split("```")
            if len(parts) >= 3:
                code = parts[1]
                # Remove language identifier
                if code.startswith("python\n"):
                    code = code[7:]
                elif code.startswith("py\n"):
                    code = code[3:]
                return code.strip()

        return response.strip()

    def fix_pr_issues(
        self, pr_number: int, feedback: str, iteration: int = 1
    ) -> dict[str, Any]:
        """Fix issues in a PR based on reviewer feedback."""
        logger.info(f"Fixing PR #{pr_number} (iteration {iteration})")

        if iteration > settings.max_iterations:
            logger.error(f"Max iterations ({settings.max_iterations}) reached")
            return {
                "success": False,
                "error": "Max iterations reached",
            }

        # Get PR details
        pr = self.github_client.get_pull_request(pr_number)

        # Get issue number from PR body
        issue_number = self._extract_issue_number(pr.body or "")

        if not issue_number:
            logger.error("Could not extract issue number from PR")
            return {
                "success": False,
                "error": "Could not find related issue",
            }

        issue_details = self.github_client.get_issue_details(issue_number)
        issue_description = f"{issue_details['title']}\n\n{issue_details['body']}"

        # Checkout PR branch
        self.git_repo.repo.git.checkout(pr.head.ref)
        self.git_repo.repo.git.pull()

        # Get modified files
        files = pr.get_files()
        files_to_fix = [f.filename for f in files]

        files_modified = []
        for file_path in files_to_fix:
            try:
                current_content = self.git_repo.get_file_content(file_path)

                # Generate fixes with feedback context
                messages = [
                    {
                        "role": "system",
                        "content": "You are an expert software developer. Fix the code based on the review feedback.",
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Original Issue:\n{issue_description}\n\n"
                            f"Current Code ({file_path}):\n{current_content}\n\n"
                            f"Review Feedback:\n{feedback}\n\n"
                            "Please provide the fixed code."
                        ),
                    },
                ]

                updated_content = self.llm_service.provider.generate(messages, temperature=0.3)
                updated_content = self._clean_code_response(updated_content)

                self.git_repo.write_file(file_path, updated_content)
                files_modified.append(file_path)

            except Exception as e:
                logger.error(f"Error fixing {file_path}: {e}")
                continue

        if not files_modified:
            return {
                "success": False,
                "error": "No files were modified",
            }

        # Commit and push fixes
        commit_message = f"Fix PR #{pr_number} based on review (iteration {iteration})"
        self.git_repo.commit_changes(commit_message, files_modified)
        self.git_repo.push_branch(pr.head.ref)

        logger.info(f"Pushed fixes to PR #{pr_number}")

        return {
            "success": True,
            "pr_number": pr_number,
            "iteration": iteration,
            "files_modified": files_modified,
        }

    def _extract_issue_number(self, text: str) -> int | None:
        """Extract issue number from text."""
        import re

        match = re.search(r"#(\d+)", text)
        if match:
            return int(match.group(1))

        return None

