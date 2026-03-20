"""Tests for PostGenerator bilingual generation with independent histories and validation."""
import pytest
from unittest.mock import MagicMock, patch, call

from linkedin_poster.generation.client import PostGenerator, GenerationResult
from linkedin_poster.generation.prompts import EN_SYSTEM_PROMPT, PT_SYSTEM_PROMPT


@pytest.fixture
def mock_client():
    """Mock OpenAI client that returns clean text by default."""
    client = MagicMock()
    response = MagicMock()
    response.choices = [MagicMock(message=MagicMock(content="Clean post content without emojis."))]
    client.chat.completions.create.return_value = response
    return client


def _make_response(text: str) -> MagicMock:
    """Helper to create a mock API response with given text."""
    resp = MagicMock()
    resp.choices = [MagicMock(message=MagicMock(content=text))]
    return resp


class TestPostGeneratorInit:
    def test_init_separate_histories(self, mock_client):
        gen = PostGenerator(client=mock_client)
        assert gen._en_history == []
        assert gen._pt_history == []
        assert gen._en_history is not gen._pt_history


class TestGeneratePair:
    def test_generate_pair_two_api_calls(self, mock_client):
        gen = PostGenerator(client=mock_client)
        gen.generate_pair("AI trends", "short")
        assert mock_client.chat.completions.create.call_count == 2

    def test_generate_pair_correct_system_prompts(self, mock_client):
        gen = PostGenerator(client=mock_client)
        gen.generate_pair("AI trends", "short")
        calls = mock_client.chat.completions.create.call_args_list
        assert calls[0].kwargs["messages"][0] == {"role": "system", "content": EN_SYSTEM_PROMPT}
        assert calls[1].kwargs["messages"][0] == {"role": "system", "content": PT_SYSTEM_PROMPT}

    def test_generate_pair_returns_result(self, mock_client):
        gen = PostGenerator(client=mock_client)
        result = gen.generate_pair("AI trends", "short")
        assert isinstance(result, GenerationResult)
        assert hasattr(result, "en_text")
        assert hasattr(result, "pt_text")
        assert hasattr(result, "topic")
        assert hasattr(result, "format_key")
        assert hasattr(result, "en_passed")
        assert hasattr(result, "pt_passed")
        assert result.topic == "AI trends"
        assert result.format_key == "short"

    def test_histories_independent(self, mock_client):
        # Return different text for EN vs PT calls
        mock_client.chat.completions.create.side_effect = [
            _make_response("EN post about AI"),
            _make_response("PT post sobre IA"),
        ]
        gen = PostGenerator(client=mock_client)
        gen.generate_pair("AI", "short")
        assert len(gen._en_history) == 2  # user + assistant
        assert len(gen._pt_history) == 2
        assert gen._en_history[-1]["content"] == "EN post about AI"
        assert gen._pt_history[-1]["content"] == "PT post sobre IA"

    def test_histories_no_shared_reference(self, mock_client):
        gen = PostGenerator(client=mock_client)
        gen.generate_pair("AI", "short")
        # Modifying EN history should not affect PT history
        gen._en_history.append({"role": "user", "content": "extra"})
        assert len(gen._pt_history) == 2
        assert len(gen._en_history) == 3


class TestRefine:
    def test_refine_uses_existing_history(self, mock_client):
        gen = PostGenerator(client=mock_client)
        gen.generate_pair("AI", "short")
        assert mock_client.chat.completions.create.call_count == 2

        gen.refine("make it shorter")
        assert mock_client.chat.completions.create.call_count == 4
        # Each history should have 4 entries: 2 from generate + 2 from refine
        assert len(gen._en_history) == 4
        assert len(gen._pt_history) == 4

    def test_refine_returns_generation_result(self, mock_client):
        gen = PostGenerator(client=mock_client)
        gen.generate_pair("AI", "short")
        result = gen.refine("make it shorter")
        assert isinstance(result, GenerationResult)
        assert result.topic == "AI"
        assert result.format_key == "short"


class TestEmojiValidation:
    def test_en_emoji_triggers_retry(self, mock_client):
        # EN initial has emoji -> validate_post calls regenerate -> EN retry clean -> PT clean
        mock_client.chat.completions.create.side_effect = [
            _make_response("text \U0001f680 with rocket"),  # EN initial (has emoji)
            _make_response("EN clean text"),                  # EN retry via validate_post
            _make_response("PT clean text"),                  # PT initial
        ]
        gen = PostGenerator(client=mock_client)
        result = gen.generate_pair("AI", "short")
        assert result.en_text == "EN clean text"
        assert result.en_passed is True

    def test_pt_only_retry_does_not_affect_en(self, mock_client):
        # EN clean on first try, PT has emoji twice then clean
        mock_client.chat.completions.create.side_effect = [
            _make_response("EN clean text"),                  # EN initial
            _make_response("PT text \U0001f389"),             # PT initial (has emoji)
            _make_response("PT text \U0001f389 again"),       # PT retry 1 (still emoji)
            _make_response("PT clean text"),                  # PT retry 2
        ]
        gen = PostGenerator(client=mock_client)
        result = gen.generate_pair("AI", "short")
        assert result.en_text == "EN clean text"
        assert result.pt_text == "PT clean text"
        assert result.pt_passed is True

    def test_failed_validation_flag(self, mock_client):
        # All responses contain emoji -- validation should fail
        mock_client.chat.completions.create.return_value = _make_response("text \U0001f680 emoji")
        gen = PostGenerator(client=mock_client)
        result = gen.generate_pair("AI", "short")
        assert result.en_passed is False
        assert result.pt_passed is False


class TestHistoryTruncation:
    @patch("linkedin_poster.generation.client.HISTORY_SOFT_CAP", 2)
    def test_history_truncation(self, mock_client):
        gen = PostGenerator(client=mock_client)
        # Generate multiple pairs to build up history
        for i in range(5):
            mock_client.chat.completions.create.side_effect = [
                _make_response(f"EN post {i}"),
                _make_response(f"PT post {i}"),
            ]
            gen.generate_pair(f"topic {i}", "short")
        # With HISTORY_SOFT_CAP=2, max_messages=4 (2 pairs of user+assistant)
        assert len(gen._en_history) <= 4
        assert len(gen._pt_history) <= 4
