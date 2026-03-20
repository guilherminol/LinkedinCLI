# Stack Research

**Domain:** Python CLI AI assistant — document ingestion, web search, LLM generation
**Researched:** 2026-03-20
**Confidence:** HIGH (core stack), MEDIUM (vector store choice)

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | 3.11+ | Runtime | 3.11 has the best balance of performance gains and library compatibility; 3.12 works but some ML libs lag. 3.10 is the minimum for modern type hints. |
| anthropic (SDK) | 0.86.x | Claude API client | Official Anthropic SDK. Provides typed sync/async clients, streaming via `client.messages.stream()`, tool use helpers, and automatic retries. Direct API — no LangChain middleman needed. |
| Rich | 14.x | Terminal output rendering | The definitive Python terminal UI library. Renders Markdown, tables, progress bars, and syntax-highlighted code directly in the terminal. Pairs with prompt_toolkit for a polished conversational interface. |
| prompt_toolkit | 3.0.x | Interactive input loop | Pure Python readline replacement with multi-line editing, history persistence, Emacs/Vi keybindings, and autocompletion. The standard for conversational terminal applications in Python. |
| pymupdf4llm | 0.0.x | PDF → Markdown extraction | Extension of PyMuPDF specifically built for LLM/RAG ingestion. Converts PDF pages to clean GitHub-flavored Markdown in one call: `pymupdf4llm.to_markdown("file.pdf")`. Handles multi-column layouts and table structure. |
| python-pptx | 1.0.x | PPTX text extraction | The only mature, actively maintained library for reading PowerPoint files in Python. Provides clean access to slides, shapes, and text frames. No C dependencies. |
| chromadb | 0.6.x | Local vector store | Persistent local vector database backed by SQLite. Runs entirely in-process with no server required — `chromadb.PersistentClient(path=".chroma")`. Uses default sentence-transformer embeddings. Ideal for the personal-tool scale of this project. |
| tavily-python | 0.5.x | Web/news search | AI-native search API built specifically for LLM workflows. Returns aggregated, ranked, LLM-ready content (not raw HTML) from up to 20 sources per query. Free tier: 1,000 credits/month — sufficient for daily news research. Has dedicated `search_depth="advanced"` and `topic="news"` parameters. |
| pydantic-settings | 2.x | Configuration management | Type-safe environment and config management. Reads from `.env` file and environment variables simultaneously. Replaces both `python-dotenv` and manual config parsing. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| python-slugify | 8.x | Post filename generation | Converts post titles to filesystem-safe slugs for `posts/YYYY-MM/slug.md` naming. Required for output file management. |
| pathlib (stdlib) | built-in | File/folder management | Use over `os.path` for all path manipulation. Creates the `posts/YYYY-MM/` folder structure cleanly. |
| python-dateutil | 2.9.x | Date parsing/formatting | Reliable date utilities for folder naming (YYYY-MM). Not strictly required — `datetime` stdlib can handle this — but useful if parsing dates from document metadata. |
| httpx | 0.27.x | HTTP client (if needed) | Async-capable HTTP client used internally by the Anthropic SDK. Only add explicitly if you need direct API calls beyond what the SDK provides. |
| sentence-transformers | 3.x | Embeddings for ChromaDB | Provides local embedding models (e.g., `all-MiniLM-L6-v2`) for ChromaDB. Only install if you want to control the embedding model explicitly rather than using ChromaDB's default. Default ChromaDB embeddings are sufficient for this use case. |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| uv | Package and environment management | Fastest Python package manager in 2025. Use `uv init` and `uv add` instead of pip. Lock file ensures reproducible installs. |
| ruff | Linting and formatting | Single tool replaces flake8 + black + isort. Zero config by default. |
| python-dotenv (via pydantic-settings) | `.env` file loading | pydantic-settings handles `.env` loading natively when `python-dotenv` is installed. Just add `python-dotenv` as a dependency — no direct usage needed. |

## Installation

```bash
# Core dependencies
uv add anthropic rich prompt_toolkit pymupdf4llm python-pptx chromadb tavily-python pydantic-settings python-slugify python-dotenv

# Development dependencies
uv add --dev ruff
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| anthropic SDK (direct) | LangChain / LangGraph | If you need multi-model routing, complex agent graphs, or are building for a team that already uses LangChain abstractions. For a single-model personal tool, LangChain adds 200+ transitive dependencies and obscures the API. |
| prompt_toolkit | Rich's built-in `Console.input()` | If you need zero-friction single-line input with no history or multi-line editing. For a conversational loop with a "thinking partner" feel, prompt_toolkit's history and key bindings matter. |
| chromadb (local) | FAISS | If you need sub-millisecond performance at millions of vectors. FAISS has no document storage, no metadata, and no persistence layer — you'd build all of that yourself. ChromaDB bundles everything for the RAG use case. |
| chromadb (local) | Qdrant | If this tool ever grows to production multi-user scale. Qdrant (Rust-core) is superior for high-throughput production systems. Overkill for a personal CLI tool. |
| tavily-python | NewsAPI | If you need a structured news-only feed by category/source. NewsAPI is cheaper for pure news use cases but doesn't extract article content — you get headlines and URLs, not LLM-ready text. Use NewsAPI if Tavily credits run out. |
| tavily-python | Brave Search API | If you want a general web index with no per-query credit model. Brave has better raw index coverage; Tavily has better LLM-formatted output. Tavily wins for this workflow. |
| pymupdf4llm | pypdf | If you need a pure-Python zero-C-dependency install. pypdf's text extraction is less structured and does not produce Markdown. pymupdf4llm's output maps directly to LLM context windows. |
| pydantic-settings | python-dotenv alone | If you want minimal dependencies. pydantic-settings is strictly better — it adds type validation and makes `ANTHROPIC_API_KEY` appear as a typed attribute rather than a raw string from `os.environ`. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| LangChain | Extremely heavy dependency tree (300+ packages). Abstracts away the Anthropic SDK in ways that make debugging difficult. The API for tool use and streaming changes between minor versions. For a single-developer tool calling one LLM, it solves no real problem. | `anthropic` SDK directly |
| LlamaIndex | Same dependency weight issue as LangChain. Valuable for complex multi-document RAG pipelines across many data sources, but is over-engineered for ingesting a personal folder of PDFs and PPTXs. | `pymupdf4llm` + `chromadb` directly |
| Typer (as the conversational loop) | Typer/Click are excellent for command-dispatch CLIs (e.g., `git commit`, `docker run`). They are the wrong abstraction for a conversational chat loop. The input model is "parse a command" not "maintain a session." | `prompt_toolkit` + a custom REPL loop |
| argparse | Too verbose for modern Python. Type hints and pydantic already solve the validation problem more cleanly. | `pydantic-settings` for config; `prompt_toolkit` for the loop |
| PyPDF2 | Deprecated and unmaintained. Replaced by `pypdf` (the official successor). Even `pypdf` is outclassed by `pymupdf4llm` for LLM workflows. | `pymupdf4llm` |
| openai SDK | Wrong model provider. This project is built on Claude. | `anthropic` SDK |
| Pinecone | Cloud-only, paid, requires network for every query. This is a personal local tool — all data should stay local. | `chromadb` with `PersistentClient` |

## Stack Patterns by Variant

**If the user wants streaming responses in the terminal (watching Claude write in real time):**
- Use `client.messages.stream()` from the `anthropic` SDK with a context manager
- Pipe chunks to `Rich.Console().print()` progressively
- This is the expected behavior for a "thinking partner" feel

**If the knowledge base grows beyond ~1,000 document chunks:**
- Switch ChromaDB embedding model from default (`all-MiniLM-L6-v2`) to a larger model like `all-mpnet-base-v2`
- Consider chunking strategy: split PDFs by page (pymupdf4llm's `page_chunks=True`) rather than whole-document

**If Tavily free credits run out:**
- NewsAPI free tier: 100 requests/day, headlines only — requires extra fetch step for article content
- Brave Search API: independent index, privacy-first, free tier available

**If bilingual generation becomes a bottleneck:**
- Generate EN and PT in a single Claude call using a structured output prompt (one JSON object with `en` and `pt` keys)
- Avoids doubling API calls and keeps context consistent between translations

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| anthropic 0.86.x | Python 3.8+ | No known conflicts with this stack. Pins httpx internally. |
| chromadb 0.6.x | Python 3.8+ | 2025 Rust-core rewrite. Breaking change from 0.4.x API — do not mix docs from old versions. |
| pymupdf4llm 0.0.x | PyMuPDF 1.24+, Python 3.8+ | `pip install pymupdf4llm` installs PyMuPDF automatically. License: AGPL for PyMuPDF (commercial license available). Acceptable for personal use. |
| python-pptx 1.0.x | Python 3.6+ | Version 1.0 (released 2024) has breaking changes from 0.x. Use 1.0.x docs, not older tutorials. |
| pydantic-settings 2.x | pydantic 2.x | Requires pydantic v2. Do not mix with pydantic v1 which has a different settings API (`BaseSettings` was in core pydantic v1). |
| Rich 14.x | Python 3.8+ | No conflicts. Works alongside prompt_toolkit without special configuration. |
| prompt_toolkit 3.0.x | Python 3.6+ | Async-native. Use `prompt_toolkit.shortcuts.PromptSession` for the main conversation loop. |

## Sources

- [anthropic PyPI](https://pypi.org/project/anthropic/) — confirmed version 0.86.0, March 2026
- [Anthropic Client SDKs docs](https://docs.claude.com/en/api/client-sdks) — streaming, tool use confirmed
- [pymupdf4llm PyPI](https://pypi.org/project/pymupdf4llm/) — LLM-optimized PDF extraction
- [PyMuPDF4LLM documentation](https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/) — `to_markdown()` API, page_chunks confirmed
- [python-prompt-toolkit GitHub](https://github.com/prompt-toolkit/python-prompt-toolkit) — 3.0.52, actively maintained
- [chromadb PyPI](https://pypi.org/project/chromadb/) — 0.6.x with Rust-core rewrite confirmed
- [Tavily pricing](https://www.tavily.com/pricing) — 1,000 free credits/month confirmed
- [tavily-python GitHub](https://github.com/tavily-ai/tavily-python) — Python SDK confirmed
- [pydantic-settings docs](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) — env + .env loading confirmed
- [Rich documentation](https://rich.readthedocs.io/en/latest/markdown.html) — Markdown rendering confirmed
- [python-pptx 1.0.0 docs](https://python-pptx.readthedocs.io/en/latest/user/quickstart.html) — version 1.0 release confirmed
- WebSearch: CLI framework comparison (Typer vs Click vs prompt_toolkit) — HIGH confidence
- WebSearch: Vector store comparison (Chroma vs FAISS vs Qdrant for small projects) — MEDIUM confidence

---
*Stack research for: LinkedIn AI Copywriter CLI — Python, Claude, document ingestion, web search*
*Researched: 2026-03-20*
