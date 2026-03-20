"""Emoji detection and retry logic for post validation."""
from typing import Callable, Tuple

import emoji


def contains_emoji(text: str) -> bool:
    """Return True if text contains any emoji character."""
    return emoji.replace_emoji(text, replace="") != text


def validate_post(
    text: str,
    regenerate_fn: Callable[[], str],
    max_retries: int = 2,
) -> Tuple[str, bool]:
    """Validate post text for emoji violations. Returns (text, passed).

    If emoji detected, calls regenerate_fn up to max_retries times.
    If all retries fail, returns the last attempt with passed=False.
    """
    if not contains_emoji(text):
        return text, True

    for _ in range(max_retries):
        text = regenerate_fn()
        if not contains_emoji(text):
            return text, True

    return text, False
