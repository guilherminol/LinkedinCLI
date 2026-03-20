import pytest
from unittest.mock import MagicMock
from pathlib import Path
import tempfile


@pytest.fixture
def mock_anthropic_client():
    client = MagicMock()
    response = MagicMock()
    response.content = [MagicMock(text="Generated post content without emojis.")]
    client.messages.create.return_value = response
    return client


@pytest.fixture
def tmp_posts_dir(tmp_path):
    posts = tmp_path / "posts"
    posts.mkdir()
    return posts


@pytest.fixture
def sample_en_post():
    return "Fine-tuning is often overkill. Most teams reach for it when prompt engineering would solve the problem faster and cheaper. Before you fine-tune, ask: does the model fail because it lacks knowledge, or because it lacks clear instructions?"


@pytest.fixture
def sample_pt_post():
    return "Fine-tuning parece a solucao obvia quando um modelo nao performa bem. Mas a maioria dos problemas que parecem exigir fine-tuning sao, na pratica, problemas de prompt engineering."


@pytest.fixture
def sample_post_with_emoji():
    return "This is a great post! \U0001f680 Let me tell you about AI."
