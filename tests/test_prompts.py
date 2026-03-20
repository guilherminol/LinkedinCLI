"""Tests for system prompts and format instructions -- TDD RED phase for Task 2."""
from linkedin_poster.generation.prompts import (
    RULE_BLOCK,
    EN_SYSTEM_PROMPT,
    PT_SYSTEM_PROMPT,
    FORMAT_INSTRUCTIONS,
    build_generation_prompt,
)


def test_rule_block_contains_emoji_rule():
    assert "NEVER use emojis" in RULE_BLOCK


def test_rule_block_contains_clickbait_rule():
    assert "NEVER use clickbait" in RULE_BLOCK


def test_en_system_prompt_includes_rule_block():
    assert RULE_BLOCK in EN_SYSTEM_PROMPT


def test_pt_system_prompt_includes_rule_block():
    assert RULE_BLOCK in PT_SYSTEM_PROMPT


def test_pt_system_prompt_has_one_shot_example():
    assert "Fine-tuning parece" in PT_SYSTEM_PROMPT


def test_pt_system_prompt_targets_br_audience():
    assert "profissionais de tecnologia" in PT_SYSTEM_PROMPT


def test_format_instructions_keys():
    assert set(FORMAT_INSTRUCTIONS.keys()) == {"short", "carousel", "hook"}


def test_short_format_length_constraint():
    assert "300" in FORMAT_INSTRUCTIONS["short"]
    assert "600" in FORMAT_INSTRUCTIONS["short"]


def test_carousel_format_sections():
    assert "3-5 sections" in FORMAT_INSTRUCTIONS["carousel"]


def test_hook_format_structure():
    text = FORMAT_INSTRUCTIONS["hook"].lower()
    assert "rhetorical question" in text or "question" in text


def test_build_generation_prompt_contains_topic():
    result = build_generation_prompt("AI safety", "short")
    assert "AI safety" in result


def test_build_generation_prompt_contains_format():
    result = build_generation_prompt("AI safety", "short")
    assert "300-600 characters" in result
