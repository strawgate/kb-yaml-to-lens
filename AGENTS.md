# Agent Guidelines: kb-yaml-to-lens Project

> Multi-language project for compiling Kibana dashboards from YAML to Lens format
> Python compiler · TypeScript VS Code extension

---

## Project Overview

1. **Dashboard Compiler** - Core YAML → JSON compilation engine
2. **VS Code Extension** - Live preview and visual editing

| Directory | Technology | Purpose |
| --------- | ---------- | ------- |
| `compiler/` | Python 3.12+ | Dashboard compiler (see `compiler/AGENTS.md`) |
| `vscode-extension/` | TypeScript/Node.js | VS Code extension (see `vscode-extension/AGENTS.md`) |

---

## Essential Commands

| Command | Purpose |
| ------- | ------- |
| `make check` | **Run before committing** (lint + typecheck + unit tests) |
| `make ci` | Comprehensive CI checks (matches GitHub Actions) |
| `make fix` | Auto-fix linting issues |
| `make install` | Install all dependencies |
| `make test-unit` | Run unit tests only |
| `make test-e2e` | Run end-to-end tests |
| `make clean` | Clean cache and temporary files |

**Troubleshooting CI failures:** Run `make ci` locally to reproduce exact CI checks.

---

## Agent Operating Principles

- **Read first** — Component AGENTS.md before working
- **Search, don't speculate** — Use Grep/Glob to find existing patterns
- **Follow patterns** — Match existing code style unless justified to diverge
- **Verify** — Run `make check`, test actual functionality
- **Be honest** — Document unresolved items, acknowledge uncertainty
- **Zero slop** — No obvious comments, no "this now does X" comparisons

**Code Style:** See component AGENTS.md files for language-specific conventions.

---

## Code Review Feedback

**Triage:** Critical (security, data corruption, type safety) → Important (error handling, performance) → Optional (style)

**Evaluate:** Search for similar patterns first. Pattern exists across files = likely intentional.

---

## Pull Requests

**Requirements:** No merge conflicts, all checks pass, use `.github/pull_request_template.md`

**Self-review:** Solves stated problem, code follows patterns, tests updated, `make ci` passes

---

## CI/CD

**Modifying workflows:** Claude cannot modify `.github/workflows/`. Create exact file in `github/` folder, request maintainer move to `.github/`.

---

## Additional Resources

| Resource | Location |
| -------- | -------- |
| Architecture | `docs/architecture.md` |
| Getting started | `docs/index.md` |
| Contributing | `CONTRIBUTING.md` |
| CLI docs | `docs/CLI.md` |
