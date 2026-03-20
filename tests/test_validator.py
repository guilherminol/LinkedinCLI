"""Tests for emoji detection and retry logic -- TDD RED phase for Task 2."""
from unittest.mock import MagicMock
from linkedin_poster.generation.validator import contains_emoji, validate_post


def test_no_emoji_in_plain_text():
    assert contains_emoji("Hello world") is False


def test_detects_rocket_emoji():
    assert contains_emoji("Launch \U0001f680") is True


def test_detects_skin_tone_modifier():
    assert contains_emoji("Thumbs \U0001f44d\U0001f3fd") is True


def test_no_false_positive_on_portuguese():
    assert contains_emoji("Termos como fine-tuning e benchmark") is False


def test_validate_clean_post():
    regenerate_fn = MagicMock()
    text, passed = validate_post("Clean post without emojis.", regenerate_fn)
    assert text == "Clean post without emojis."
    assert passed is True
    regenerate_fn.assert_not_called()


def test_validate_retries_on_emoji():
    regenerate_fn = MagicMock(side_effect=[
        "Still has emoji \U0001f680",
        "Still has emoji \U0001f525",
    ])
    text, passed = validate_post("Bad post \U0001f680", regenerate_fn)
    assert passed is False
    assert regenerate_fn.call_count == 2


def test_validate_succeeds_on_retry():
    regenerate_fn = MagicMock(return_value="Clean text after retry")
    text, passed = validate_post("Bad post \U0001f680", regenerate_fn)
    assert text == "Clean text after retry"
    assert passed is True
    assert regenerate_fn.call_count == 1
