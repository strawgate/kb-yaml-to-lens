# Agent Guidelines: Dashboard Compiler (Python)

> Python 3.12+ compiler converting YAML to Kibana dashboard JSON
> Pydantic · PyYAML · uv package manager

---

## Project Architecture

### Data Flow

```text
YAML File → PyYAML → Config Models → Compile Functions → View Models → Kibana JSON
```

### Directory Structure

| Directory | Purpose |
| --------- | ------- |
| `src/dashboard_compiler/dashboard/` | Top-level dashboard config and compilation |
| `src/dashboard_compiler/panels/` | Panel types (markdown, links, images, search, charts) |
| `src/dashboard_compiler/panels/charts/` | Lens/ESQL chart types (metric, pie, xy) |
| `src/dashboard_compiler/controls/` | Dashboard control groups |
| `src/dashboard_compiler/filters/` | Filter compilation |
| `src/dashboard_compiler/queries/` | KQL, Lucene, ESQL query support |
| `src/dashboard_compiler/shared/` | Base models and utilities |

### Three-Layer Pattern

Each component follows:

1. **`config.py`** — Pydantic models defining YAML schema (source of truth)
2. **`view.py`** — Pydantic models defining Kibana JSON output
3. **`compile.py`** — Functions transforming config → view models

### Test Standards

- Use inline snapshots via `inline-snapshot` library (prefer snapshots over many assertions)
- Tests should be useful, maintainable, and well-documented

---

## Code Conventions

See root CODE_STYLE.md and CODERABBIT.md for detailed conventions.

### Quick Reference: Finding Patterns

| Task | Search Strategy |
| ---- | --------------- |
| **New panel type** | `grep -r "isinstance.*Panel" src/dashboard_compiler/panels/compile.py` |
| **New chart type** | Study `src/dashboard_compiler/panels/charts/` directory |
| **Pydantic validation** | `grep -r "@model_validator" src/` (look for `mode='after'`) |
| **Union types** | Search for isinstance chains with final error handlers |
| **New config option** | Find similar in `config.py`, check defaults in `compile.py` |

**Remember:** Search the codebase first, then implement following existing patterns.

### Documentation Updates

When updating YAML configuration docs:

1. `config.py` files are the source of truth
2. Include: overview, minimal example, complex example, full options table
3. Table columns: `YAML Key`, `Data Type`, `Description`, `Default`, `Required`
4. Defaults are typically "Kibana Default" (defined in `compile.py`)

---

## AI Agent Guidelines

### Before Making Changes

1. **Read relevant files first**
2. **Search for existing patterns**
3. **Understand architecture**: Config → compile → view
4. **Follow code style guidelines**

### When Working on Chart Types

Get accurate reference data using the fixture generator:

#### Option 1: Reference Existing Fixtures (Preferred)

1. Check `fixture-generator/output/` for chart type
2. Read fixture to understand Kibana JSON structure
3. Compare compiler output against fixture

#### Option 2: Create New Fixtures

1. Create generator in `fixture-generator/examples/<chart-type>.js`
2. Run `cd fixture-generator && make build` (if needed)
3. Run `cd fixture-generator && make run-example EXAMPLE=<chart-type>.js`
4. Verify output in `fixture-generator/output/`
5. Compare compiler output with fixture
6. Commit both generator script AND output files

#### Option 3: Review Kibana Codebase

Use GitHub code search for JSON examples from the chart type in Kibana codebase.

**Why fixtures:** Generated from real Kibana APIs, ensuring accuracy. Much faster than manual creation.

See `fixture-generator/AGENTS.md` for details.

### Verification

- Schema changes: cross-reference official docs
- Test changes: explain WHY data changed, not just WHAT
- Type errors: verify fix compiles AND semantically correct
- Boolean checks: explicit comparisons only
- Run `make typecheck` and `make check` after each fix
- Test compiled output validity

**Radical Honesty:** Document unresolved items, acknowledge uncertainty, report problems, share reasoning, admit limitations. Never claim completion with critical/important issues unresolved.

---

## CI/CD

**CI fails on:** Ruff/Markdown/YAML lint failures, test failures, type errors, docstring coverage <80%, merge conflicts

Run `make ci` before pushing.

---

## Additional Resources

| Resource | Location |
| -------- | -------- |
| Architecture | `docs/architecture.md` |
| Getting started | `docs/index.md` |
| Contributing | `CONTRIBUTING.md` |
| CLI docs | `docs/CLI.md` |
