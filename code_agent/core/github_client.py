"""GitHub client for Code Agent."""

import os
from typing import Any

import git
from github import Github
from github.Issue import Issue
from github.PullRequest import PullRequest
from github.Repository import Repository

from code_agent.config import settings


class GitHubClient:
    """Client for GitHub operations."""

    def __init__(self, token: str | None = None, repo_name: str | None = None) -> None:
        """Initialize GitHub client."""
        self.token = token or settings.github_token
        self.repo_name = repo_name or settings.github_repo
        self.gh = Github(self.token)
        self.repo: Repository = self.gh.get_repo(self.repo_name)

    def get_issue(self, issue_number: int) -> Issue:
        """Get issue by number."""
        return self.repo.get_issue(issue_number)

    def get_issue_details(self, issue_number: int) -> dict[str, Any]:
        """Get detailed issue information."""
        issue = self.get_issue(issue_number)
        return {
            "number": issue.number,
            "title": issue.title,
            "body": issue.body or "",
            "state": issue.state,
            "labels": [label.name for label in issue.labels],
            "assignees": [assignee.login for assignee in issue.assignees],
            "created_at": issue.created_at.isoformat(),
            "updated_at": issue.updated_at.isoformat(),
        }

    def create_pull_request(
        self,
        title: str,
        body: str,
        head: str,
        base: str = "main",
    ) -> PullRequest:
        """Create a pull request."""
        return self.repo.create_pull(title=title, body=body, head=head, base=base)

    def get_pull_request(self, pr_number: int) -> PullRequest:
        """Get pull request by number."""
        return self.repo.get_pull(pr_number)

    def add_comment_to_pr(self, pr_number: int, comment: str) -> None:
        """Add a comment to a pull request."""
        pr = self.get_pull_request(pr_number)
        pr.create_issue_comment(comment)

    def get_pr_diff(self, pr_number: int) -> str:
        """Get pull request diff."""
        pr = self.get_pull_request(pr_number)
        files = pr.get_files()

        diff_text = ""
        for file in files:
            diff_text += f"\n{'='*80}\n"
            diff_text += f"File: {file.filename}\n"
            diff_text += f"Status: {file.status}\n"
            diff_text += f"Changes: +{file.additions} -{file.deletions}\n"
            diff_text += f"{'='*80}\n"
            if file.patch:
                diff_text += file.patch + "\n"

        return diff_text

    def get_pr_checks(self, pr_number: int) -> list[dict[str, Any]]:
        """Get CI/CD check results for a PR."""
        pr = self.get_pull_request(pr_number)
        commit = pr.get_commits().reversed[0]

        check_runs = commit.get_check_runs()
        checks = []

        for check in check_runs:
            checks.append({
                "name": check.name,
                "status": check.status,
                "conclusion": check.conclusion,
                "output": check.output.summary if check.output else None,
            })

        return checks

    def create_review(
        self,
        pr_number: int,
        body: str,
        event: str = "COMMENT",
        comments: list[dict[str, Any]] | None = None,
    ) -> None:
        """Create a review on a pull request."""
        pr = self.get_pull_request(pr_number)

        if comments:
            # Create review with inline comments
            commit = pr.get_commits().reversed[0]
            pr.create_review(
                commit=commit,
                body=body,
                event=event,
                comments=comments,  # type: ignore
            )
        else:
            # Create simple review
            pr.create_review(body=body, event=event)

    def update_issue_labels(self, issue_number: int, labels: list[str]) -> None:
        """Update issue labels."""
        issue = self.get_issue(issue_number)
        issue.set_labels(*labels)

    def close_pull_request(self, pr_number: int) -> None:
        """Close a pull request."""
        pr = self.get_pull_request(pr_number)
        pr.edit(state="closed")


class GitRepo:
    """Git repository operations."""

    def __init__(self, repo_path: str) -> None:
        """Initialize Git repository."""
        self.repo_path = repo_path

        if os.path.exists(repo_path):
            self.repo = git.Repo(repo_path)
        else:
            raise ValueError(f"Repository path does not exist: {repo_path}")

    def create_branch(self, branch_name: str, base_branch: str = "main") -> None:
        """Create a new branch."""
        self.repo.git.checkout(base_branch)
        self.repo.git.pull()

        # Delete branch if it exists
        try:
            self.repo.git.branch("-D", branch_name)
        except git.GitCommandError:
            pass

        self.repo.git.checkout("-b", branch_name)

    def commit_changes(self, message: str, files: list[str] | None = None) -> None:
        """Commit changes to the repository."""
        if files:
            self.repo.index.add(files)
        else:
            self.repo.git.add(A=True)

        self.repo.index.commit(message)

    def push_branch(self, branch_name: str) -> None:
        """Push branch to remote."""
        origin = self.repo.remote(name="origin")
        origin.push(branch_name, force=True)

    def get_file_content(self, file_path: str) -> str:
        """Get file content from repository."""
        full_path = os.path.join(self.repo_path, file_path)

        if not os.path.exists(full_path):
            return ""

        with open(full_path, encoding="utf-8") as f:
            return f.read()

    def write_file(self, file_path: str, content: str) -> None:
        """Write content to file in repository."""
        full_path = os.path.join(self.repo_path, file_path)

        # Create directories if needed
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

    def get_repo_structure(self, max_depth: int = 3) -> str:
        """Get repository structure as a string."""
        structure = []

        for root, dirs, files in os.walk(self.repo_path):
            # Skip hidden and common non-source directories
            dirs[:] = [
                d for d in dirs
                if not d.startswith(".") and d not in ["node_modules", "__pycache__", "venv"]
            ]

            level = root.replace(self.repo_path, "").count(os.sep)
            if level > max_depth:
                continue

            indent = " " * 2 * level
            structure.append(f"{indent}{os.path.basename(root)}/")

            sub_indent = " " * 2 * (level + 1)
            for file in files:
                if not file.startswith("."):
                    structure.append(f"{sub_indent}{file}")

        return "\n".join(structure)

