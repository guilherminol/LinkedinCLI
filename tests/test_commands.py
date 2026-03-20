"""Tests for command parsing and dispatch."""

from linkedin_poster.cli.commands import parse_input, parse_format


def test_parse_slash_command():
    assert parse_input("/save") == ("/save", None)


def test_parse_command_with_arg():
    assert parse_input("/new carousel") == ("/new", "carousel")


def test_parse_natural_language():
    assert parse_input("make it shorter") == ("topic", None)


def test_parse_slash_in_middle():
    assert parse_input("I want to /save this") == ("topic", None)


def test_parse_empty():
    assert parse_input("") == ("", None)


def test_parse_whitespace_only():
    assert parse_input("   ") == ("", None)


def test_parse_command_case_insensitive():
    assert parse_input("/SAVE") == ("/save", None)


def test_parse_format_valid():
    assert parse_format("carousel") == "carousel"


def test_parse_format_hook():
    assert parse_format("hook") == "hook"


def test_parse_format_short():
    assert parse_format("short") == "short"


def test_parse_format_invalid():
    assert parse_format("invalid") == "short"


def test_parse_format_none():
    assert parse_format(None) == "short"
