# Developing: Compiler

This guide covers development workflows for the Python dashboard compiler.

## Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (package manager)

## Setup

```bash
# From repository root
make compiler install
```

## Commands

Run from the repository root using the passthrough pattern:

| Command | Purpose |
| ------- | ------- |
| `make compiler ci` | Run all CI checks (lint + typecheck + test) |
| `make compiler fix` | Auto-fix Python linting issues |
| `make compiler test` | Run Python unit tests |
| `make compiler typecheck` | Run type checking with basedpyright |
| `make compiler compile` | Compile YAML dashboards to NDJSON |

For all commands, see `make compiler help`.

**From within component directory:** You can also run `make <target>` directly from `packages/kb-dashboard-compiler/`.

## Architecture

**Data Flow:** `YAML → PyYAML → Config Models → Compile Functions → View Models → JSON`

Compilation follows a three-layer pattern:

| File | Purpose |
| ---- | ------- |
| `config.py` | YAML schema (Pydantic models for input) |
| `view.py` | JSON output (Pydantic models for Kibana format) |
| `compile.py` | Transformation (config → view) |

## Fixture Repository

The [kb-yaml-to-lens-fixtures](https://github.com/strawgate/kb-yaml-to-lens-fixtures) repository contains "known-good" Kibana Lens JSON generated directly from Kibana's API.

### Repository Structure

| Directory | Purpose |
| --------- | ------- |
| `examples/` | TypeScript generator scripts for each visualization type |
| `output/<kibana-version>/` | Generated JSON fixtures organized by Kibana version |

### Dual-Variant System

Each fixture has ES|QL and Data View versions:

- `metric-basic-esql.json`
- `metric-basic-dataview.json`

### Usage Guidelines

- Reference fixture links in `view.py` files when documenting expected Kibana JSON output
- Reference fixture links in test files when validating compiler output
- Compare generated output against fixtures to validate correctness

## Verification

After making changes:

1. Run `make compiler typecheck` — catches type errors
2. Run `make compiler ci` — runs all quality checks
3. Test compiled output validity

**CI fails on:** Ruff/Markdown/YAML lint failures, test failures, type errors, docstring, code coverage <80%
