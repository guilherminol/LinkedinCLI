"""Tests for the REPL session loop."""

from dataclasses import dataclass
from unittest.mock import MagicMock, patch
from pathlib import Path

from linkedin_poster.cli.repl import Session
from linkedin_poster.generation.client import GenerationResult


def _make_result(**overrides):
    """Create a GenerationResult with sensible defaults."""
    defaults = {
        "en_text": "EN post text",
        "pt_text": "PT post text",
        "topic": "AI trends",
        "format_key": "short",
        "en_passed": True,
        "pt_passed": True,
    }
    defaults.update(overrides)
    return GenerationResult(**defaults)


def _make_session():
    """Create a Session with a mocked generator."""
    gen = MagicMock()
    gen.generate_pair.return_value = _make_result()
    gen.refine.return_value = _make_result(en_text="Refined EN", pt_text="Refined PT")
    session = Session(generator=gen)
    return session, gen


def test_session_init():
    gen = MagicMock()
    session = Session(generator=gen)
    assert session.generator is gen
    assert session.current_format == "short"
    assert session.current_result is None


def test_handle_new_resets():
    session, gen = _make_session()
    session.current_result = _make_result()
    session._handle_new("carousel")
    assert session.current_format == "carousel"
    assert session.current_result is None
    gen.reset.assert_called_once()


def test_handle_new_default_format():
    session, gen = _make_session()
    session._handle_new(None)
    assert session.current_format == "short"


def test_handle_topic_generates():
    session, gen = _make_session()
    with patch("linkedin_poster.cli.repl.generation_spinner") as mock_spinner:
        mock_spinner.return_value.__enter__ = MagicMock(return_value=MagicMock())
        mock_spinner.return_value.__exit__ = MagicMock(return_value=False)
        with patch("linkedin_poster.cli.repl.display_post_pair"):
            session._handle_topic_or_refinement("AI trends")

    assert session.current_result is not None
    gen.generate_pair.assert_called_once_with("AI trends", "short")


def test_handle_refinement():
    session, gen = _make_session()
    session.current_result = _make_result()

    with patch("linkedin_poster.cli.repl.generation_spinner") as mock_spinner:
        mock_spinner.return_value.__enter__ = MagicMock(return_value=MagicMock())
        mock_spinner.return_value.__exit__ = MagicMock(return_value=False)
        with patch("linkedin_poster.cli.repl.display_post_pair"):
            session._handle_topic_or_refinement("shorter")

    gen.refine.assert_called_once_with("shorter")


def test_handle_save_no_post():
    session, gen = _make_session()
    # Should not crash when no post exists
    with patch("linkedin_poster.cli.repl.display_error") as mock_err:
        session._handle_save()
    mock_err.assert_called_once()
    assert "No post" in mock_err.call_args[0][0]


def test_handle_save_with_post():
    session, gen = _make_session()
    session.current_result = _make_result(topic="AI trends", format_key="short")

    with patch("linkedin_poster.cli.repl.save_post", return_value=Path("posts/ai.md")) as mock_save:
        with patch("linkedin_poster.cli.repl.display_saved") as mock_display:
            session._handle_save()

    mock_save.assert_called_once_with(
        topic="AI trends",
        en_text="EN post text",
        pt_text="PT post text",
        format_type="short",
    )
    mock_display.assert_called_once()


def test_handle_list():
    session, gen = _make_session()
    entries = [{"date": "2026-03-20", "topic": "AI", "format": "short", "file_path": "x.md"}]

    with patch("linkedin_poster.cli.repl.list_posts", return_value=entries) as mock_list:
        with patch("linkedin_poster.cli.repl.display_posts_table") as mock_display:
            session._handle_list()

    mock_list.assert_called_once()
    mock_display.assert_called_once_with(entries)
