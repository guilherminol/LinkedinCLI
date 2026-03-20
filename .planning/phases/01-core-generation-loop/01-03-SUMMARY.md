---
phase: 01-core-generation-loop
plan: 03
subsystem: generation
tags: [anthropic, bilingual, conversation-history, emoji-validation, retry]

# Dependency graph
requires:
  - phase: 01-core-generation-loop
    plan: 01
    provides: "prompts.py (EN/PT system prompts, build_generation_prompt), validator.py (validate_post, contains_emoji), config.py (constants)"
provides:
  - "PostGenerator class with generate_pair() and refine() methods"
  - "GenerationResult dataclass (en_text, pt_text, topic, format_key, en_passed, pt_passed)"
  - "Independent EN/PT conversation histories with truncation"
affects: [01-04-cli-repl]

# Tech tracking
tech-stack:
  added: []
  patterns: ["Independent bilingual API calls (never translation)", "Per-language emoji retry with validator integration", "History truncation at HISTORY_SOFT_CAP pairs"]

key-files:
  created:
    - src/linkedin_poster/generation/client.py
    - tests/test_generation.py
  modified: []

key-decisions:
  - "Truncate history after both user and assistant appends to ensure stored history never exceeds cap"
  - "Regenerate removes last assistant message and re-calls API with same history (no new user message)"

patterns-established:
  - "Independent EN/PT generation: two separate API calls, separate histories, never pass EN output to PT"
  - "Validator integration: validate_post wraps regenerate lambda for per-language retry"

requirements-completed: [GEN-02, CLI-04]

# Metrics
duration: 4min
completed: 2026-03-20
---

# Phase 01 Plan 03: Generation Engine Summary

**PostGenerator with independent EN/PT Anthropic API calls, per-language emoji retry, conversation history with soft-cap truncation**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-20T22:49:37Z
- **Completed:** 2026-03-20T22:54:00Z
- **Tasks:** 1 (TDD: RED + GREEN)
- **Files modified:** 2

## Accomplishments
- PostGenerator class making 2 independent API calls per generation (EN and PT never share history)
- Emoji validation with per-language retry: if only PT fails, only PT retries (EN untouched)
- Conversation history truncation prevents token exhaustion on long refinement sessions
- 12 tests covering init, generate_pair, refine, emoji retry, history truncation -- all passing
- Full suite 46/46 green (including plan 01 and 02 tests)

## Task Commits

Each task was committed atomically (TDD):

1. **Task 1 RED: Failing tests for PostGenerator** - `2c6b44d` (test)
2. **Task 1 GREEN: PostGenerator implementation** - `d361937` (feat)

## Files Created/Modified
- `src/linkedin_poster/generation/client.py` - PostGenerator class with generate_pair(), refine(), reset(), history management
- `tests/test_generation.py` - 12 tests for bilingual generation, independent retry, history separation

## Decisions Made
- Truncation runs after both user append and assistant append in _call_api to ensure history stays within cap
- _regenerate pops the failed assistant message and re-calls the API with the same user message still in history (no duplicate user entry)
- Test side_effect ordering follows actual execution: EN initial -> EN retry (if emoji) -> PT initial (not interleaved)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed history truncation timing**
- **Found during:** Task 1 GREEN phase
- **Issue:** Truncation only ran before API call (after user append), leaving history at max_messages+1 after assistant append
- **Fix:** Added second truncation call after appending assistant message
- **Files modified:** src/linkedin_poster/generation/client.py
- **Verification:** test_history_truncation passes with HISTORY_SOFT_CAP=2
- **Committed in:** d361937 (Task 1 GREEN commit)

**2. [Rule 1 - Bug] Fixed test side_effect ordering for emoji retry**
- **Found during:** Task 1 GREEN phase
- **Issue:** Test assumed PT initial would be called before EN retry, but validate_post calls regenerate synchronously before PT generation starts
- **Fix:** Reordered mock side_effect to match actual call sequence: EN initial -> EN retry -> PT initial
- **Files modified:** tests/test_generation.py
- **Verification:** test_en_emoji_triggers_retry passes
- **Committed in:** d361937 (Task 1 GREEN commit)

---

**Total deviations:** 2 auto-fixed (2 bugs)
**Impact on plan:** Both fixes were necessary for correctness. No scope creep.

## Issues Encountered
None beyond the auto-fixed deviations above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- PostGenerator is ready for CLI integration in Plan 04
- CLI will call generate_pair() and refine() to drive the conversational loop
- GenerationResult provides all fields needed for terminal display (en_text, pt_text, format_key, passed flags)

---
*Phase: 01-core-generation-loop*
*Completed: 2026-03-20*
