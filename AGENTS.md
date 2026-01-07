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

- `compiler/Makefile` - Python compiler commands (see below)
- `vscode-extension/Makefile` - Extension development commands
- `fixture-generator/Makefile` - Fixture generation commands

## Code Style

@CODE_STYLE.md

## Code Review Guidelines

@CODERABBIT.md

## Agent Operating Principles

- **Read first** — Component README.md/AGENTS.md before working
- **Search, don't speculate** — Use Grep/Glob to find how the codebase solves similar problems
- **Pattern matching** — Follow existing patterns unless justified to diverge
- **Verify** — Run tests, ensure checks pass (lint/typecheck/tests), test actual functionality
- **Honest** — Document unresolved items, acknowledge uncertainty, never claim completion with critical issues
- **Thorough** — Update docs/tests when changing code (search thoroughly—not always co-located), consider broader impact
- **Zero slop** — No slop comments, code, logic, architecture, design. Avoid obvious comments or "this now does X" comparisons

### Context7 MCP Integration

Query up-to-date library documentation via MCP tools: `resolve-library-id` → `query-docs`. **Rate limited—use sparingly** (max 3 calls/question).

**Project libraries:**

| Library | Context7 ID | Use Cases |
| ------- | ----------- | --------- |
| Pydantic | `/websites/pydantic_dev` | Field validators, frozen models, model config patterns |
| Elasticsearch | `/elastic/elasticsearch-py` | Client initialization, search queries, response handling |
| PyYAML | `/yaml/pyyaml` | Safe loading, custom tags, multi-document streams |

## Modifying workflows

Claude cannot modify `.github/workflows/` (permission restriction). To request changes: Create exact file in `github/` folder, request maintainer/Copilot move to `.github/`. Copilot needs explicit instructions—no options, no trust.

---

## Pull Requests

**Requirements:** No merge conflicts, no unrelated changes/plan files, all checks pass, self-review done, use `.github/pull_request_template.md` for PR body

**Self-review:** Solves stated problem (reference issue), code complete/follows patterns, tests updated, docs accurate, `make ci` passes

---

## Additional Resources

| Resource | Location |
| ---------- | ---------- |
| Component AGENTS.md files | `compiler/AGENTS.md`, `vscode-extension/AGENTS.md`, `fixture-generator/AGENTS.md` |
| Architecture details | `docs/architecture.md` |
| Getting started guide | `docs/index.md` (includes installation and first dashboard tutorial) |
| Contributing guide | `CONTRIBUTING.md` |
| CLI documentation | `docs/CLI.md` |
