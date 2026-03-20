# Roadmap: LinkedIn AI Copywriter

## Overview

Four phases that build sequentially: first a working conversational CLI that generates quality bilingual posts (the minimum viable product), then a personal knowledge base via RAG, then AI news research and topic discovery, and finally a hardening pass to ensure tone rules hold across multi-turn sessions and all integrations behave reliably. Each phase delivers something immediately usable; later phases enhance without changing the core loop.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Core Generation Loop** - Conversational CLI that generates, refines, and saves bilingual posts with enforced writing rules
- [ ] **Phase 2: Knowledge Base Pipeline** - Personal PDF/PPTX documents ingested into a local vector store and retrieved during post generation
- [ ] **Phase 3: News Research Integration** - AI news searched via Tavily, suggested as topics at session start, with deduplication against prior posts
- [ ] **Phase 4: Hardening and Polish** - Multi-turn tone rule persistence verified, RAG retrieval quality confirmed, UX roughness removed

## Phase Details

### Phase 1: Core Generation Loop
**Goal**: Users can open a terminal, have a conversational session, generate posts in all three formats in both languages, refine them conversationally, and save approved posts to disk — with writing rules enforced on every generation.
**Depends on**: Nothing (first phase)
**Requirements**: CLI-01, CLI-02, CLI-04, GEN-01, GEN-02, GEN-03, GEN-04, OUT-01, OUT-02
**Success Criteria** (what must be TRUE):
  1. User can start a session, type a topic, and receive a fully formatted EN + PT post pair in the terminal without any manual prompt engineering
  2. User can request changes conversationally ("make it shorter", "less formal") and receive a revised post that keeps prior context
  3. User can select any of the three formats (short text, carousel/sections, hook+breakdown) and receive structurally distinct output for each
  4. User can type `/save` and find a correctly named `.md` file at `posts/YYYY-MM/slug.md` with front-matter metadata
  5. Generated posts never contain emojis or clickbait phrases — validated on every generation, with a re-generation triggered automatically on violation
**Plans:** 4 plans
Plans:
- [ ] 01-01-PLAN.md — Project scaffolding, prompts, and emoji validator (GEN-01, GEN-03, GEN-04)
- [ ] 01-02-PLAN.md — Output storage layer: save and list posts (OUT-01, OUT-02)
- [ ] 01-03-PLAN.md — Generation engine: bilingual Anthropic API client (GEN-02, CLI-04)
- [ ] 01-04-PLAN.md — CLI REPL, commands, display, and end-to-end wiring (CLI-01, CLI-02)

### Phase 2: Knowledge Base Pipeline
**Goal**: Users can drop their technical PDFs and PPTXs into a `knowledge/` folder, run an ingest command, and have subsequent post generation automatically pull relevant context from those documents.
**Depends on**: Phase 1
**Requirements**: KB-01, KB-02, KB-03, KB-04
**Success Criteria** (what must be TRUE):
  1. User can place files in `knowledge/` and run an ingest command that processes all PDFs and PPTXs without errors or silent data loss
  2. When generating a technical post, the CLI displays which knowledge base chunks were retrieved and used as context
  3. Re-running ingest after adding new files only processes changed files — existing indexed content is not duplicated
  4. RAG retrieval returns semantically relevant chunks: a query about "fine-tuning LLMs" retrieves slides/pages about fine-tuning, not unrelated content
**Plans**: TBD

### Phase 3: News Research Integration
**Goal**: Users open a session and immediately see suggested AI news topics pulled from authoritative sources, can pick one to generate a post, and the tool avoids suggesting topics that already have posts in the library.
**Depends on**: Phase 2
**Requirements**: CLI-03, NEWS-01, OUT-03
**Success Criteria** (what must be TRUE):
  1. At session start, the tool automatically displays 3-5 current AI news topics from trusted sources (arXiv, HuggingFace, OpenAI blog, Anthropic blog) with source title and date
  2. User can select a suggested topic and immediately generate a post grounded in the news article content
  3. Topics for which a post already exists in `posts/` are not suggested again — the tool checks existing post metadata before surfacing suggestions
**Plans**: TBD

### Phase 4: Hardening and Polish
**Goal**: The tool behaves reliably under real-world usage conditions — tone rules hold across long refinement sessions, RAG retrieval is manually verified as relevant, Portuguese output quality matches English quality, and the UX has no rough edges.
**Depends on**: Phase 3
**Requirements**: (no new requirements — validates and hardens all prior phases)
**Success Criteria** (what must be TRUE):
  1. After 5+ refinement turns on the same post, generated content still contains no emojis, no clickbait hooks, and no hype phrases — tone rules persist across the full conversation
  2. Portuguese posts read as independently authored content for a Brazilian Portuguese AI audience, not as translations — loanwords like "fine-tuning", "embedding", and "benchmark" remain in English
  3. The CLI provides visual progress feedback (spinner, source attribution, EN/PT section separators) so users always know what the tool is doing and where output begins
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Core Generation Loop | 0/4 | Planning complete | - |
| 2. Knowledge Base Pipeline | 0/TBD | Not started | - |
| 3. News Research Integration | 0/TBD | Not started | - |
| 4. Hardening and Polish | 0/TBD | Not started | - |
