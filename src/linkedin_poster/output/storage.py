"""Output storage layer -- save and list LinkedIn posts as Markdown with YAML front-matter."""

from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

import frontmatter
from slugify import slugify


def save_post(
    topic: str,
    en_text: str,
    pt_text: str,
    format_type: str,
    posts_dir: Optional[Path] = None,
) -> Path:
    """Save an EN+PT post pair as a Markdown file with YAML front-matter.

    Returns the path to the saved file.
    """
    if posts_dir is None:
        from linkedin_poster.config import POSTS_DIR

        posts_dir = POSTS_DIR

    now = datetime.now()
    slug = slugify(topic, max_length=60)
    dir_path = posts_dir / now.strftime("%Y-%m")
    dir_path.mkdir(parents=True, exist_ok=True)

    body = f"## English\n\n{en_text}\n\n## Portugues\n\n{pt_text}"

    post = frontmatter.Post(body)
    post.metadata.update(
        {
            "date": now.isoformat(),
            "topic": topic,
            "format": format_type,
            "languages": ["en", "pt"],
        }
    )

    file_path = dir_path / f"{slug}.md"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(frontmatter.dumps(post))

    return file_path


def list_posts(posts_dir: Optional[Path] = None) -> List[Dict[str, str]]:
    """List all saved posts from the posts directory.

    Returns list of dicts with date, topic, format, file_path keys,
    sorted by date descending.
    """
    if posts_dir is None:
        from linkedin_poster.config import POSTS_DIR

        posts_dir = POSTS_DIR

    if not posts_dir.exists():
        return []

    entries = []
    for md_file in posts_dir.rglob("*.md"):
        post = frontmatter.load(str(md_file))
        entries.append(
            {
                "date": str(post.get("date", ""))[:10],
                "topic": post.get("topic", "Unknown"),
                "format": post.get("format", "Unknown"),
                "file_path": str(md_file),
            }
        )

    entries.sort(key=lambda e: e["date"], reverse=True)
    return entries
