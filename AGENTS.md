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
- **Verify** — Run `make all ci`, test actual functionality
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

- **Compiler (Python):** [packages/kb-dashboard-compiler/AGENTS.md](packages/kb-dashboard-compiler/AGENTS.md)
- **VS Code Extension (TypeScript):** [vscode-extension/AGENTS.md](vscode-extension/AGENTS.md)

---

## LLM Workflows

Specialized guides for LLM-driven dashboard creation tasks:

| Workflow | When to Use |
| -------- | ----------- |
| [OTel Dashboard Guide](packages/kb-dashboard-docs/content/llm-workflows/otel-dashboard-guide.md) | Creating dashboards from OpenTelemetry Collector receiver data |
| [ES\|QL Language Reference](packages/kb-dashboard-docs/content/llm-workflows/esql-language-reference.md) | Writing ES\|QL queries for dashboard panels |
| [Dashboard Decompiling Guide](packages/kb-dashboard-docs/content/dashboard-decompiling-guide.md) | Converting existing Kibana JSON dashboards to YAML |
| [Dashboard Style Guide](packages/kb-dashboard-docs/content/dashboard-style-guide.md) | Layout, sizing, and design patterns |

---

## Additional Resources

| Resource | Location |
| -------- | -------- |
| Architecture | `packages/kb-dashboard-docs/content/architecture.md` |
| Getting started | `packages/kb-dashboard-docs/content/index.md` |
| Contributing | `CONTRIBUTING.md` |
| CLI docs | `packages/kb-dashboard-docs/content/CLI.md` |
