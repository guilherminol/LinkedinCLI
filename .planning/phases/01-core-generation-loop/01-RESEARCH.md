# Phase 1: Core Generation Loop - Research

**Researched:** 2026-03-20
**Domain:** Python CLI + Anthropic Messages API + bilingual post generation
**Confidence:** HIGH

## Summary

Phase 1 builds a conversational REPL that generates bilingual LinkedIn posts using the Anthropic Python SDK directly (no LangChain). The core loop is: user types a topic, the system sends a request to Claude with a system prompt enforcing voice/tone rules, receives EN and PT posts, validates them for emoji violations, and displays the pair. The user can refine conversationally (multi-turn via stateless message history accumulation) or save to disk as front-matter Markdown.

The stack is straightforward: `anthropic` SDK for LLM calls, `prompt_toolkit` for the interactive REPL with command parsing, `rich` for terminal formatting and spinner animations, `python-frontmatter` for Markdown output with YAML front-matter, and `python-slugify` for filename generation. Emoji detection uses the `emoji` library which tracks Unicode releases. All libraries are mature and stable.

**Primary recommendation:** Build a clean separation between the REPL layer (input/commands), the generation layer (Anthropic API calls + retry logic), and the output layer (formatting + file persistence). The system prompt is the primary control mechanism for tone; the post-generation emoji check is the safety net.

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions

**Post Format Specs:**
- Short text: 300-600 characters of prose, single block, no headers/bullets, CTA generated fresh each time
- Carousel/long-form: 3-5 sections with bold header + 2-4 sentences each, ~800-1,500 characters total
- Hook + breakdown: Rhetorical question hook, 2-3 short prose paragraphs answering it, conversational not listicle

**Portuguese Voice Spec:**
- Audience: Brazilian tech professionals and recruiters (BR Portuguese, not neutral/European)
- Loanword rule: Established tech terms stay in English (fine-tuning, embedding, benchmark, prompt, token, RAG, LLM)
- Content relationship: Same topic and key points, independently phrased for BR audience -- NOT translation
- System prompt must include a PT-specific one-shot example

**REPL Session Flow:**
- Session start: Brief welcome line + blank prompt
- Post display: EN block first, then PT block, separated by labeled dividers
- Refinements: Apply to both EN and PT simultaneously
- Progress feedback: Animated spinner with sequential status messages

**Writing Rule Enforcement:**
- Blocked content: Emojis only (regex/unicode range check), no explicit phrase blocklist
- Violation response: Auto re-generate silently, max 2 retries per language
- After 2 retries: Show error message with raw output, user can refine manually
- EN and PT checked independently; if only one fails, only that one is re-generated

**SDK and Architecture:**
- Use Anthropic SDK directly -- do NOT use LangChain
- Per-turn rule injection: prepend short rule block to every LLM call
- Post-generation blocked vocabulary check (emoji regex) after every generation call

### Claude's Discretion
- Exact spinner animation library / implementation
- Session history format in memory
- Exact welcome message wording
- Slug generation logic for the `.md` filename

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope.

</user_constraints>

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| CLI-01 | Conversational REPL with session history | prompt_toolkit provides REPL loop; conversation history stored as list of message dicts passed to Anthropic API |
| CLI-02 | `/new`, `/refine`, `/save`, `/list` commands | prompt_toolkit input handler with command prefix detection; simple if/elif dispatch |
| CLI-04 | Formatted post preview in terminal before saving | rich library Console + Panel/Markdown rendering for EN/PT dividers and formatted output |
| GEN-01 | Choose post format (short text, carousel, hook+breakdown) | Format selection via prompt or command; format-specific instructions injected into system prompt |
| GEN-02 | Bilingual EN + PT generation (independent, not translation) | Two separate API calls per generation -- one EN system prompt, one PT system prompt with one-shot example |
| GEN-03 | No-emoji and no-clickbait enforcement with auto re-generation | emoji library `emoji.replace_emoji()` for detection; retry loop with max 2 attempts per language |
| GEN-04 | Consistent "AI translator" voice | System prompt with voice guidelines, per-turn rule injection block |
| OUT-01 | Posts saved as `.md` at `posts/YYYY-MM/slug.md` with front-matter | python-frontmatter for YAML front-matter; python-slugify for filename; pathlib for directory creation |
| OUT-02 | `/list` command shows previously generated posts | Scan `posts/` directory, parse front-matter metadata, display as formatted table via rich |

</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| anthropic | 0.86.0 | LLM API calls (Messages API) | Official Anthropic SDK, actively maintained, stateless multi-turn via message list |
| prompt_toolkit | 3.0.52 | Interactive REPL with history, key bindings | De facto standard for Python CLI REPLs, used by IPython/ptpython, supports async |
| rich | 14.3.3 | Terminal formatting, spinners, panels, markdown | Most popular Python terminal formatting lib, built-in spinner/status support |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| python-frontmatter | 1.1.0 | Read/write Markdown with YAML front-matter | Saving and listing posts (OUT-01, OUT-02) |
| python-slugify | 8.0.4 | Generate URL-safe slugs from post topics | Filename generation for `posts/YYYY-MM/slug.md` |
| emoji | 2.15.0 | Detect emojis in generated text | Post-generation validation check (GEN-03) |
| python-dotenv | 1.1.0 | Load `.env` for ANTHROPIC_API_KEY | Environment variable management |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| prompt_toolkit | built-in input() | No history, no keybindings, no async -- unsuitable for REPL |
| rich | colorama | No spinner, no panels, no markdown rendering -- too low-level |
| emoji library | raw regex | Regex patterns break on new Unicode releases; emoji lib tracks them |
| python-frontmatter | manual YAML + string concat | Error-prone YAML serialization, frontmatter handles edge cases |

**Installation:**
```bash
pip install anthropic prompt_toolkit rich python-frontmatter python-slugify emoji python-dotenv
```

## Architecture Patterns

### Recommended Project Structure
```
src/
  linkedin_poster/
    __init__.py
    main.py              # Entry point, REPL loop
    cli/
      __init__.py
      repl.py            # prompt_toolkit REPL session, command dispatch
      commands.py        # /new, /refine, /save, /list handlers
      display.py         # rich formatting, spinners, post preview
    generation/
      __init__.py
      client.py          # Anthropic client wrapper, message history
      prompts.py         # System prompts (EN, PT), format templates, rule block
      validator.py       # Emoji detection, retry logic
    output/
      __init__.py
      storage.py         # Save posts, list posts, directory management
      frontmatter.py     # Front-matter schema, serialization
    config.py            # Settings, model name, paths, constants
posts/                   # Generated output (gitignored or version-controlled)
  YYYY-MM/
    slug.md
tests/
  __init__.py
  test_validator.py
  test_storage.py
  test_prompts.py
  conftest.py
```

### Pattern 1: Stateless Multi-Turn Conversation
**What:** The Anthropic Messages API is stateless. You accumulate the full conversation history as a list of `{"role": "user"|"assistant", "content": "..."}` dicts and send the entire list on every call.
**When to use:** Every generation and refinement call.
**Example:**
```python
# Source: https://platform.claude.com/docs/en/api/messages-examples
import anthropic

client = anthropic.Anthropic()

# Conversation history stored in-memory as a list
history = []

def generate(user_input: str, system_prompt: str) -> str:
    history.append({"role": "user", "content": user_input})
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        system=system_prompt,
        messages=history,
    )
    assistant_text = message.content[0].text
    history.append({"role": "assistant", "content": assistant_text})
    return assistant_text
```

### Pattern 2: Per-Turn Rule Injection via System Prompt
**What:** Prepend a short rule block to the system prompt on every call, ensuring tone rules are always active regardless of conversation length.
**When to use:** Every `messages.create()` call.
**Example:**
```python
RULE_BLOCK = """
MANDATORY RULES (apply to EVERY response):
- NEVER use emojis in the post text
- NEVER use clickbait phrases, hype language, or sensationalist hooks
- Write with professional authority -- technical depth made accessible
- Tone: substance over performance, no "mind-blowing" or "game-changing"
"""

EN_SYSTEM_PROMPT = RULE_BLOCK + """
You are a LinkedIn copywriter for an AI engineer targeting US tech recruiters.
Voice: "AI translator" -- you understand the technical depth and communicate it clearly.
...
"""

PT_SYSTEM_PROMPT = RULE_BLOCK + """
Voce e um copywriter de LinkedIn para um engenheiro de IA.
Publico: profissionais de tecnologia e recrutadores brasileiros.
Termos tecnicos em ingles mantidos: fine-tuning, embedding, benchmark, prompt, token, RAG, LLM.
Nao traduza o post do ingles -- escreva de forma independente para o publico BR.

Exemplo:
[one-shot PT example here]
...
"""
```

### Pattern 3: Format-Specific Prompt Injection
**What:** Each post format (short, carousel, hook+breakdown) has a specific structural instruction appended to the system prompt or user message.
**When to use:** When user selects or changes format.
**Example:**
```python
FORMAT_INSTRUCTIONS = {
    "short": (
        "Generate a SHORT TEXT post:\n"
        "- 300-600 characters of prose\n"
        "- Single block, no headers, no bullets\n"
        "- End with a fresh CTA fitted to this specific post"
    ),
    "carousel": (
        "Generate a CAROUSEL/LONG-FORM post:\n"
        "- 3-5 sections, each with a **bold header** + 2-4 sentences\n"
        "- Total length: 800-1,500 characters\n"
        "- Designed to read as a multi-slide carousel"
    ),
    "hook": (
        "Generate a HOOK + BREAKDOWN post:\n"
        "- Start with a rhetorical question hook\n"
        "- Follow with 2-3 short prose paragraphs that answer the hook\n"
        "- Conversational tone, not a listicle"
    ),
}
```

### Pattern 4: Independent EN/PT Generation with Shared Context
**What:** Generate EN and PT as two separate API calls, each with its own system prompt, but sharing the same user topic/instructions. This is NOT translation -- each language gets independent phrasing.
**When to use:** Every post generation.
**Example:**
```python
def generate_pair(topic: str, format_key: str, history_en: list, history_pt: list):
    format_instruction = FORMAT_INSTRUCTIONS[format_key]
    user_msg = f"Topic: {topic}\n\n{format_instruction}"

    en_post = generate(user_msg, EN_SYSTEM_PROMPT, history_en)
    pt_post = generate(user_msg, PT_SYSTEM_PROMPT, history_pt)

    return en_post, pt_post
```

### Anti-Patterns to Avoid
- **Single API call for both languages:** Do NOT ask Claude to generate EN and PT in one response -- it leads to translation artifacts and makes independent retry impossible
- **Storing system prompt in message history:** The `system` parameter is separate from `messages`; do not include it as a user message
- **Unbounded conversation history:** Over many refinement turns, the history grows. Implement a soft cap (e.g., keep last N turns) to avoid token limit issues
- **Parsing structured output from free text:** If you need structured data (e.g., post metadata), use separate extraction rather than parsing prose responses

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Emoji detection | Custom Unicode range regex | `emoji` library (2.15.0) | Unicode emoji spec changes yearly; library tracks releases |
| YAML front-matter | String concatenation of `---` blocks | `python-frontmatter` (1.1.0) | Handles escaping, multiline strings, roundtrip read/write |
| URL-safe slugs | Custom regex replace | `python-slugify` (8.0.4) | Handles Unicode, transliteration, edge cases |
| Terminal spinners | Threading + print statements | `rich.status` or `rich.spinner` | Thread-safe, non-blocking, many animation styles |
| REPL input loop | `while True: input()` | `prompt_toolkit.PromptSession` | History, keybindings, async support, multiline |

**Key insight:** Every "simple" text-processing task in this project (emoji check, YAML serialization, slug generation) has edge cases that libraries handle and hand-rolled code does not.

## Common Pitfalls

### Pitfall 1: Emoji Leaking Through Validation
**What goes wrong:** Claude generates posts with emojis despite system prompt instructions. The post reaches the user.
**Why it happens:** LLMs are probabilistic; system prompts are suggestions, not guarantees. Emojis can appear as Unicode characters that simple string checks miss.
**How to avoid:** Always run `emoji.replace_emoji(text, replace='')` and compare lengths. If lengths differ, emojis were present. This catches all Unicode emoji including skin tone modifiers and ZWJ sequences.
**Warning signs:** Tests pass with ASCII-only content but fail with real LLM output.

### Pitfall 2: Token Limit Exhaustion on Long Sessions
**What goes wrong:** After many refinement turns, the accumulated message history exceeds the model's context window, causing API errors.
**Why it happens:** The Messages API is stateless -- you send the FULL history every time. 20+ turns of bilingual posts add up fast.
**How to avoid:** Track approximate token count (rough estimate: 4 chars per token). When approaching 80% of context window, truncate oldest turns while keeping the system prompt and last 3-4 exchanges. Warn the user.
**Warning signs:** `anthropic.BadRequestError` with "max tokens" or context length messages.

### Pitfall 3: PT Posts Reading as Translations
**What goes wrong:** Portuguese posts feel like translated English rather than independently authored BR content.
**Why it happens:** If the EN post is generated first and included in the PT prompt context, Claude tends to translate rather than independently phrase. Also, weak PT system prompts lead to "translate" behavior.
**How to avoid:** Keep EN and PT conversation histories completely separate. The PT system prompt must include a strong one-shot example of what good BR Portuguese content looks like. Never pass the EN output as input to the PT generation.
**Warning signs:** PT posts mirror EN sentence structure exactly.

### Pitfall 4: Command Parsing Conflicts with Natural Language
**What goes wrong:** User types "I want to /save this for later" and the system interprets `/save` as a command.
**Why it happens:** Naive string matching for commands.
**How to avoid:** Only treat input as a command if the ENTIRE input starts with `/`. If the first character is `/`, it is a command; otherwise, it is a refinement instruction.
**Warning signs:** Users report unexpected behavior when using `/` in natural language.

### Pitfall 5: Rich Spinner Conflicts with Input
**What goes wrong:** Spinner animation corrupts the terminal display or overlaps with the next prompt.
**Why it happens:** `rich.status` uses carriage returns to animate; if not properly stopped before printing output, display breaks.
**How to avoid:** Use `rich.console.status()` as a context manager. Ensure the spinner is fully stopped (context exited) before printing the generated post.
**Warning signs:** Garbled terminal output after generation completes.

## Code Examples

### REPL Session with prompt_toolkit
```python
# Source: prompt_toolkit docs - https://python-prompt-toolkit.readthedocs.io/
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory

session = PromptSession(history=InMemoryHistory())

while True:
    try:
        user_input = session.prompt("LinkedIn Copywriter > ")
        if not user_input.strip():
            continue
        if user_input.startswith("/"):
            handle_command(user_input)
        else:
            handle_topic_or_refinement(user_input)
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye!")
        break
```

### Rich Spinner During Generation
```python
# Source: rich docs - https://rich.readthedocs.io/en/stable/reference/spinner.html
from rich.console import Console

console = Console()

with console.status("Generating EN post...", spinner="dots") as status:
    en_post = generate_en(topic)
    status.update("Generating PT post...")
    pt_post = generate_pt(topic)
    status.update("Validating...")
    en_post = validate_and_retry(en_post, "en")
    pt_post = validate_and_retry(pt_post, "pt")

# Spinner is automatically stopped when context manager exits
console.print()
console.rule("[bold blue]ENGLISH[/bold blue]")
console.print(en_post)
console.print()
console.rule("[bold green]PORTUGUES[/bold green]")
console.print(pt_post)
```

### Emoji Validation with Retry
```python
# Source: emoji library - https://pypi.org/project/emoji/
import emoji

def contains_emoji(text: str) -> bool:
    return emoji.replace_emoji(text, replace='') != text

def validate_and_retry(text: str, lang: str, max_retries: int = 2) -> tuple[str, bool]:
    """Returns (text, passed_validation)."""
    for attempt in range(max_retries):
        if not contains_emoji(text):
            return text, True
        # Re-generate silently
        text = regenerate(lang)
    # After max retries, return last attempt with failure flag
    return text, False
```

### Saving Posts with Front-Matter
```python
# Source: python-frontmatter docs - https://pypi.org/project/python-frontmatter/
import frontmatter
from pathlib import Path
from datetime import datetime
from slugify import slugify

def save_post(topic: str, en_text: str, pt_text: str, format_type: str):
    now = datetime.now()
    slug = slugify(topic, max_length=60)
    dir_path = Path("posts") / now.strftime("%Y-%m")
    dir_path.mkdir(parents=True, exist_ok=True)

    post = frontmatter.Post(
        content=f"## English\n\n{en_text}\n\n## Portugues\n\n{pt_text}",
        handler=frontmatter.YAMLHandler(),
    )
    post.metadata.update({
        "date": now.isoformat(),
        "topic": topic,
        "format": format_type,
        "languages": ["en", "pt"],
    })

    file_path = dir_path / f"{slug}.md"
    frontmatter.dump(post, str(file_path))
    return file_path
```

### Listing Saved Posts
```python
import frontmatter
from pathlib import Path
from rich.table import Table
from rich.console import Console

def list_posts():
    console = Console()
    posts_dir = Path("posts")
    if not posts_dir.exists():
        console.print("[yellow]No posts yet.[/yellow]")
        return

    table = Table(title="Saved Posts")
    table.add_column("Date", style="cyan")
    table.add_column("Topic", style="white")
    table.add_column("Format", style="green")
    table.add_column("File", style="dim")

    for md_file in sorted(posts_dir.rglob("*.md"), reverse=True):
        post = frontmatter.load(str(md_file))
        table.add_row(
            post.get("date", "?")[:10],
            post.get("topic", "?"),
            post.get("format", "?"),
            str(md_file),
        )

    console.print(table)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Anthropic completions API | Messages API (`client.messages.create`) | 2024 | Messages API is the only supported interface; completions is deprecated |
| Prefilling assistant responses | System prompt instructions + structured outputs | 2025 | Prefilling deprecated on Claude Sonnet 4.5+; use system prompt instead |
| LangChain wrappers | Direct Anthropic SDK | Ongoing | For single-provider usage, direct SDK is simpler and more predictable |

**Deprecated/outdated:**
- `anthropic.completions` API: Fully deprecated, use `messages.create()`
- Prefilling (putting words in Claude's mouth): Deprecated on newer models (Claude Sonnet 4.5+, Opus), use system prompt instructions instead

## Open Questions

1. **Model selection for cost vs. quality**
   - What we know: Claude Sonnet is cheaper and faster; Claude Opus is higher quality
   - What's unclear: Whether Sonnet is sufficient for consistent tone adherence and format compliance
   - Recommendation: Start with `claude-sonnet-4-20250514` for cost efficiency; make the model name configurable in `config.py` so it can be upgraded easily

2. **PT one-shot example quality**
   - What we know: The CONTEXT.md contains a candidate example that needs user review
   - What's unclear: Whether the candidate example accurately represents the user's voice
   - Recommendation: Use the candidate example as a starting placeholder; flag for user review before Phase 1 execution begins

3. **Token counting for history truncation**
   - What we know: The Anthropic SDK has a `client.count_tokens()` method (or similar)
   - What's unclear: Exact API for token counting in current SDK version
   - Recommendation: Use character-based estimation (4 chars ~= 1 token) for the initial implementation; upgrade to SDK token counting if available

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.x |
| Config file | none -- see Wave 0 |
| Quick run command | `pytest tests/ -x -q` |
| Full suite command | `pytest tests/ -v` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CLI-01 | REPL session with history tracking | integration | `pytest tests/test_repl.py -x` | No -- Wave 0 |
| CLI-02 | Command dispatch (/new, /refine, /save, /list) | unit | `pytest tests/test_commands.py -x` | No -- Wave 0 |
| CLI-04 | Formatted post preview in terminal | unit | `pytest tests/test_display.py -x` | No -- Wave 0 |
| GEN-01 | Format selection produces structurally distinct output | unit | `pytest tests/test_prompts.py -x` | No -- Wave 0 |
| GEN-02 | Independent EN + PT generation | integration | `pytest tests/test_generation.py -x` | No -- Wave 0 |
| GEN-03 | Emoji detection + auto retry | unit | `pytest tests/test_validator.py -x` | No -- Wave 0 |
| GEN-04 | Voice consistency via system prompt | integration | `pytest tests/test_generation.py::test_voice -x` | No -- Wave 0 |
| OUT-01 | Save post as .md with front-matter | unit | `pytest tests/test_storage.py -x` | No -- Wave 0 |
| OUT-02 | List posts from disk | unit | `pytest tests/test_storage.py::test_list_posts -x` | No -- Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/ -x -q`
- **Per wave merge:** `pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/conftest.py` -- shared fixtures (mock Anthropic client, temp posts directory)
- [ ] `tests/test_validator.py` -- covers GEN-03 (emoji detection, retry logic)
- [ ] `tests/test_storage.py` -- covers OUT-01, OUT-02 (save, list)
- [ ] `tests/test_commands.py` -- covers CLI-02 (command parsing)
- [ ] `tests/test_prompts.py` -- covers GEN-01 (format-specific prompt construction)
- [ ] `tests/test_display.py` -- covers CLI-04 (rich formatting output)
- [ ] `tests/test_generation.py` -- covers GEN-02, GEN-04 (API integration, voice)
- [ ] `tests/test_repl.py` -- covers CLI-01 (session history)
- [ ] `pytest.ini` or `pyproject.toml` [tool.pytest] section
- [ ] Framework install: `pip install pytest pytest-mock` -- no test infrastructure exists yet

## Sources

### Primary (HIGH confidence)
- [Anthropic Messages API examples](https://platform.claude.com/docs/en/api/messages-examples) -- multi-turn conversation pattern, system prompt usage, streaming
- [PyPI anthropic 0.86.0](https://pypi.org/project/anthropic/) -- verified latest version
- [PyPI prompt-toolkit 3.0.52](https://pypi.org/project/prompt-toolkit/) -- verified latest version
- [PyPI rich 14.3.3](https://pypi.org/project/rich/) -- verified latest version
- [rich spinner docs](https://rich.readthedocs.io/en/stable/reference/spinner.html) -- spinner/status API
- [PyPI python-frontmatter 1.1.0](https://pypi.org/project/python-frontmatter/) -- verified latest version
- [PyPI python-slugify 8.0.4](https://pypi.org/project/python-slugify/) -- verified latest version
- [PyPI emoji 2.15.0](https://pypi.org/project/emoji/) -- verified latest version

### Secondary (MEDIUM confidence)
- [prompt-toolkit REPL tutorial](https://github.com/prompt-toolkit/python-prompt-toolkit/blob/main/docs/pages/tutorials/repl.rst) -- REPL patterns
- [python-prompt-toolkit docs](https://python-prompt-toolkit.readthedocs.io/) -- PromptSession API

### Tertiary (LOW confidence)
- Token counting API availability in anthropic SDK 0.86.0 -- could not verify exact method name; character estimation recommended as fallback

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all packages verified on PyPI with current versions, well-established libraries
- Architecture: HIGH -- patterns based on official Anthropic docs and standard Python CLI practices
- Pitfalls: HIGH -- based on known LLM integration patterns and Messages API behavior documented by Anthropic
- Validation: MEDIUM -- test structure is standard pytest but no infrastructure exists yet

**Research date:** 2026-03-20
**Valid until:** 2026-04-20 (stable ecosystem, 30-day validity)
