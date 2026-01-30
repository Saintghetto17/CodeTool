"""CLI interface for Code Agent."""

import logging
import sys

import typer
from rich.console import Console
from rich.logging import RichHandler

from code_agent import __version__
from code_agent.agents.code_agent import CodeAgent
from code_agent.agents.reviewer_agent import ReviewerAgent
from code_agent.config import settings

# Initialize Typer app
app = typer.Typer(
    name="code-agent",
    help="Automated SDLC Agent System for GitHub",
    add_completion=False,
)

console = Console()


def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, console=console)],
    )


@app.command()
def version() -> None:
    """Show version information."""
    console.print(f"Code Agent version: {__version__}")


@app.command()
def process_issue(
    issue_number: int = typer.Argument(..., help="GitHub issue number to process"),
    repo_path: str | None = typer.Option(
        None, "--repo-path", "-r", help="Path to local repository"
    ),
    log_level: str = typer.Option(
        settings.log_level, "--log-level", "-l", help="Logging level"
    ),
) -> None:
    """Process a GitHub issue and create a pull request."""
    setup_logging(log_level)

    console.print(f"[bold blue]Processing issue #{issue_number}...[/bold blue]")

    try:
        agent = CodeAgent(repo_path=repo_path)
        result = agent.process_issue(issue_number)

        if result.get("success"):
            if result.get("demo_mode"):
                console.print("[bold yellow]⚠[/bold yellow] DEMO_MODE: PR was not created on GitHub (permissions).")
                if result.get("diff_path"):
                    console.print(f"  Local diff: {result['diff_path']}")
                if result.get("pr_url"):
                    console.print(f"  PR: {result['pr_url']}")
            else:
                console.print("[bold green]✓[/bold green] Successfully created pull request!")
                console.print(f"  PR Number: #{result['pr_number']}")
            console.print(f"  Branch: {result['branch']}")
            console.print(f"  Files Modified: {len(result['files_modified'])}")
        else:
            console.print(f"[bold red]✗[/bold red] Failed: {result.get('error')}")
            sys.exit(1)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        # Avoid scary tracebacks in demos; still keep details when DEBUG is enabled.
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            logging.exception("Failed to process issue")
        else:
            logging.error("Failed to process issue: %s", e)
        sys.exit(1)


@app.command()
def review_pr(
    pr_number: int = typer.Argument(..., help="Pull request number to review"),
    repo_path: str | None = typer.Option(
        None, "--repo-path", "-r", help="Path to local repository (used for DEMO_MODE artifacts)"
    ),
    log_level: str = typer.Option(
        settings.log_level, "--log-level", "-l", help="Logging level"
    ),
) -> None:
    """Review a pull request and provide feedback."""
    setup_logging(log_level)

    console.print(f"[bold blue]Reviewing PR #{pr_number}...[/bold blue]")

    try:
        agent = ReviewerAgent(repo_path=repo_path)
        result = agent.review_pull_request(pr_number)

        if result.get("approved"):
            console.print("[bold green]✓[/bold green] PR Approved!")
        else:
            console.print("[bold yellow]⚠[/bold yellow] Changes Requested")

        console.print("\n[bold]Feedback:[/bold]")
        console.print(result.get("feedback", "No feedback provided"))

        issues = result.get("issues", [])
        if issues:
            console.print("\n[bold]Issues:[/bold]")
            for i, issue in enumerate(issues, 1):
                console.print(f"  {i}. {issue}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            logging.exception("Failed to review PR")
        else:
            logging.error("Failed to review PR: %s", e)
        sys.exit(1)


@app.command()
def fix_pr(
    pr_number: int = typer.Argument(..., help="Pull request number to fix"),
    feedback: str = typer.Option(
        ..., "--feedback", "-f", help="Feedback from review to address"
    ),
    iteration: int = typer.Option(1, "--iteration", "-i", help="Iteration number"),
    repo_path: str | None = typer.Option(
        None, "--repo-path", "-r", help="Path to local repository"
    ),
    log_level: str = typer.Option(
        settings.log_level, "--log-level", "-l", help="Logging level"
    ),
) -> None:
    """Fix issues in a pull request based on review feedback."""
    setup_logging(log_level)

    console.print(f"[bold blue]Fixing PR #{pr_number} (iteration {iteration})...[/bold blue]")

    try:
        agent = CodeAgent(repo_path=repo_path)
        result = agent.fix_pr_issues(pr_number, feedback, iteration)

        if result.get("success"):
            console.print("[bold green]✓[/bold green] Successfully fixed PR!")
            console.print(f"  Files Modified: {len(result['files_modified'])}")
        else:
            console.print(f"[bold red]✗[/bold red] Failed: {result.get('error')}")
            sys.exit(1)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            logging.exception("Failed to fix PR")
        else:
            logging.error("Failed to fix PR: %s", e)
        sys.exit(1)


@app.command()
def generate_summary(
    pr_number: int = typer.Argument(..., help="Pull request number"),
    repo_path: str | None = typer.Option(
        None, "--repo-path", "-r", help="Path to local repository (used for DEMO_MODE artifacts)"
    ),
    log_level: str = typer.Option(
        settings.log_level, "--log-level", "-l", help="Logging level"
    ),
) -> None:
    """Generate a review summary for GitHub Actions."""
    setup_logging(log_level)

    try:
        agent = ReviewerAgent(repo_path=repo_path)
        summary = agent.generate_review_summary(pr_number)

        # Print summary to stdout (can be captured by GitHub Actions)
        print(summary)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            logging.exception("Failed to generate summary")
        else:
            logging.error("Failed to generate summary: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    app()

