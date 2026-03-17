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
- **Verify** — Run `just all ci`, test actual functionality
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

**Modifying workflows:** Claude cannot directly modify `.github/workflows/`. Propose workflow changes in the PR description and request a maintainer to apply them.

---

## Component Guidelines

Read the component-specific AGENTS.md before working in that component:

- **CLI (Python):** [packages/kb-dashboard-cli/AGENTS.md](packages/kb-dashboard-cli/AGENTS.md)
- **Core (Python):** [packages/kb-dashboard-core/AGENTS.md](packages/kb-dashboard-core/AGENTS.md)
- **Lint (Python):** `packages/kb-dashboard-lint/` — follows same patterns as other Python packages (`just lint ci`)
- **Tools (Python):** `packages/kb-dashboard-tools/` — follows same patterns as other Python packages (`just tools ci`)
- **VS Code Extension (TypeScript):** [packages/vscode-extension/AGENTS.md](packages/vscode-extension/AGENTS.md)
- **Docs (MkDocs):** [packages/kb-dashboard-docs/AGENTS.md](packages/kb-dashboard-docs/AGENTS.md)

---

## LLM Workflows

Specialized guides for LLM-driven dashboard creation tasks:

| Workflow | When to Use |
| -------- | ----------- |
| [OTel Dashboard Guide](packages/kb-dashboard-docs/content/guides/otel-dashboard-guide.md) | Creating dashboards from OpenTelemetry Collector receiver data |
| [ES\|QL Language Reference](packages/kb-dashboard-docs/content/guides/esql-language-reference.md) | Writing ES\|QL queries for dashboard panels |
| [Dashboard Decompiling Guide](packages/kb-dashboard-docs/content/guides/dashboard-decompiling-guide.md) | Converting existing Kibana JSON dashboards to YAML |
| [Dashboard Style Guide](packages/kb-dashboard-docs/content/guides/dashboard-style-guide.md) | Layout, sizing, and design patterns |

---

## Explore Agent System

Automated explore agents run against live Kibana instances via GitHub Actions to discover UI behavior and saved-object structure.

- **Workflows:** `.github/workflows/explore-*.yml` — one per chart type and variant (Lens vs ES|QL)
- **Agent guides:** `.github/agent-guides/explore-agents/` — getting-started, networking, response-format, and verification docs
- **Triage:** Explore reports are triaged into GitHub issues; see the "Kibana Features that seem like they should exist but don't" section below before filing bugs

---

## Kibana Features that seem like they should exist but don't

These Kibana features are intentionally not supported by the compiler.
Do NOT flag them as bugs in explore workflow reports or triage issues:

- **ES|QL Annotation layers** — Lens-only feature, not available
  for ES|QL charts
- **ES|QL reference line layers** — Lens-only feature, not available
  for ES|QL charts
- **ES|QL formula metrics** — ES|QL uses query-computed columns, not
  Lens formula syntax
- **Collapsible sections on Kibana < 9.1** — `section` panels require
  Kibana 9.1+; do not tell agents to add or test them on older stacks
- **Nested collapsible sections** — sections cannot contain sections
- **Palette `continuity` configuration** — Kibana does not expose
  `continuity` in its palette editor UI; the compiler hardcodes it
  to `above` which matches Kibana's own default behavior

## Saved Object content that seems like it matters but doesn't

- We do not need adhocdataviews and we do not need to parse ES|QL queries
  to get an index name that we can stringify.

---

## Additional Resources

| Resource | Location |
| -------- | -------- |
| Architecture | `packages/kb-dashboard-core/docs/compiler-architecture.md` |
| Getting started | `packages/kb-dashboard-docs/content/index.md` |
| Contributing | `CONTRIBUTING.md` |
| CLI docs | `packages/kb-dashboard-docs/content/CLI.md` |
