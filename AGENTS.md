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
| `src/dashboard_compiler/` | Python 3.12+ | Core compilation logic | `src/dashboard_compiler/AGENTS.md` |
| `vscode-extension/` | TypeScript/Node.js | VS Code extension | `vscode-extension/AGENTS.md` |
| `fixture-generator/` | JavaScript/Docker | Kibana fixture generation | `fixture-generator/AGENTS.md` |
| `tests/` | Python pytest | Unit tests for compiler | `src/dashboard_compiler/AGENTS.md` |
| `inputs/` | YAML | Example dashboards | - |
| `docs/` | Markdown | Documentation | - |

### Common Commands

Root-level commands orchestrate all components via `make`:

| Command | Purpose |
| --------- | --------- |
| `make install` | Install all dependencies (all components) |
| `make ci` or `make check` | **Run before committing** (all linting + typecheck + all tests) |
| `make fix` | Auto-fix all linting issues (all components) |
| `make lint-all-check` | Check all linting without fixing (all components) |
| `make test-all` | Run all tests (all components) |
| `make test` | Run Python unit tests only |
| `make typecheck` | Run type checking with basedpyright |
| `make compile` | Compile YAML dashboards to NDJSON |

**Component-specific Makefiles:**

- `vscode-extension/Makefile` - Extension development commands
- `fixture-generator/Makefile` - Fixture generation commands

Component-specific commands can be run by cd-ing into the component directory. See component-specific AGENTS.md files for available commands.

**Workflow example:**

```bash
# First time setup
make install

# Development cycle
# 1. Make changes
# 2. Auto-fix linting issues
make fix
# 3. Run all CI checks (linting + typecheck + tests)
make ci
```

---

## AI Agent Guidelines

@CODE_STYLE.md

**Core Principles:**

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

**When to use:** Implementing new Pydantic validation patterns, working with Elasticsearch client in `kibana_client.py`, extending YAML parsing in `loader.py`, understanding library-specific best practices during code review.

**Query guidelines:** Be specific ("How to use field validators with mode='after' in Pydantic 2.x?" not "pydantic validators"), include version context, prioritize official documentation sources (High reputation).

---

## Code Review Feedback

**Triage:** Critical (security, data corruption, type safety, test failures) → Important (error handling, performance, missing tests/types) → Optional (style, minor refactors)

**Evaluate:** Search for similar patterns before accepting. Pattern exists across files = likely intentional. Preserve consistency over isolated best practices.

**Verify:** Critical/important issues addressed, component checks pass, manual testing done

---

## CI/CD

**Workflows:** Testing/quality checks, docs deployment (GitHub Pages), Claude AI assistance, Docker builds

**Modifying workflows:** Claude cannot modify `.github/workflows/` (permission restriction). To request changes: Create exact file in `github/` folder, request maintainer/Copilot move to `.github/`. Copilot needs explicit instructions—no options, no trust.

---

## Pull Requests

**Requirements:** No merge conflicts, no unrelated changes/plan files, all checks pass, self-review done, use `.github/pull_request_template.md` for PR body

**Self-review:** Solves stated problem (reference issue), code complete/follows patterns, tests updated, docs accurate, `make ci` passes

**CodeRabbit:** @CODERABBIT.md — Reviews PRs automatically. Sometimes makes mistakes; evaluate feedback carefully.

---

## Additional Resources

| Resource | Location |
| ---------- | ---------- |
| Component AGENTS.md files | `src/dashboard_compiler/AGENTS.md`, `vscode-extension/AGENTS.md`, `fixture-generator/AGENTS.md` |
| Architecture details | `docs/architecture.md` |
| Getting started guide | `docs/index.md` (includes installation and first dashboard tutorial) |
| Contributing guide | `CONTRIBUTING.md` |
| CLI documentation | `docs/CLI.md` |
