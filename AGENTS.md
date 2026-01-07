# Agent Guidelines: kb-yaml-to-lens Project

> Multi-language project for compiling Kibana dashboards from YAML to Lens format
> Python compiler · TypeScript VS Code extension · JavaScript fixture generator
>
> **Note:** `CLAUDE.md` is a symlink to `AGENTS.md` throughout this repository. Both names reference the same file.

---

## Project Overview

This repository contains three main components:

1. **Dashboard Compiler** - Core YAML → JSON compilation engine
2. **VS Code Extension** - Live preview and visual editing
3. **Fixture Generator** - Kibana API-based test fixture generation

### Repository Structure

| Directory | Technology | Purpose | AGENTS.md |
| --------- | ---------- | ------- | --------- |
| `compiler/` | Python 3.12+ | Dashboard compiler | `compiler/AGENTS.md` |
| `compiler/src/dashboard_compiler/` | Python 3.12+ | Core compilation logic | `compiler/AGENTS.md` |
| `compiler/tests/` | Python pytest | Unit tests for compiler | `compiler/AGENTS.md` |
| `compiler/inputs/` | YAML | Example dashboards | - |
| `vscode-extension/` | TypeScript/Node.js | VS Code extension | `vscode-extension/AGENTS.md` |
| `fixture-generator/` | JavaScript/Docker | Kibana fixture generation | `fixture-generator/AGENTS.md` |
| `docs/` | Markdown | Documentation | - |

### Common Commands

**Root-level commands** orchestrate all components:

| Command | Purpose |
| --------- | --------- |
| `make install` | Install all dependencies (all components) |
| `make ci` or `make check` | **Run before committing** (linting + tests across all components) |
| `make fix` | Auto-fix linting issues (all components) |
| `make lint-all-check` | Check all linting without fixing |
| `make test-all` | Run all tests (all components) |
| `make clean` | Clean cache and temporary files |
| `make clean-full` | Deep clean including virtual environments |

**Component-specific Makefiles** provide focused workflows:

- `compiler/Makefile` - Python compiler commands (see `compiler/AGENTS.md`)
- `vscode-extension/Makefile` - Extension development commands (see `vscode-extension/AGENTS.md`)
- `fixture-generator/Makefile` - Fixture generation commands (see `fixture-generator/AGENTS.md`)

See `make help` in root or component directories for complete command lists.

## AI Agent Guidelines

### IMPORTANT: Post-Compaction Recovery

If you have recently undergone context summarization/compaction:

1. **IMMEDIATELY re-read this file** (`AGENTS.md`) before proceeding with any work
2. **DO NOT rely on summarized references** to framework rules in your conversation history
3. **DO NOT assume you remember project conventions** from the summary—the summary is lossy and paraphrased
4. **Re-establish understanding** of: Core Principles, Code Style, Verification requirements, and project patterns

**Why this matters:** Post-compaction behavioral compliance drops 30-40% when agents rely on paraphrased summaries instead of authoritative source files. AGENTS.md files survive compaction intact and are loaded fresh from disk—you have access to them, so use them.

---

## Agent Operating Principles

- **Read first** — Component README.md/AGENTS.md before working
- **Search, don't speculate** — Use Grep/Glob to find how the codebase solves similar problems
- **Pattern matching** — Follow existing patterns unless justified to diverge
- **Verify** — Run tests, ensure checks pass (lint/typecheck/tests), test actual functionality
- **Honest** — Document unresolved items, acknowledge uncertainty, never claim completion with critical issues
- **Thorough** — Update docs/tests when changing code (search thoroughly—not always co-located), consider broader impact
- **Zero slop** — No slop comments, code, logic, architecture, design. Avoid obvious comments or "this now does X" comparisons

**Code Style:** See component AGENTS.md files for language-specific conventions and detailed patterns.

---

## Code Review Feedback

**Triage:** Critical (security, data corruption, type safety, test failures) → Important (error handling, performance, missing tests/types) → Optional (style, minor refactors)

**Evaluate:** Search for similar patterns before accepting. Pattern exists across files = likely intentional. Preserve consistency over isolated best practices.

**Verify:** Critical/important issues addressed, component checks pass, manual testing done

---

## CI/CD

**Workflows:** Testing/quality checks, docs deployment (GitHub Pages), Claude AI assistance, Docker builds

**Modifying workflows:** Claude cannot modify `.github/workflows/` (permission restriction). To request changes: Create exact file in `github/` folder (mirroring `.github/workflows/` structure), request maintainer/Copilot move to `.github/`. Copilot needs explicit instructions—no options, no trust.

---

## Pull Requests

**Requirements:** No merge conflicts, no unrelated changes/plan files, all checks pass, self-review done, use `.github/pull_request_template.md` for PR body

**Self-review:** Solves stated problem (reference issue), code complete/follows patterns, tests updated, docs accurate, `make ci` passes

## Before Completion

When you think you've finished the job take one moment to review the original ask and ensure you have thoroughly addressed it. It's easy to get lost in the details and forget the original goal.

---

## Additional Resources

| Resource | Location |
| ---------- | ---------- |
| Component AGENTS.md files | `compiler/AGENTS.md`, `vscode-extension/AGENTS.md`, `fixture-generator/AGENTS.md` |
| Architecture details | `docs/architecture.md` |
| Getting started guide | `docs/index.md` (includes installation and first dashboard tutorial) |
| Contributing guide | `CONTRIBUTING.md` |
| CLI documentation | `docs/CLI.md` |
