# Architecture Research

**Domain:** Python CLI tool — LLM + RAG + document ingestion (AI copywriter)
**Researched:** 2026-03-20
**Confidence:** HIGH (LangChain, RAG pipeline patterns, vector stores verified via official docs and multiple 2025-2026 sources)

## Standard Architecture

### System Overview

```
┌──────────────────────────────────────────────────────────────┐
│                        CLI LAYER                              │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  PromptSession (prompt_toolkit)                          │  │
│  │  Conversational REPL loop — reads user input,           │  │
│  │  routes commands, prints output, manages session state  │  │
│  └───────────────────────────┬─────────────────────────────┘  │
└──────────────────────────────┼───────────────────────────────┘
                               │
          ┌────────────────────▼────────────────────┐
          │            ORCHESTRATOR                  │
          │  (post generation session coordinator)   │
          │  Holds: conversation history, active     │
          │  topic, user intent, current draft        │
          └──┬───────────┬──────────────┬────────────┘
             │           │              │
    ┌────────▼──┐  ┌─────▼──────┐  ┌───▼──────────────┐
    │  NEWS     │  │  RAG /     │  │  POST GENERATOR   │
    │  SEARCHER │  │  KNOWLEDGE │  │  (LLM client +    │
    │  (Tavily) │  │  BASE      │  │  prompt builder)  │
    └────────┬──┘  └─────┬──────┘  └───────────────────┘
             │           │                    │
             │    ┌──────▼───────┐            │
             │    │  VECTOR      │            │
             │    │  STORE       │            │
             │    │  (ChromaDB,  │            │
             │    │  persisted)  │            │
             │    └──────────────┘            │
             │                                │
┌────────────┴────────────────────────────────▼──────────────┐
│                     INGESTION PIPELINE                       │
│  PDF Loader → PPTX Loader → Text Splitter → Embedder        │
│  (runs once on setup, re-runs when knowledge base changes)  │
└────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────▼──────────────┐
                    │      FILE OUTPUT          │
                    │  posts/YYYY-MM/slug.md   │
                    │  (Markdown writer)        │
                    └──────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| CLI Layer | User-facing REPL loop. Reads input, prints formatted output, handles Ctrl-C/exit gracefully. No business logic. | `prompt_toolkit.PromptSession` with `prompt()` in a `while True` loop |
| Orchestrator | Coordinates a single post-creation session. Holds mutable state: chat history, current topic, draft post. Routes user intent to the right subsystem. | Plain Python class `PostSession` instantiated per run |
| News Searcher | Fetches fresh AI news headlines/summaries for topic discovery. Returns structured results for display and LLM context injection. | Tavily Python SDK (`tavily-python`), wrapped in a thin service class |
| RAG / Knowledge Base | Retrieves relevant chunks from the user's personal documents given a query. Returns top-k text passages. | LangChain `VectorStoreRetriever` backed by ChromaDB |
| Vector Store | Persists embedded document chunks to disk. Queried at runtime for semantic similarity. | ChromaDB with local persistence path (`~/.linkedin_poster/chroma/`) |
| Ingestion Pipeline | One-off pipeline that loads PDFs/PPTXs, splits text, embeds, and writes to the vector store. Not in the hot path. | LangChain `PyPDFLoader` + `UnstructuredPowerPointLoader` + `RecursiveCharacterTextSplitter` + OpenAI embeddings |
| Post Generator | Assembles a prompt from topic + news context + RAG context + writing rules + conversation history, calls the LLM, returns structured draft. | LangChain `ChatOpenAI` (or Anthropic) with a system prompt template |
| File Output | Writes the approved post (EN + PT) to `posts/YYYY-MM/slug.md` with frontmatter metadata. | Plain Python `pathlib` + string templating — no framework needed |

## Recommended Project Structure

```
linkedin_poster/
├── cli/
│   ├── __init__.py
│   ├── main.py              # Entry point — `python -m linkedin_poster` or `linkedin-poster` via pyproject.toml
│   └── session.py           # PostSession class — orchestrates one post-creation run
│
├── ingestion/
│   ├── __init__.py
│   ├── loaders.py           # PDF + PPTX loader wrappers
│   ├── splitter.py          # Chunking config (size, overlap)
│   └── pipeline.py          # Ingestion entry point: load → split → embed → persist
│
├── knowledge/
│   ├── __init__.py
│   ├── store.py             # ChromaDB init, collection management
│   └── retriever.py         # Query interface returning top-k chunks
│
├── news/
│   ├── __init__.py
│   └── searcher.py          # Tavily wrapper — returns formatted news items
│
├── generator/
│   ├── __init__.py
│   ├── prompts.py           # System prompt template, writing rules, bilingual instructions
│   └── generator.py         # LLM call — takes context bundle, returns EN + PT draft
│
├── output/
│   ├── __init__.py
│   └── writer.py            # Writes approved posts to posts/YYYY-MM/slug.md
│
├── config.py                # Loads .env / config (API keys, model name, paths)
├── posts/                   # Generated post files (gitignored or committed per preference)
│   └── YYYY-MM/
│       └── topic-slug.md
└── knowledge_base/          # User drops PDFs/PPTXs here; ingestion reads from here
    └── .gitkeep
```

### Structure Rationale

- **cli/**: Keeps all terminal I/O isolated. Nothing in here makes LLM calls or touches the filesystem for posts. This boundary means the CLI can be tested independently or replaced.
- **ingestion/**: Runs separately from the main loop (a `ingest` command or a startup check). Separating it prevents accidental re-ingestion on every run.
- **knowledge/**: The vector store is infrastructure — isolating it means you can swap ChromaDB for FAISS or Qdrant without touching business logic.
- **news/**: Tavily is a network call with its own error domain. Wrapping it in its own module makes mocking in tests trivial and replacement easy.
- **generator/**: The prompt is the most-changed artifact during development. Isolating it in `prompts.py` keeps iteration fast.
- **output/**: Writing to disk is a side effect. One module, one concern.

## Architectural Patterns

### Pattern 1: Session Object as State Container

**What:** A single `PostSession` class holds all mutable state for one post-creation run: conversation history, the current topic, retrieved news, RAG results, and the current draft. All subsystems receive only what they need from this object.

**When to use:** Any conversational CLI tool where multiple turns happen before the final output is produced. Avoids global state and makes the session testable.

**Trade-offs:** Simple and effective for a single-user CLI. Does not scale to concurrent sessions — but that is out of scope here.

**Example:**
```python
class PostSession:
    def __init__(self):
        self.history: list[dict] = []          # LLM chat messages [{role, content}]
        self.topic: str | None = None
        self.news_context: list[dict] = []
        self.rag_context: list[str] = []
        self.current_draft: dict | None = None  # {"en": ..., "pt": ...}

    def add_turn(self, role: str, content: str) -> None:
        self.history.append({"role": role, "content": content})
```

### Pattern 2: Context Bundle Assembly Before LLM Call

**What:** Before calling the LLM, the generator assembles a single "context bundle" — a dict containing topic, news snippets, RAG passages, writing rules, and conversation history. The prompt template receives the bundle and renders the final messages list.

**When to use:** Any time multiple retrieval sources feed one generation step. Centralizing assembly makes it easy to debug what the LLM actually saw.

**Trade-offs:** Slightly more code than passing arguments directly. Pays off during refinement when you need to see what went wrong.

**Example:**
```python
def build_context(session: PostSession) -> dict:
    return {
        "topic": session.topic,
        "news": session.news_context,
        "rag_passages": session.rag_context,
        "history": session.history,
        "writing_rules": WRITING_RULES,  # constant from prompts.py
    }
```

### Pattern 3: Ingestion as a Separate Command (Not Auto-Run)

**What:** The `ingest` command is invoked explicitly by the user (`linkedin-poster ingest ./knowledge_base/`) rather than automatically on every startup. The vector store persists between runs, so re-embedding is only needed when documents change.

**When to use:** Any RAG tool where the document set is stable. Embedding is slow and costs tokens — don't do it on every launch.

**Trade-offs:** User must remember to re-run ingest after adding new documents. A simple "last-indexed" timestamp check at startup can prompt the user without forcing re-ingestion.

## Data Flow

### Flow 1: New Post Creation (Primary Flow)

```
User types: "write a post about GPT-4o voice mode"
    │
    ▼
CLI Layer (session.py)
    │  parses intent: "new post", topic = "GPT-4o voice mode"
    ▼
News Searcher
    │  Tavily query: "GPT-4o voice mode AI news 2026"
    │  returns: [{"title": ..., "url": ..., "snippet": ...}, ...]
    ▼
RAG Retriever
    │  query: "GPT-4o voice mode multimodal"
    │  ChromaDB similarity search → top-4 chunks from user's documents
    ▼
Post Generator
    │  builds context bundle (topic + news + rag + history + rules)
    │  renders system prompt + user message
    │  calls LLM (ChatOpenAI / Anthropic)
    │  returns {"en": "...", "pt": "..."}
    ▼
CLI Layer
    │  prints EN draft, then PT draft
    │  prompts: "Looks good? (yes / refine: ...)"
    ▼
[User approves]
    ▼
File Output
    │  constructs slug from topic + date
    │  writes posts/2026-03/gpt4o-voice-mode.md
    ▼
CLI confirms: "Saved to posts/2026-03/gpt4o-voice-mode.md"
```

### Flow 2: Conversational Refinement

```
User types: "make it shorter and remove the statistic"
    │
    ▼
CLI Layer
    │  appends user message to session.history
    ▼
Post Generator
    │  context bundle includes FULL history (prior drafts, user feedback)
    │  LLM sees previous draft + instruction → generates revised draft
    ▼
CLI Layer
    │  prints revised EN + PT
    │  continues REPL — loops back to approval prompt
```

### Flow 3: Knowledge Base Ingestion (One-time Setup)

```
User runs: linkedin-poster ingest ./knowledge_base/
    │
    ▼
Ingestion Pipeline
    │  scans directory for .pdf and .pptx files
    │  for each file:
    │    PDF  → PyPDFLoader → list[Document]
    │    PPTX → UnstructuredPowerPointLoader → list[Document]
    │  RecursiveCharacterTextSplitter (chunk=600, overlap=100)
    │  OpenAI text-embedding-3-small → float vectors
    │  ChromaDB.add_documents(chunks, embeddings)
    │  persists to ~/.linkedin_poster/chroma/
    ▼
CLI confirms: "Ingested 3 files, 142 chunks stored."
```

### Session State

```
PostSession (lives for one terminal run)
    │
    ├── history[]         ← grows with each turn (user + assistant)
    ├── topic             ← set on first "write a post about X" intent
    ├── news_context[]    ← fetched once per topic, reused across refinements
    ├── rag_context[]     ← fetched once per topic, reused across refinements
    └── current_draft{}  ← overwritten on each generation/refinement
```

## Suggested Build Order

The build order follows the dependency graph — each layer can only be tested when its dependencies exist.

| Order | Component | Why This Position | Unblocks |
|-------|-----------|------------------|----------|
| 1 | Config + project scaffold | Everything reads from config (API keys, paths, model names). Must exist first. | All other components |
| 2 | LLM client (generator/generator.py) | Core capability. Validate the model works, prompt renders correctly, EN+PT returns. | Post generator iteration |
| 3 | CLI skeleton (REPL loop + PostSession) | Establishes the interactive loop. Can be tested with stub generator that echoes input. | Whole interaction model |
| 4 | News Searcher | Independent service, no dependencies on RAG. Adds real topic-research capability quickly, making the tool feel useful early. | News-grounded posts |
| 5 | Post Generator with news context | Wire news results into the prompt. Validate quality before adding RAG complexity. | Baseline post quality |
| 6 | Ingestion Pipeline | More complex (file parsing, splitting, embedding). Can be built and tested in isolation. | RAG capability |
| 7 | Vector Store + Retriever | Depends on ingestion pipeline having run at least once. | RAG-grounded posts |
| 8 | Post Generator with RAG context | Full context bundle: topic + news + rag + history. | Complete generation |
| 9 | File Output | Last because it depends on the post being approved — a UX concern, not a technical one. | Persistent output |
| 10 | Refinement loop polish | Conversational history already works from step 3; this step tightens the UX (exit commands, confirmation prompts, etc.) | Polished product |

## Anti-Patterns

### Anti-Pattern 1: Running Ingestion on Every Startup

**What people do:** Load and embed all documents at the start of every CLI session to ensure the knowledge base is "always fresh."

**Why it's wrong:** Embedding 50 PDF pages takes 5-30 seconds and costs real API tokens. The user's knowledge base rarely changes. The startup cost destroys the tool's usability.

**Do this instead:** Persist ChromaDB to disk. Add a startup check that compares `mtime` of files in `knowledge_base/` against a stored timestamp. Only re-ingest if files changed. Prompt the user: "New documents detected — run `ingest` to update."

### Anti-Pattern 2: Putting Business Logic in the CLI Loop

**What people do:** Write LLM calls, file writes, and prompt assembly directly inside the `while True:` REPL loop in `main.py`.

**Why it's wrong:** Untestable, unmaintainable, and makes adding features (e.g., a `--dry-run` flag or a test harness) nearly impossible without rearchitecting.

**Do this instead:** The CLI loop does exactly three things: read input, call an orchestrator method, print output. All logic lives in `PostSession` and the service modules.

### Anti-Pattern 3: One Monolithic LLM Prompt Template

**What people do:** A single 500-token system prompt string hardcoded in the function that calls the LLM.

**Why it's wrong:** The prompt is the highest-iteration artifact in an LLM tool. Mixing it with LLM call code means every tweak touches LLM infrastructure code. The bilingual requirement (EN + PT) adds structure that needs clear ownership.

**Do this instead:** Keep prompts in `generator/prompts.py` as named string constants or Jinja2 templates. Writing rules, persona instructions, and output format requirements are each separate constants assembled by a `render_system_prompt(context_bundle)` function.

### Anti-Pattern 4: Storing Full Conversation History in the LLM Call Every Turn

**What people do:** Pass the entire session history (including all prior drafts) as messages on every call, not realizing draft text can be 600+ tokens each.

**Why it's wrong:** Context window fills up quickly. A post session with 4 refinements can hit 8k-12k tokens easily, increasing cost and latency, and eventually hitting context limits.

**Do this instead:** Store full history in `PostSession.history` but pass only the last N turns to the LLM (a rolling window of ~6 turns is sufficient for refinement continuity). The current draft is always included explicitly — don't rely on the model "remembering" it from earlier history.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| OpenAI (LLM + embeddings) | REST via `langchain-openai` / `openai` SDK | API key from env. Use `gpt-4o` for generation, `text-embedding-3-small` for embeddings (cheapest, good enough for personal doc corpus) |
| Tavily Search API | REST via `tavily-python` SDK | Designed for LLM-friendly results. Free tier: 1000 searches/month — plenty for daily personal use. Wraps in `news/searcher.py`. |
| ChromaDB (local) | In-process Python library, no server needed | Persist to `~/.linkedin_poster/chroma/`. Zero infrastructure. The `chromadb` package runs entirely in-process. |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| CLI Layer ↔ Orchestrator | Direct Python method calls on `PostSession` | Session is a plain Python object — no events, no queues |
| Orchestrator ↔ News Searcher | Method call, returns `list[dict]` | Synchronous. Async upgrade possible if startup latency becomes a concern. |
| Orchestrator ↔ RAG Retriever | Method call, returns `list[str]` (chunk text only) | Metadata (source file, page) is captured but only surfaced in verbose mode |
| Orchestrator ↔ Post Generator | Method call, receives context bundle, returns `{"en": str, "pt": str}` | The generator is pure: same inputs produce same (probabilistic) outputs |
| Post Generator ↔ LLM Client | LangChain `ChatOpenAI.invoke()` or `ainvoke()` | LangChain abstraction lets you swap models (Anthropic, local Ollama) by changing one config value |
| Ingestion Pipeline ↔ Vector Store | LangChain `VectorStore.add_documents()` | Ingestion and retrieval both go through the same `knowledge/store.py` interface |
| Post Generator ↔ File Output | No direct connection — CLI layer receives draft, user approves, CLI calls writer | Keeps generation and persistence decoupled |

## Scaling Considerations

This is a single-user personal tool. Scaling is not a design concern. The relevant "scale" questions are about document corpus size and session length:

| Concern | Current Scope | Guidance |
|---------|--------------|----------|
| Knowledge base size | 10-50 personal documents | ChromaDB in-process is ideal. No server, no overhead. |
| Context window per session | 4-8 refinement turns | Rolling window of 6 turns + current draft stays under 8k tokens comfortably with GPT-4o |
| News search latency | ~1-2s per Tavily call | Acceptable for interactive use. Fetch news once per topic, reuse for refinements. |
| Embedding cost | One-time on ingest | `text-embedding-3-small` at $0.02/1M tokens makes 50 documents cost cents |

## Sources

- LangChain RAG documentation: https://docs.langchain.com/oss/python/langchain/rag
- LangChain PyPDFLoader: https://docs.langchain.com/oss/python/integrations/document_loaders/pypdfloader
- ChromaDB vs FAISS comparison (2025): https://medium.com/@priyaskulkarni/vector-databases-for-rag-faiss-vs-chroma-vs-pinecone-6797bd98277d
- ChromaDB Chroma vs FAISS recommendation: https://www.capellasolutions.com/blog/faiss-vs-chroma-lets-settle-the-vector-database-debate
- Tavily Python SDK: https://github.com/tavily-ai/tavily-python
- LangChain Tavily integration: https://python.langchain.com/docs/integrations/retrievers/tavily/
- prompt_toolkit documentation: https://python-prompt-toolkit.readthedocs.io/
- RAG pipeline patterns 2026: https://www.dsinnovators.com/blog/python/building-rag-pipelines-python-2026/
- LangChain vs LlamaIndex 2026: https://blog.premai.io/langchain-vs-llamaindex-2026-complete-production-rag-comparison/
- LLM agent memory architecture: https://dev.to/oblivionlabz/building-ai-agent-memory-architecture-a-deep-dive-into-llm-state-management-for-power-users-h8m

---
*Architecture research for: Python CLI LLM + RAG AI copywriter tool (LinkedIn Poster)*
*Researched: 2026-03-20*
