"""Tests for CLI display formatting."""

from io import StringIO

from rich.console import Console

from linkedin_poster.cli.display import (
    display_post_pair,
    display_posts_table,
    display_help,
    display_welcome,
    display_saved,
    display_error,
    display_new_session,
)
import linkedin_poster.cli.display as display_mod


def _capture_output(func, *args, **kwargs) -> str:
    """Run a display function with a recording console and return output."""
    original = display_mod.console
    buf = StringIO()
    display_mod.console = Console(file=buf, force_terminal=True, width=120, highlight=False)
    try:
        func(*args, **kwargs)
    finally:
        display_mod.console = original
    return buf.getvalue()


def test_display_post_pair_contains_dividers():
    output = _capture_output(
        display_post_pair,
        en_text="Hello world",
        pt_text="Ola mundo",
        en_passed=True,
        pt_passed=True,
    )
    assert "ENGLISH" in output
    assert "PORTUGUES" in output
    assert "Hello world" in output
    assert "Ola mundo" in output


def test_display_post_pair_shows_warning_on_failure():
    output = _capture_output(
        display_post_pair,
        en_text="Hello",
        pt_text="Ola",
        en_passed=False,
        pt_passed=True,
    )
    assert "Warning" in output


def test_display_post_pair_shows_warning_on_pt_failure():
    output = _capture_output(
        display_post_pair,
        en_text="Hello",
        pt_text="Ola",
        en_passed=True,
        pt_passed=False,
    )
    assert "Warning" in output


def test_display_posts_table_empty():
    output = _capture_output(display_posts_table, entries=[])
    assert "No posts saved" in output


def test_display_posts_table_with_entries():
    entries = [
        {"date": "2026-03-20", "topic": "AI trends", "format": "short", "file_path": "posts/ai.md"},
        {"date": "2026-03-19", "topic": "RAG tips", "format": "carousel", "file_path": "posts/rag.md"},
    ]
    output = _capture_output(display_posts_table, entries=entries)
    assert "AI trends" in output
    assert "RAG tips" in output


def test_display_help_shows_commands():
    output = _capture_output(display_help)
    assert "/new" in output
    assert "/save" in output
    assert "/list" in output
    assert "/help" in output
    assert "/quit" in output


def test_display_welcome():
    output = _capture_output(display_welcome)
    assert "LinkedIn Copywriter" in output


def test_display_saved():
    output = _capture_output(display_saved, file_path="posts/2026-03/ai.md")
    assert "posts/2026-03/ai.md" in output


def test_display_error():
    output = _capture_output(display_error, message="Something went wrong")
    assert "Something went wrong" in output


def test_display_new_session():
    output = _capture_output(display_new_session, format_key="carousel")
    assert "carousel" in output
    assert "New session" in output
