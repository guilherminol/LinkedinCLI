# Phase 1: Core Generation Loop - Context

**Gathered:** 2026-03-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Conversational CLI that lets the user open a terminal, type a topic, generate bilingual (EN + PT) LinkedIn posts in any of three formats, refine them conversationally, and save approved posts to disk — with writing rules enforced on every generation.

Creating posts is the only capability. News research (Phase 3) and knowledge base RAG (Phase 2) are out of scope here.

</domain>

<decisions>
## Implementation Decisions

### Post Format Specs

**Short text:**
- Length: 300–600 characters of prose
- Structure: Single block (no headers, no bullets)
- Ends with a CTA generated fresh by the LLM each time (fitted to the specific post — not templated)

**Carousel / long-form:**
- Structure: 3–5 sections, each with a bold header + 2–4 sentences
- Total length: ~800–1,500 characters
- Designed to read as a multi-slide carousel

**Hook + breakdown:**
- Structure: Rhetorical question hook → 2–3 short prose paragraphs answering it
- Hook is a question that the rest of the post resolves
- Conversational, not listicle

### Portuguese Voice Spec

- **Audience:** Brazilian tech professionals and recruiters (not neutral PT, not European PT)
- **Loanword rule:** Established tech terms stay in English — fine-tuning, embedding, benchmark, prompt, token, fine-tuning, RAG, LLM — only translate when a natural BR Portuguese equivalent exists and is commonly used
- **Content relationship to EN:** Same topic and key points, independently phrased for a BR audience — NOT a sentence-by-sentence translation. Tone, framing, and phrasing are adapted for BR readers
- **System prompt:** Must include a PT-specific one-shot example (see Specific Ideas below)

### REPL Session Flow

- **Session start:** Brief welcome line + blank prompt — e.g., `LinkedIn Copywriter → type a topic or /help`
- **Post display:** EN block first, then PT block, separated by labeled dividers:
  `── ENGLISH ──` and `── PORTUGUÊS ──`
- **Refinements:** Apply to both EN and PT simultaneously — one instruction updates both languages
- **Progress feedback:** Animated spinner with sequential status messages:
  `Generating EN post...` → `Generating PT post...` → `Done`

### Writing Rule Enforcement

- **Blocked content:** Emojis only — detected via regex/unicode range check. No explicit phrase blocklist; tone control is via system prompt
- **Violation response:** Auto re-generate silently (user never sees the violating draft). Max 2 retries per language
- **After 2 retries:** Show error message `Failed to generate clean post after 2 retries — showing last attempt` + raw output. User can refine manually
- **Check scope:** EN and PT outputs are checked independently. Both must pass before the pair is shown. If only PT fails, only PT is re-generated

### SDK and Architecture

- Use Anthropic SDK directly — **do not use LangChain** (pre-phase decision from research)
- Per-turn rule injection: prepend a short rule block to every LLM call enforcing tone rules
- Post-generation blocked vocabulary check (emoji regex) runs after every generation call

### Claude's Discretion

- Exact spinner animation library / implementation
- Session history format in memory (how the REPL tracks conversation context internally)
- Exact welcome message wording
- Slug generation logic for the `.md` filename

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements

- `.planning/REQUIREMENTS.md` — Full requirement list for Phase 1: CLI-01, CLI-02, CLI-04, GEN-01, GEN-02, GEN-03, GEN-04, OUT-01, OUT-02. Contains acceptance criteria and traceability.

### Project context

- `.planning/PROJECT.md` — Voice guidelines, tone rules, audience definition, key decisions table

No external specs or ADRs — requirements are fully captured in the documents above and in the decisions section.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

None — fresh project with no existing code. A `.env` file exists at project root (empty).

### Established Patterns

None yet — Phase 1 establishes the patterns for subsequent phases.

### Integration Points

- Phase 1 output (`posts/YYYY-MM/slug.md` + front-matter metadata) is consumed by Phase 3 for deduplication (OUT-03)
- Phase 2 will add RAG context injection into the generation call established in Phase 1

</code_context>

<specifics>
## Specific Ideas

### PT one-shot example (candidate — edit before use)

```
Tópico: Fine-tuning vs. prompt engineering

Fine-tuning parece a solução óbvia quando um modelo não performa bem. Mas a maioria dos problemas que parecem exigir fine-tuning são, na prática, problemas de prompt engineering. Fine-tuning custa tempo, dinheiro e dados anotados — e muitas vezes um prompt bem construído resolve em minutos. Antes de treinar, pergunte: o modelo falha porque não sabe a tarefa, ou porque não recebeu as instruções certas? Compartilhe sua experiência nos comentários.
```

This is a candidate example drafted from voice spec decisions. Review and replace with a real post written in your own voice before Phase 1 executes.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 01-core-generation-loop*
*Context gathered: 2026-03-20*
