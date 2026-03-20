"""PostGenerator: bilingual LinkedIn post generation via Anthropic API."""
from dataclasses import dataclass
from typing import List, Dict, Optional

import anthropic

from linkedin_poster.config import (
    ANTHROPIC_API_KEY,
    ANTHROPIC_MODEL,
    MAX_TOKENS,
    MAX_RETRIES,
    HISTORY_SOFT_CAP,
)
from linkedin_poster.generation.prompts import (
    EN_SYSTEM_PROMPT,
    PT_SYSTEM_PROMPT,
    build_generation_prompt,
)
from linkedin_poster.generation.validator import validate_post


@dataclass
class GenerationResult:
    """Result of a bilingual post generation."""

    en_text: str
    pt_text: str
    topic: str
    format_key: str
    en_passed: bool
    pt_passed: bool


class PostGenerator:
    """Generates bilingual LinkedIn posts via Anthropic API.

    Maintains separate EN and PT conversation histories.
    Validates each post independently for emoji violations.
    """

    def __init__(self, client: Optional[anthropic.Anthropic] = None):
        self._client = client or anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self._en_history: List[Dict[str, str]] = []
        self._pt_history: List[Dict[str, str]] = []
        self._current_topic: str = ""
        self._current_format: str = "short"

    def generate_pair(self, topic: str, format_key: str) -> GenerationResult:
        """Generate an EN+PT post pair for the given topic and format."""
        self._current_topic = topic
        self._current_format = format_key
        user_msg = build_generation_prompt(topic, format_key)

        # Generate EN
        en_raw = self._call_api(user_msg, EN_SYSTEM_PROMPT, self._en_history)
        en_text, en_passed = validate_post(
            en_raw,
            lambda: self._regenerate("en"),
            max_retries=MAX_RETRIES,
        )

        # Generate PT (completely independent)
        pt_raw = self._call_api(user_msg, PT_SYSTEM_PROMPT, self._pt_history)
        pt_text, pt_passed = validate_post(
            pt_raw,
            lambda: self._regenerate("pt"),
            max_retries=MAX_RETRIES,
        )

        return GenerationResult(
            en_text=en_text,
            pt_text=pt_text,
            topic=topic,
            format_key=format_key,
            en_passed=en_passed,
            pt_passed=pt_passed,
        )

    def refine(self, instruction: str) -> GenerationResult:
        """Refine the current post pair with a user instruction."""
        # Generate refined EN
        en_raw = self._call_api(instruction, EN_SYSTEM_PROMPT, self._en_history)
        en_text, en_passed = validate_post(
            en_raw,
            lambda: self._regenerate("en"),
            max_retries=MAX_RETRIES,
        )

        # Generate refined PT
        pt_raw = self._call_api(instruction, PT_SYSTEM_PROMPT, self._pt_history)
        pt_text, pt_passed = validate_post(
            pt_raw,
            lambda: self._regenerate("pt"),
            max_retries=MAX_RETRIES,
        )

        return GenerationResult(
            en_text=en_text,
            pt_text=pt_text,
            topic=self._current_topic,
            format_key=self._current_format,
            en_passed=en_passed,
            pt_passed=pt_passed,
        )

    def reset(self):
        """Clear conversation histories for a new post."""
        self._en_history.clear()
        self._pt_history.clear()
        self._current_topic = ""
        self._current_format = "short"

    def _call_api(
        self, user_msg: str, system_prompt: str, history: List[Dict[str, str]]
    ) -> str:
        """Make a single API call and update history."""
        history.append({"role": "user", "content": user_msg})
        self._truncate_history(history)

        response = self._client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=MAX_TOKENS,
            system=system_prompt,
            messages=history,
        )
        assistant_text = response.content[0].text
        history.append({"role": "assistant", "content": assistant_text})
        self._truncate_history(history)
        return assistant_text

    def _regenerate(self, lang: str) -> str:
        """Re-generate a post for retry. Removes last assistant response and re-calls."""
        if lang == "en":
            history = self._en_history
            system_prompt = EN_SYSTEM_PROMPT
        else:
            history = self._pt_history
            system_prompt = PT_SYSTEM_PROMPT

        # Remove the failed assistant response
        if history and history[-1]["role"] == "assistant":
            history.pop()

        response = self._client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=MAX_TOKENS,
            system=system_prompt,
            messages=history,
        )
        assistant_text = response.content[0].text
        history.append({"role": "assistant", "content": assistant_text})
        return assistant_text

    def _truncate_history(self, history: List[Dict[str, str]]):
        """Keep only the last HISTORY_SOFT_CAP message pairs to avoid token exhaustion."""
        max_messages = HISTORY_SOFT_CAP * 2  # Each pair is user + assistant
        if len(history) > max_messages:
            del history[:-max_messages]
