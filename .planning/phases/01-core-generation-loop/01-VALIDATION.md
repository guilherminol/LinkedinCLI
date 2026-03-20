---
phase: 1
slug: core-generation-loop
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-20
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | pytest.ini or pyproject.toml — Wave 0 installs |
| **Quick run command** | `pytest tests/ -x -q` |
| **Full suite command** | `pytest tests/ -v` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/ -x -q`
- **After every plan wave:** Run `pytest tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 1-01-01 | 01 | 0 | CLI-01 | unit | `pytest tests/test_cli.py -x -q` | ❌ W0 | ⬜ pending |
| 1-01-02 | 01 | 1 | CLI-02 | unit | `pytest tests/test_session.py -x -q` | ❌ W0 | ⬜ pending |
| 1-01-03 | 01 | 1 | GEN-01 | unit | `pytest tests/test_generator.py -x -q` | ❌ W0 | ⬜ pending |
| 1-01-04 | 01 | 1 | GEN-02 | unit | `pytest tests/test_generator.py::test_formats -x -q` | ❌ W0 | ⬜ pending |
| 1-01-05 | 01 | 2 | GEN-03 | unit | `pytest tests/test_generator.py::test_bilingual -x -q` | ❌ W0 | ⬜ pending |
| 1-01-06 | 01 | 2 | GEN-04 | unit | `pytest tests/test_validator.py -x -q` | ❌ W0 | ⬜ pending |
| 1-01-07 | 01 | 2 | OUT-01 | unit | `pytest tests/test_output.py -x -q` | ❌ W0 | ⬜ pending |
| 1-01-08 | 01 | 3 | OUT-02 | unit | `pytest tests/test_save.py -x -q` | ❌ W0 | ⬜ pending |
| 1-01-09 | 01 | 3 | CLI-04 | manual | N/A — interactive REPL | manual | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/__init__.py` — test package init
- [ ] `tests/conftest.py` — shared fixtures (mock Anthropic client, sample post content)
- [ ] `tests/test_cli.py` — stubs for CLI-01 (entry point, session start)
- [ ] `tests/test_session.py` — stubs for CLI-02 (conversational loop)
- [ ] `tests/test_generator.py` — stubs for GEN-01, GEN-02, GEN-03 (post generation, formats, bilingual)
- [ ] `tests/test_validator.py` — stubs for GEN-04 (emoji/clickbait validation)
- [ ] `tests/test_output.py` — stubs for OUT-01 (terminal display)
- [ ] `tests/test_save.py` — stubs for OUT-02 (/save command, file naming)
- [ ] `pytest` and `pytest-mock` installed (pyproject.toml or requirements-dev.txt)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Interactive REPL conversational flow | CLI-04 | Requires live terminal session with real user input | Start session with `python -m linkedin_poster`, type a topic, verify response appears formatted in terminal with spinner |
| Portuguese post quality | GEN-03 | Quality judgment requires human review | Generate a post in PT, verify grammar and tone match EN quality without being a literal translation |
| Emoji re-generation trigger | GEN-04 | End-to-end flow requires live API + validation loop | Confirm that when validator detects emoji in generated output, a new generation is automatically triggered without user intervention |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
