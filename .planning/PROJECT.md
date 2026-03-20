# LinkedIn AI Copywriter

## What This Is

CLI tool that acts as a personal LinkedIn copywriter for an AI engineer targeting US recruiters. It researches AI news daily, ingests a personal knowledge base (PDFs/PPTXs), generates professional posts in English and Portuguese, and saves them as structured Markdown files. All interaction happens in the terminal via a conversational loop.

## Core Value

Generate authoritative, professional AI posts that position the user as a trusted "AI translator" — someone who understands the technical depth and can communicate it clearly — attracting US tech recruiters.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Terminal chat interface for end-to-end post creation workflow
- [ ] AI news research: tool discovers relevant AI news and suggests post topics
- [ ] Knowledge base ingestion: user provides PDFs/PPTXs as personal context for technical posts
- [ ] Post generation in three formats: short text (300-600 chars), long/carousel (sections), hook + breakdown
- [ ] Bilingual output: every post generated in both English and Portuguese
- [ ] Refinement loop: user can request changes conversationally until satisfied
- [ ] Posts saved as .md files in organized folder structure (e.g. posts/YYYY-MM/slug.md)
- [ ] Writing rules enforced: no emojis in post text, no sensationalist/clickbait language
- [ ] "Tradutor de IA" voice: technical depth made accessible, not dumbed down

### Out of Scope

- Web/frontend UI — terminal only
- Social media API integration (auto-posting) — user copies/pastes manually
- Analytics or engagement tracking — outside scope of this tool
- Multi-user support — personal tool for one user

## Context

- User is an AI engineer with 2 years of experience
- Primary goal: visibility with US tech recruiters
- Audience for posts: non-engineer recruiters who hire engineers, plus peers in the field
- Tone: professional authority, no hype, no emojis — substance over performance
- The tool must feel like a thinking partner, not a content mill

## Constraints

- **Interface**: Terminal/CLI only — no web server, no GUI
- **Language**: Python preferred (AI ecosystem tooling)
- **Output**: Posts as `.md` files, folder structure by date (posts/YYYY-MM/slug.md)
- **Tone rules**: No emojis in generated post text; no clickbait or sensationalist hooks

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| CLI only, no frontend | User explicitly requested terminal interface | — Pending |
| Bilingual output (EN + PT) | Targets US recruiters but user also has PT audience | — Pending |
| PDF/PPTX knowledge base | User has existing materials to ground technical posts | — Pending |
| Posts saved as .md files | Persistent, portable, version-controllable output | — Pending |

---
*Last updated: 2026-03-20 after initialization*
