from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 2048
MAX_RETRIES = 2
POSTS_DIR = Path("posts")
HISTORY_SOFT_CAP = 10  # Keep last N message pairs to avoid token exhaustion
