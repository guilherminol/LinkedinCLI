# Feature Research

**Domain:** CLI-based LinkedIn AI copywriter for personal branding (AI engineer targeting US recruiters)
**Researched:** 2026-03-20
**Confidence:** HIGH (table stakes), MEDIUM (differentiators), HIGH (anti-features)

---

## Feature Landscape

### Table Stakes (Users Expect These)

Features that must exist for the tool to be functional. Missing any of these makes the tool feel broken or incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Conversational input for post creation | User must be able to describe what they want in natural language — a pure form-fill is not a writing partner | LOW | Simple REPL loop with streaming LLM response |
| Post generation from topic prompt | Core function: give topic, get post draft | LOW | Single LLM call with structured system prompt |
| Multiple post format support | LinkedIn has distinct formats (short text, carousel-style sections, hook+breakdown) with different algorithms performance; tool must match real platform formats | MEDIUM | Needs format-routing logic and per-format prompt templates |
| Refinement loop | User expects to say "make it shorter" or "change the opening" and get an updated draft; one-shot generation is not enough | MEDIUM | Maintain conversation context, apply targeted edits |
| File output as .md | Output must persist — copying to clipboard and losing it is not acceptable for a personal-branding workflow | LOW | Write to `posts/YYYY-MM/slug.md` with front matter |
| Writing rules enforcement | No emojis, no clickbait hooks — these are the primary differentiators in tone; a tool that ignores them produces unusable output | MEDIUM | System prompt constraints + post-generation validation pass |
| Knowledge base ingestion (PDF/PPTX) | User has existing technical materials; grounding posts in personal expertise prevents generic AI output | HIGH | RAG pipeline: parse, chunk, embed, retrieve at generation time |
| AI news research / topic discovery | Tool must find relevant AI news so user has fresh topics; without this, it's just a text formatter | HIGH | Web search or RSS aggregation + LLM summarization to suggest angles |
| Bilingual output (EN + PT) | User explicitly requires English and Portuguese; missing PT means the tool cannot serve the full stated use case | MEDIUM | Generate EN first, then PT in same session; or parallel generation |

### Differentiators (Competitive Advantage)

Features that set this personal tool apart from SaaS tools like Taplio, ContentIn, and EasyGen. These align with the "AI translator" positioning.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Personal knowledge base as grounding source | Competitors generate from generic context; this tool generates posts that reference the user's actual talks, PDFs, and projects — making content irreproducibly personal | HIGH | RAG retrieval surfaces specific claims, stats, or frameworks the user has authored; competitors do not support this |
| "AI translator" voice enforcement | A defined persona — technical depth made accessible, no hype, no dumbing down — produces a consistent, recognizable author voice across all posts. Competitors let users pick a generic tone slider. | MEDIUM | System prompt with detailed persona specification; validated against no-emoji and no-sensationalism rules |
| CLI-first zero-distraction workflow | All SaaS competitors are browser-based with dashboards, notifications, and upsell modals. Terminal interaction means the user stays in their environment, no account required, no context-switching | LOW | This is architectural, not a feature to build — it falls out of the CLI design choice |
| Structured post file library | Posts saved as versioned .md files in `posts/YYYY-MM/` are grep-able, diff-able, and git-trackable. No competitor produces a local portable archive of your content history | LOW | File naming with slug + date; optionally front matter with topic, format, language |
| Topic suggestion from real news | Tool proposes post angles based on current AI news, not template prompts. User does not have to source their own topics. This is active rather than passive. | HIGH | Requires web search integration (e.g., Brave Search or RSS feeds) and LLM summarization step |
| Same-session bilingual generation | EN and PT versions produced in the same refinement session, so changes made in refinement are applied consistently to both languages. Competitors either do not offer multilingual or require separate runs. | MEDIUM | After EN draft is approved, generate PT adaptation (not direct translation — culturally adapted) |
| No account, no cloud, local execution | No credentials for a SaaS, no data sent to a third-party content platform — only LLM API calls. Personal branding content is sensitive; local-first is a trust differentiator | LOW | Falls out of the Python CLI architecture; note in documentation |

### Anti-Features (Deliberately NOT Built)

Features commonly found in LinkedIn tools that would actively harm this product's goals.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Auto-posting to LinkedIn via API | Convenient, reduces manual steps | LinkedIn API is enterprise-gated and has strict usage policies; getting access for a personal tool is non-trivial. More importantly, manual copy-paste creates a review checkpoint that prevents accidentally posting AI drafts verbatim — a real professional risk | User pastes final draft manually; tool's job ends at file output |
| Emoji insertion in post text | Emojis increase visual engagement on most LinkedIn posts | This user's explicit brand positioning is anti-emoji for authority signaling in technical domains. A tool that inserts emojis trains the user to accept them. The constraint is the brand. | Enforced via system prompt constraints; validation step flags any emoji in output |
| Engagement-bait hook templates | "5 reasons why...", "Nobody talks about this...", "I was shocked when..." — these are high-click patterns | These hooks signal low-quality AI-generated content. LinkedIn's 2025 algorithm update explicitly downgrades content detected as low-value AI generation. US tech recruiters reading technical content are sophisticated enough to be repelled by them. | System prompt defines the "AI translator" hook pattern: lead with the insight, not the reaction |
| Hashtag generation | Every LinkedIn post generator adds hashtags | More than 5 hashtags is treated as spam by LinkedIn's algorithm. Auto-generated hashtags are typically generic (#AI #MachineLearning #Innovation). They add noise without helping niche discoverability. | If user wants hashtags, they add them manually after reviewing the draft |
| Posting schedule / calendar management | Taplio and ContentIn make this a core feature | This is a personal tool, not a social media management dashboard. Building a calendar requires state management, notification systems, and a persistence layer that adds weeks of complexity for zero content quality improvement. | User manages their own posting cadence; tool's scope is content quality, not scheduling |
| Analytics / engagement tracking | Knowing what performs helps improve future content | Requires LinkedIn API integration (enterprise access) or scraping (ToS violation). The tool cannot reliably measure this. Any analytics would be fake precision. | User observes LinkedIn's native analytics; insights inform future topic choices given to the tool |
| Multi-user / team support | Agencies and teams might want to use this | This is a personal tool built around one voice, one knowledge base, one persona. Multi-user support requires authentication, isolated knowledge bases, billing — a completely different product category. | If team use is needed, fork and adapt; the architecture should not be generalized for this |
| Web UI / browser interface | More accessible for non-terminal users | Terminal interaction IS the product decision. A web UI requires a server, hosting, auth — and eliminates the zero-distraction, no-account, local-first properties that differentiate this from SaaS alternatives | Terminal only; no Flask/FastAPI server, no React frontend |
| Voice note input | EasyGen differentiates on voice dictation | Adds audio processing dependency (Whisper or similar), increases latency, and adds a library dependency chain that complicates setup. Low value for a user who is already comfortable in a terminal. | Text prompt input is sufficient; user can transcribe voice notes before inputting |

---

## Feature Dependencies

```
[AI News Research]
    └──enables──> [Topic Suggestion]
                      └──feeds──> [Post Generation]

[Knowledge Base Ingestion (PDF/PPTX)]
    └──enables──> [RAG Retrieval]
                      └──enhances──> [Post Generation]
                                         └──enables──> [Refinement Loop]
                                                            └──enables──> [Bilingual Output]
                                                                               └──enables──> [File Output (.md)]

[Writing Rules Enforcement] ──applies-to──> [Post Generation]
[Writing Rules Enforcement] ──applies-to──> [Refinement Loop]
[Writing Rules Enforcement] ──applies-to──> [Bilingual Output]

[Post Generation] ──requires──> [Format Selection (short/carousel/hook+breakdown)]
```

### Dependency Notes

- **Post Generation requires Format Selection:** The prompt template, length constraints, and structure differ fundamentally between a 300-char short post and a carousel-style sectioned post. Format must be determined before generation begins.
- **Refinement Loop requires Post Generation:** Refinement has no meaning without an existing draft. Must be built after generation is working.
- **Bilingual Output requires Refinement Loop to be complete:** Generating the PT version before the EN version is approved wastes tokens and creates inconsistency. PT should be generated after EN is finalized.
- **RAG Retrieval requires Knowledge Base Ingestion:** Ingestion (parsing, chunking, embedding) must run at least once before retrieval is available. This is a setup step, not a per-run step.
- **Topic Suggestion requires AI News Research:** Without a news source, topic suggestion falls back to generic LLM suggestions — which defeats the "current AI news" value proposition.
- **File Output requires Post Generation and Refinement Loop:** Writing to disk should happen after the user confirms the draft, not before.
- **Writing Rules Enforcement conflicts with emoji/clickbait output:** These constraints must be baked into system prompts and validated after generation — they cannot be added as an afterthought without risking output quality degradation.

---

## MVP Definition

### Launch With (v1)

The minimum to validate the core loop: user provides topic, gets a professional post in both languages, saves it.

- [ ] Terminal conversational interface (input loop, streaming output) — without this, there is no tool
- [ ] Post generation in three formats (short text, long/carousel, hook+breakdown) — format variety is table stakes per project requirements
- [ ] Writing rules enforcement (no emoji, no clickbait) — core brand differentiator; cannot be deferred
- [ ] Refinement loop — one-shot generation with no editing is unusable for real content work
- [ ] Bilingual output (EN + PT) — explicitly required; EN-only is an incomplete product for this user
- [ ] File output to `posts/YYYY-MM/slug.md` — without persistence, there is no content library

### Add After Validation (v1.x)

Add once the generation loop is proven to work and produce quality output.

- [ ] Knowledge base ingestion (PDF/PPTX) — high value but high setup cost; validate that base generation is good first, then layer in personal grounding
- [ ] AI news research / topic suggestion — high value for daily use; depends on web search integration which adds API and rate-limit complexity

### Future Consideration (v2+)

Defer until core use case is established.

- [ ] Knowledge base incremental updates (add new PDFs without re-indexing everything) — optimization; v1 can re-index on each run
- [ ] Post tagging / search across saved posts — useful for building on past content; requires indexing the `posts/` directory
- [ ] Topic history to avoid repetition — prevents re-generating posts on the same subject; requires tracking what was previously written

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Conversational input loop | HIGH | LOW | P1 |
| Post generation (all three formats) | HIGH | MEDIUM | P1 |
| Writing rules enforcement | HIGH | LOW | P1 |
| Refinement loop | HIGH | MEDIUM | P1 |
| Bilingual output (EN + PT) | HIGH | MEDIUM | P1 |
| File output (.md with folder structure) | HIGH | LOW | P1 |
| Knowledge base ingestion (RAG) | HIGH | HIGH | P2 |
| AI news research / topic suggestion | HIGH | HIGH | P2 |
| Structured post file library / searchable archive | MEDIUM | LOW | P3 |
| Topic history / deduplication | MEDIUM | LOW | P3 |

**Priority key:**
- P1: Must have for launch
- P2: Should have, add after core loop is validated
- P3: Nice to have, future consideration

---

## Competitor Feature Analysis

| Feature | Taplio ($39-199/mo) | ContentIn ($15/mo) | EasyGen ($60/mo) | This Tool |
|---------|---------------------|---------------------|------------------|-----------|
| Post generation | Yes, generic voice | Yes, mimics past posts | Yes, trained on top posts | Yes, personal knowledge base grounded |
| Personal voice | Style settings | Ghostwriter from past posts | Voice notes + style | Enforced persona (AI translator) + RAG |
| Carousel / format support | Yes | Yes | Limited | Yes, three formats |
| Scheduling | Yes | Yes | No | Explicitly out of scope |
| Analytics | Yes | Yes | No | Explicitly out of scope |
| Bilingual output | No | No | No | Yes (EN + PT, same session) |
| PDF / PPTX knowledge base | No | No | No | Yes (core differentiator) |
| CLI / terminal interface | No | No | No | Yes (only interface) |
| No-emoji enforcement | No | No | No | Yes (system-level constraint) |
| No clickbait enforcement | No | No | No | Yes (system-level constraint) |
| AI news topic suggestion | Limited (trend signals) | No | Yes (trend signals) | Yes (real-time research) |
| Local file output (.md) | No | No | No | Yes (posts/YYYY-MM/slug.md) |
| No account required | No | No | No | Yes (local-first) |

---

## Sources

- [Top 11 AI LinkedIn Post Generator Tools Compared (2026) — ContentIn](https://contentin.io/blog/best-ai-linkedin-post-generators/) — competitor feature landscape
- [Taplio vs Buffer vs EasyGen: Ultimate LinkedIn Tool Comparison — AutoPosting.ai](https://autoposting.ai/taplio-vs-buffer-vs-easygen/) — pricing and feature comparison
- [ContentIn vs EasyGen: Full Comparison 2026 — ContentIn](https://contentin.io/vs/easygen/) — feature-level detail
- [LinkedIn Carousel Posts: Ultimate Professional Guide for 2025 — PostNitro](https://postnitro.ai/blog/post/linkedin-carousel-posts-ultimate-professional-guide-for-2025) — carousel format performance data (24.42% engagement rate, 77% tech audience preference)
- [LinkedIn Content Strategy 2025-2026: What Actually Works — Postiv AI](https://postiv.ai/blog/linkedin-content-strategy-2025) — algorithm behavior, content pitfalls
- [LinkedIn Personal Branding: How to Build Authority — Cleverly](https://www.cleverly.co/blog/linkedin-personal-branding) — recruiter visibility strategy
- [Build a Personal RAG Knowledge Base for Your AI Assistant — Claw.ist](https://claw.ist/rag-ai-knowledge-base-tutorial) — RAG for personal knowledge base pattern
- [RAG-Anything: All-in-One RAG Framework — GitHub](https://github.com/HKUDS/RAG-Anything) — multimodal document ingestion including PPTX
- [How the LinkedIn algorithm works (2025 Update) — SourceGeek](https://www.sourcegeek.com/en/news/how-the-linkedin-algorithm-works-2025-update) — algorithm signals including emoji and hashtag behavior
- [10 Best Multilingual LLMs for 2026 — Azumo](https://azumo.com/artificial-intelligence/ai-insights/multilingual-llms) — EN/PT LLM quality assessment

---
*Feature research for: LinkedIn AI Copywriter CLI — personal branding tool for AI engineer targeting US recruiters*
*Researched: 2026-03-20*
