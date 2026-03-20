---
phase: 01-core-generation-loop
plan: 01
subsystem: generation
tags: [anthropic, emoji, prompts, tdd, pytest, python]

# Dependency graph
requires: []
provides:
  - "Project skeleton with pyproject.toml and editable install"
  - "Config module with ANTHROPIC_MODEL, MAX_RETRIES, POSTS_DIR constants"
  - "EN and PT system prompts with per-turn rule injection"
  - "Three format instruction templates (short, carousel, hook)"
  - "Emoji validator with retry logic (contains_emoji, validate_post)"
  - "Test infrastructure with conftest.py fixtures and 23 passing tests"
affects: [01-02, 01-03, 01-04]

# Tech tracking
tech-stack:
  added: [anthropic, prompt-toolkit, rich, python-frontmatter, python-slugify, emoji, python-dotenv, pytest, pytest-mock]
  patterns: [per-turn-rule-injection, format-specific-prompt-injection, emoji-replace-validation, tdd-red-green]

key-files:
  created:
    - pyproject.toml
    - src/linkedin_poster/__init__.py
    - src/linkedin_poster/config.py
    - src/linkedin_poster/cli/__init__.py
    - src/linkedin_poster/generation/__init__.py
    - src/linkedin_poster/generation/prompts.py
    - src/linkedin_poster/generation/validator.py
    - src/linkedin_poster/output/__init__.py
    - tests/__init__.py
    - tests/conftest.py
    - tests/test_config.py
    - tests/test_prompts.py
    - tests/test_validator.py
    - .gitignore
  modified: []

key-decisions:
  - "Used setuptools build backend for pyproject.toml (standard, no extra deps)"
  - "RULE_BLOCK stored as plain string constant for easy per-turn injection via concatenation"
  - "PT one-shot example kept as ASCII (no accented chars) to avoid encoding issues in source"

patterns-established:
  - "TDD workflow: RED (failing tests) -> commit -> GREEN (implementation) -> commit"
  - "Per-turn rule injection: RULE_BLOCK prepended to both EN and PT system prompts"
  - "Format-specific prompt injection: FORMAT_INSTRUCTIONS dict keyed by format name"
  - "Emoji validation: emoji.replace_emoji comparison for Unicode-aware detection"

requirements-completed: [GEN-01, GEN-03, GEN-04]

# Metrics
duration: 5min
completed: 2026-03-20
---

# Phase 01 Plan 01: Project Foundation Summary

**Python project skeleton with TDD test suite, bilingual system prompts with per-turn rule injection, three format templates, and emoji validator with retry logic**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-20T22:37:22Z
- **Completed:** 2026-03-20T22:42:02Z
- **Tasks:** 2
- **Files modified:** 14

## Accomplishments
- Project installable via `pip install -e ".[dev]"` with all 9 dependencies resolving
- EN and PT system prompts with mandatory RULE_BLOCK enforcing no-emoji and no-clickbait rules
- PT system prompt includes BR Portuguese one-shot example for independent (non-translated) generation
- Three format instruction templates matching CONTEXT.md specs (short 300-600 chars, carousel 3-5 sections, hook rhetorical question)
- Emoji validator using `emoji.replace_emoji` for Unicode-aware detection including skin tone modifiers and ZWJ sequences
- Retry logic: validate_post calls regenerate_fn up to 2 times on emoji violation
- 23 passing tests across 3 test files with full TDD discipline

## Task Commits

Each task was committed atomically:

1. **Task 1: Project scaffolding, config, and test infrastructure** - `35912b8` (feat)
   - TDD RED: tests fail (module not found) -> GREEN: all config tests pass
2. **Task 2: System prompts, format instructions, and emoji validator** - `b732131` (test, RED) + `b511e89` (feat, GREEN)
   - TDD RED: 19 new tests fail (modules not implemented) -> GREEN: all 23 tests pass

## Files Created/Modified
- `pyproject.toml` - Project metadata, all dependencies, pytest config
- `src/linkedin_poster/__init__.py` - Package marker
- `src/linkedin_poster/config.py` - ANTHROPIC_MODEL, MAX_RETRIES, POSTS_DIR, HISTORY_SOFT_CAP constants
- `src/linkedin_poster/cli/__init__.py` - CLI subpackage marker
- `src/linkedin_poster/generation/__init__.py` - Generation subpackage marker
- `src/linkedin_poster/generation/prompts.py` - RULE_BLOCK, EN/PT system prompts, FORMAT_INSTRUCTIONS, build_generation_prompt
- `src/linkedin_poster/generation/validator.py` - contains_emoji, validate_post with retry logic
- `src/linkedin_poster/output/__init__.py` - Output subpackage marker
- `tests/__init__.py` - Test package marker
- `tests/conftest.py` - Shared fixtures (mock_anthropic_client, tmp_posts_dir, sample posts)
- `tests/test_config.py` - 4 tests for config imports and values
- `tests/test_prompts.py` - 12 tests for prompts, rule block, format instructions
- `tests/test_validator.py` - 7 tests for emoji detection and retry logic
- `.gitignore` - Excludes __pycache__, .egg-info, .env, posts/

## Decisions Made
- Used setuptools build backend (standard, compatible) -- initially tried `_legacy` backend which failed, corrected to `setuptools.build_meta`
- RULE_BLOCK as plain string constant concatenated into system prompts (not f-string interpolation) for clarity
- PT one-shot example uses ASCII approximations of accented characters in source to avoid encoding edge cases

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fixed setuptools build backend import**
- **Found during:** Task 1 (pip install)
- **Issue:** `setuptools.backends._legacy:_Backend` does not exist in current setuptools
- **Fix:** Changed to `setuptools.build_meta` (standard backend)
- **Files modified:** pyproject.toml
- **Verification:** `pip install -e ".[dev]"` succeeds
- **Committed in:** 35912b8

**2. [Rule 2 - Missing Critical] Added .gitignore for generated files**
- **Found during:** Post-task cleanup
- **Issue:** __pycache__, .egg-info, .env, and posts/ would be tracked by git
- **Fix:** Created .gitignore with standard Python exclusions
- **Files modified:** .gitignore
- **Verification:** `git status` no longer shows __pycache__ or .egg-info

---

**Total deviations:** 2 auto-fixed (1 blocking, 1 missing critical)
**Impact on plan:** Both fixes necessary for correct project setup. No scope creep.

## Issues Encountered
None beyond the auto-fixed deviations above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Config module exports all constants needed by downstream plans (01-02 client, 01-03 REPL, 01-04 output)
- System prompts and format instructions ready for the Anthropic client wrapper (01-02)
- Validator ready for integration into generation pipeline (01-02)
- Test infrastructure established with fixtures for mocking Anthropic client

## Self-Check: PASSED

- All 14 created files verified present on disk
- All 3 task commits verified in git log (35912b8, b732131, b511e89)
- 23/23 tests passing

---
*Phase: 01-core-generation-loop*
*Completed: 2026-03-20*
