"""Rich formatting for post display, spinners, and CLI output."""

from contextlib import contextmanager
from typing import List, Dict

from rich.console import Console
from rich.table import Table

console = Console()


def display_post_pair(en_text: str, pt_text: str, en_passed: bool, pt_passed: bool):
    """Display EN and PT posts with labeled dividers.

    Uses rich rules as dividers:
    -- ENGLISH --
    [post text]
    -- PORTUGUES --
    [post text]

    If validation failed, shows warning before the post.
    """
    console.print()
    console.rule("[bold blue]ENGLISH[/bold blue]")
    if not en_passed:
        console.print(
            "[yellow]Warning: Failed to generate clean post after 2 retries"
            " -- showing last attempt[/yellow]"
        )
    console.print(en_text)
    console.print()
    console.rule("[bold green]PORTUGUES[/bold green]")
    if not pt_passed:
        console.print(
            "[yellow]Warning: Failed to generate clean post after 2 retries"
            " -- showing last attempt[/yellow]"
        )
    console.print(pt_text)
    console.print()


def display_posts_table(entries: List[Dict[str, str]]):
    """Display saved posts as a rich table."""
    if not entries:
        console.print("[yellow]No posts saved yet.[/yellow]")
        return

    table = Table(title="Saved Posts")
    table.add_column("Date", style="cyan")
    table.add_column("Topic", style="white")
    table.add_column("Format", style="green")
    table.add_column("File", style="dim")

    for entry in entries:
        table.add_row(entry["date"], entry["topic"], entry["format"], entry["file_path"])

    console.print(table)


@contextmanager
def generation_spinner():
    """Context manager for generation progress spinner.

    Usage:
        with generation_spinner() as status:
            status.update("Generating EN post...")
            # ... generate EN ...
            status.update("Generating PT post...")
            # ... generate PT ...
    """
    with console.status("Generating EN post...", spinner="dots") as status:
        yield status


def display_welcome():
    """Show brief welcome message at session start."""
    console.print("[bold]LinkedIn Copywriter[/bold] -- type a topic or /help")
    console.print()


def display_help():
    """Show available commands."""
    help_text = (
        "[bold]Commands:[/bold]\n"
        "  /new [format]    Start a new post (formats: short, carousel, hook)."
        " Default: short\n"
        "  /save            Save the current post pair to disk\n"
        "  /list            List previously saved posts\n"
        "  /help            Show this help message\n"
        "  /quit            Exit the session\n"
        "\n"
        "[bold]Usage:[/bold]\n"
        "  Type a topic to generate a post pair (EN + PT)\n"
        "  Type a refinement instruction to update the current post\n"
    )
    console.print(help_text)


def display_saved(file_path: str):
    """Confirm post was saved."""
    console.print(f"[green]Post saved to: {file_path}[/green]")


def display_error(message: str):
    """Show error message."""
    console.print(f"[red]Error: {message}[/red]")


def display_new_session(format_key: str):
    """Confirm new session started."""
    console.print(f"[cyan]New session started (format: {format_key}). Type a topic.[/cyan]")
