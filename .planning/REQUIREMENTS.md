# Requirements: LinkedIn AI Copywriter

**Defined:** 2026-03-20
**Core Value:** Generate authoritative, professional AI posts in EN and PT that position the user as a trusted "AI translator" — attracting US tech recruiters without hype, emojis, or clickbait.

## v1 Requirements

### CLI

- [ ] **CLI-01**: User can interact via a conversational REPL with session history
- [ ] **CLI-02**: User can use `/new`, `/refine`, `/save`, `/list` commands to navigate the post creation workflow
- [ ] **CLI-03**: Tool automatically suggests AI news topics at session start
- [ ] **CLI-04**: User sees a formatted post preview in the terminal before saving

### Generation

- [x] **GEN-01**: User can choose post format — short text (300-600 chars), carousel/sections (long-form), or hook+breakdown
- [ ] **GEN-02**: Every post is generated simultaneously in English and Portuguese (independent generation, not translation)
- [x] **GEN-03**: Generated posts enforce no-emoji and no-clickbait rules automatically — validated on every generation via post-processing check
- [x] **GEN-04**: All posts follow a consistent "AI translator" voice — technical depth made accessible to non-engineer readers

### Knowledge Base

- [ ] **KB-01**: User places PDF and PPTX files in a designated `knowledge/` folder for automatic ingestion
- [ ] **KB-02**: Tool ingests PDFs with semantic chunking (paragraph/heading-based) into ChromaDB local vector store
- [ ] **KB-03**: Tool ingests PPTX with slide-level chunking (1 slide = minimum 1 chunk) into ChromaDB
- [ ] **KB-04**: Technical post generation automatically retrieves relevant context from the knowledge base (RAG)

### News

- [ ] **NEWS-01**: Tool searches for current AI news via Tavily, restricted to trusted sources (arXiv, HuggingFace, OpenAI blog, Anthropic blog, etc.)

### Output

- [x] **OUT-01**: Posts saved as `.md` files at `posts/YYYY-MM/slug.md` with front-matter metadata (date, format, language, topic)
- [x] **OUT-02**: User can list previously generated posts with `/list` command
- [ ] **OUT-03**: Tool avoids re-suggesting topics already covered in previous posts by checking existing post metadata

## v2 Requirements

### CLI Enhancements

- **CLI-V2-01**: `/ingest <file>` command for explicit single-file ingestion outside the knowledge/ folder
- **CLI-V2-02**: Session auto-save and restore across terminal restarts

### Generation Enhancements

- **GEN-V2-01**: User can define and switch between multiple voice profiles
- **GEN-V2-02**: Post scoring/quality feedback before saving

### Output Enhancements

- **OUT-V2-01**: Export posts to clipboard directly from terminal
- **OUT-V2-02**: Post tagging and search across saved posts

## Out of Scope

| Feature | Reason |
|---------|--------|
| Web/frontend UI | Terminal-only by design |
| LinkedIn API auto-posting | User copies/pastes manually; API adds OAuth complexity |
| Post scheduling | Out of scope — tool generates, user decides when to post |
| Analytics / engagement tracking | External to the tool's purpose |
| Multi-user support | Personal tool for one user |
| Auto-emoji or hashtag injection | Explicitly excluded per writing rules |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| CLI-01 | Phase 1 | Pending |
| CLI-02 | Phase 1 | Pending |
| CLI-03 | Phase 3 | Pending |
| CLI-04 | Phase 1 | Pending |
| GEN-01 | Phase 1 | Complete |
| GEN-02 | Phase 1 | Pending |
| GEN-03 | Phase 1 | Complete |
| GEN-04 | Phase 1 | Complete |
| KB-01 | Phase 2 | Pending |
| KB-02 | Phase 2 | Pending |
| KB-03 | Phase 2 | Pending |
| KB-04 | Phase 2 | Pending |
| NEWS-01 | Phase 3 | Pending |
| OUT-01 | Phase 1 | Complete |
| OUT-02 | Phase 1 | Complete |
| OUT-03 | Phase 3 | Pending |

**Coverage:**
- v1 requirements: 16 total
- Mapped to phases: 16
- Unmapped: 0

---
*Requirements defined: 2026-03-20*
*Last updated: 2026-03-20 after roadmap creation — traceability confirmed against ROADMAP.md*
