"""Tests for the output/storage module -- save_post and list_posts."""

from pathlib import Path
from unittest.mock import patch
from datetime import datetime

import frontmatter
import pytest

from linkedin_poster.output.storage import save_post, list_posts


class TestSavePost:
    """Tests for save_post function."""

    def test_save_creates_file(self, tmp_path: Path):
        result = save_post(
            "Fine-tuning tips", "EN content", "PT content", "short", tmp_path
        )
        assert result.exists()
        assert result.suffix == ".md"

    def test_save_file_path_structure(self, tmp_path: Path):
        now = datetime.now()
        result = save_post(
            "Fine-tuning tips", "EN content", "PT content", "short", tmp_path
        )
        expected_dir = tmp_path / now.strftime("%Y-%m")
        assert result.parent == expected_dir
        assert result.name == "fine-tuning-tips.md"

    def test_save_frontmatter_keys(self, tmp_path: Path):
        path = save_post(
            "Fine-tuning tips", "EN content", "PT content", "short", tmp_path
        )
        post = frontmatter.load(str(path))
        for key in ("date", "topic", "format", "languages"):
            assert key in post.metadata, f"Missing front-matter key: {key}"

    def test_save_frontmatter_values(self, tmp_path: Path):
        path = save_post(
            "Fine-tuning tips", "EN content", "PT content", "short", tmp_path
        )
        post = frontmatter.load(str(path))
        assert post.metadata["topic"] == "Fine-tuning tips"
        assert post.metadata["format"] == "short"
        assert post.metadata["languages"] == ["en", "pt"]

    def test_save_body_contains_en_pt_sections(self, tmp_path: Path):
        path = save_post(
            "Fine-tuning tips", "EN content", "PT content", "short", tmp_path
        )
        post = frontmatter.load(str(path))
        assert "## English" in post.content
        assert "## Portugues" in post.content

    def test_save_body_contains_content(self, tmp_path: Path):
        path = save_post(
            "Fine-tuning tips", "EN content here", "PT content here", "short", tmp_path
        )
        post = frontmatter.load(str(path))
        assert "EN content here" in post.content
        assert "PT content here" in post.content

    def test_save_slug_truncation(self, tmp_path: Path):
        long_topic = "A" * 120  # 120 chars, slug should be truncated
        path = save_post(long_topic, "EN", "PT", "short", tmp_path)
        stem = path.stem  # filename without .md extension
        assert len(stem) <= 60

    def test_save_creates_directories(self, tmp_path: Path):
        nested = tmp_path / "deep" / "nested"
        # nested dir does not exist yet
        assert not nested.exists()
        path = save_post("Test topic", "EN", "PT", "short", nested)
        assert path.exists()


class TestListPosts:
    """Tests for list_posts function."""

    def test_list_empty(self, tmp_path: Path):
        result = list_posts(tmp_path)
        assert result == []

    def test_list_returns_entries(self, tmp_path: Path):
        save_post("Topic one", "EN1", "PT1", "short", tmp_path)
        save_post("Topic two", "EN2", "PT2", "carousel", tmp_path)
        entries = list_posts(tmp_path)
        assert len(entries) == 2
        for entry in entries:
            for key in ("date", "topic", "format", "file_path"):
                assert key in entry, f"Missing key: {key}"

    def test_list_sorted_descending(self, tmp_path: Path):
        # Save two posts with different mocked dates
        with patch("linkedin_poster.output.storage.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2025, 1, 15, 10, 0, 0)
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            save_post("Older post", "EN", "PT", "short", tmp_path)

        with patch("linkedin_poster.output.storage.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2025, 6, 20, 10, 0, 0)
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            save_post("Newer post", "EN", "PT", "short", tmp_path)

        entries = list_posts(tmp_path)
        assert len(entries) == 2
        assert entries[0]["topic"] == "Newer post"
        assert entries[1]["topic"] == "Older post"
