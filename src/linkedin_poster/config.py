from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL = os.getenv("MODEL", "anthropic/claude-sonnet-4-5")
MAX_TOKENS = 2048
MAX_RETRIES = 2
POSTS_DIR = Path("posts")
HISTORY_SOFT_CAP = 10  # Keep last N message pairs to avoid token exhaustion
