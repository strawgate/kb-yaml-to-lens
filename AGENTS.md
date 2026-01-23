# Agent Guidelines: kb-yaml-to-lens

> Multi-language project for compiling Kibana dashboards from YAML to Lens format

---

## Project Overview

@DEVELOPING.md

---

## Essential Commands

See DEVELOPING.md above.

---

## Agent Operating Principles

- **Read first** — Read component AGENTS.md before working in that component
- **Search, don't speculate** — Use Grep/Glob to find existing patterns
- **Follow patterns** — Match existing code style unless justified to diverge
- **Verify** — Run `make check`, test actual functionality
- **Be honest** — Document unresolved items, acknowledge uncertainty
- **Zero slop** — No obvious comments, no "this now does X" comparisons

---

## Code Style

@CODE_STYLE.md

---

## Code Review Feedback

**Triage:** Critical (security, data corruption, type safety) → Important (error handling, performance) → Optional (style)

**Evaluate:** Search for similar patterns first. Pattern exists across files = likely intentional.

---

## Pull Requests

@CONTRIBUTING.md

---

## CI/CD

**Modifying workflows:** Claude cannot modify `.github/workflows/`. Create exact file in `github/` folder, request maintainer move to `.github/`.

---

## Component Guidelines

Read the component-specific AGENTS.md before working in that component:

- **Compiler (Python):** [compiler/AGENTS.md](compiler/AGENTS.md)
- **VS Code Extension (TypeScript):** [vscode-extension/AGENTS.md](vscode-extension/AGENTS.md)

---

## Additional Resources

| Resource | Location |
| -------- | -------- |
| Architecture | `docs/architecture.md` |
| Getting started | `docs/index.md` |
| Contributing | `CONTRIBUTING.md` |
| CLI docs | `docs/CLI.md` |
