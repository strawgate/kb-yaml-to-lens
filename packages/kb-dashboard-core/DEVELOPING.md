# Developing: Core

This guide covers development workflows for the core dashboard compilation engine.

## Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (package manager)

## Setup

```bash
# From repository root
make core install
```

## Commands

Run from the repository root using the passthrough pattern:

| Command | Purpose |
| ------- | ------- |
| `make core ci` | Run all CI checks (lint + typecheck + test) |
| `make core fix` | Auto-fix Python linting issues |
| `make core test` | Run Python unit tests |
| `make core typecheck` | Run type checking with basedpyright |

For all commands, see `make core help`.

**From within component directory:** You can also run `make <target>` directly from `packages/kb-dashboard-core/`.

## Architecture

**Data Flow:** `YAML → PyYAML → Config Models → Compile Functions → View Models → JSON`

Compilation follows a three-layer pattern:

| File | Purpose |
| ---- | ------- |
| `config.py` | YAML schema (Pydantic models for input) |
| `view.py` | JSON output (Pydantic models for Kibana format) |
| `compile.py` | Transformation (config → view) |

## Package Structure

```text
kb_dashboard_core/
├── controls/        # Dashboard controls (filters, options)
├── dashboard/       # Dashboard-level models and compilation
├── filters/         # Filter models and compilation
├── panels/          # Panel types (charts, markdown)
│   ├── charts/      # Lens and ES|QL chart types
│   └── markdown/    # Markdown panel support
├── queries/         # Query types (KQL, Lucene, ES|QL)
└── shared/          # Shared utilities and base models
```

## Verification

After making changes:

1. Run `make core typecheck` - catches type errors
2. Run `make core ci` - runs all quality checks
3. Test with CLI: `make cli test` - ensures core changes work end-to-end

**CI fails on:** Ruff/Markdown/YAML lint failures, test failures, type errors, docstring coverage <80%
