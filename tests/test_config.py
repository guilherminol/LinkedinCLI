"""Tests for project config and imports -- TDD RED phase for Task 1."""
from pathlib import Path


def test_import_linkedin_poster():
    """Importing linkedin_poster succeeds without error."""
    import linkedin_poster  # noqa: F401


def test_anthropic_model_value():
    """config.ANTHROPIC_MODEL equals expected model string."""
    from linkedin_poster.config import ANTHROPIC_MODEL
    assert ANTHROPIC_MODEL == "claude-sonnet-4-20250514"


def test_posts_dir_value():
    """config.POSTS_DIR equals Path('posts')."""
    from linkedin_poster.config import POSTS_DIR
    assert POSTS_DIR == Path("posts")


def test_max_retries_value():
    """config.MAX_RETRIES equals 2."""
    from linkedin_poster.config import MAX_RETRIES
    assert MAX_RETRIES == 2
