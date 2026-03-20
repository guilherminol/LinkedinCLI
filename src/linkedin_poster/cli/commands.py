"""Command parsing and dispatch for the CLI REPL."""

from typing import Optional, Tuple

from linkedin_poster.generation.prompts import FORMAT_INSTRUCTIONS

# Valid commands
COMMANDS = {"/new", "/save", "/list", "/help", "/quit"}


def parse_input(raw: str) -> Tuple[str, Optional[str]]:
    """Parse user input into (command_or_text, argument).

    Returns:
        - ("/command", arg_or_none) if input starts with /
        - ("topic", None) if input is natural language
    """
    stripped = raw.strip()
    if not stripped:
        return ("", None)

    if stripped.startswith("/"):
        parts = stripped.split(None, 1)
        command = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else None
        return (command, arg)

    return ("topic", None)


def parse_format(arg: Optional[str]) -> str:
    """Parse format argument for /new command. Returns validated format key.

    Valid formats: short, carousel, hook. Default: short.
    """
    if arg is None:
        return "short"
    fmt = arg.strip().lower()
    if fmt in FORMAT_INSTRUCTIONS:
        return fmt
    return "short"
