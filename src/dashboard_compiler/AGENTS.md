# Agent Guidelines: Dashboard Compiler (Python)

> **Dashboard Compiler** converts human-readable YAML into Kibana dashboard JSON.
> Python 3.12+ · Pydantic · PyYAML · uv package manager

---

## Quick Reference

### Essential Commands

| Command | Purpose |
| ------- | ------- |
| `make install` | Install all dependencies |
| `make check` | **Run before committing** (lint + typecheck + test) |
| `make test` | Run pytest suite |
| `make lint` | Format and lint code |
| `make typecheck` | Run type checking with basedpyright |
| `make compile` | Compile YAML dashboards to NDJSON |

### Common Workflows

```bash
# First time setup
make install

# Development cycle
# 1. Make changes
# 2. Run checks
make check
```

---

## Project Architecture

### Data Flow

```text
YAML File → PyYAML Parser → Config Models (Pydantic) → Compile Functions → View Models → Kibana JSON
```

### Directory Structure

| Directory | Purpose |
| --------- | ------- |
| `src/dashboard_compiler/` | Core compilation logic |
| `src/dashboard_compiler/dashboard/` | Top-level dashboard config and compilation |
| `src/dashboard_compiler/panels/` | Panel types (markdown, links, images, search, charts) |
| `src/dashboard_compiler/panels/charts/` | Lens/ESQL chart types (metric, pie, xy) |
| `src/dashboard_compiler/controls/` | Dashboard control groups |
| `src/dashboard_compiler/filters/` | Filter compilation |
| `src/dashboard_compiler/queries/` | KQL, Lucene, ESQL query support |
| `src/dashboard_compiler/shared/` | Base models and utilities |
| `tests/` | Unit tests with snapshot testing (inline snapshots via `inline-snapshot` library) |
| `inputs/` | Example YAML dashboards |

### Three-Layer Pattern

Each component follows this structure:

1. **`config.py`** — Pydantic models defining YAML schema (source of truth)
2. **`view.py`** — Pydantic models defining Kibana JSON output
3. **`compile.py`** — Functions transforming config → view models

### Test Standards

- **Use inline snapshots** via `inline-snapshot` library (not external snapshot files)
- **Prefer inline tests** in Python test files over separate scenario files
- **Note:** Scenario-based tests in `tests/scenarios/` are being phased out in favor of inline snapshot tests
- See existing tests for patterns (e.g., `tests/panels/charts/lens/metrics/test_metrics.py`)

---

## Code Conventions

### Style

- **Line length**: 140 characters (Ruff enforced)
- **Dependency manager**: `uv` (not Poetry)
- **Docstring coverage**: 80% threshold

### Pydantic Models

**Configuration Models** (`BaseCfgModel`):

- Settings: `strict=True`, `extra='forbid'`, `frozen=True`, `validate_default=True`
- Use attribute docstrings for field descriptions
- Location: `**/config.py` files

**View Models** (`BaseVwModel`):

- Custom serializer omits fields with `OmitIfNone` metadata when value is `None`
- May narrow types in subclasses (e.g., `str` → `Literal['value']`)
- `reportIncompatibleVariableOverride = false` in basedpyright allows this

### Explicit Boolean Checks

Always use explicit comparisons instead of implicit truthiness:

**✅ Correct:**

- `if my_var is not None:` (for optional types)
- `if my_var is None:` (for None checks)
- `if len(my_list) > 0:` (for non-empty lists)
- `if len(my_str) > 0:` (for non-empty strings)
- `if my_bool is True:` or `if my_bool:` (for actual booleans)

**❌ Incorrect:**

- `if my_var:` (ambiguous: could be None, empty, False, 0, etc.)
- `if not my_var:` (ambiguous truthiness check)

**Exception:** `if TYPE_CHECKING:` is standard Python and acceptable.

### Documentation Updates

When updating YAML configuration docs:

1. `config.py` files are the source of truth for all configuration options
2. Each component's markdown should include: overview, minimal example, complex example, full options table
3. Table columns: `YAML Key`, `Data Type`, `Description`, `Default`, `Required`
4. Defaults are typically "Kibana Default" (defined in `compile.py`, not config models)
5. Run `make compile-docs` to regenerate `docs/yaml_reference.md`

---

## AI Agent Guidelines

### Before Making Changes

1. **Read relevant files first** — Never speculate about code you haven't inspected
2. **Search for existing patterns** — Check how similar components handle the same problem
3. **Understand the architecture** — Config models → compile functions → view models
4. **Use explicit Boolean comparisons** — Never rely on implicit truthiness
   - `if x is not None:` instead of `if x:`
   - `if len(items) > 0:` instead of `if items:`

### Verification Requirements

Before claiming work is complete:

- [ ] **For schema changes:** Cross-reference with official documentation (Kibana repo, API docs, etc.)
- [ ] **For test changes:** Explain WHY test data changed, not just WHAT changed
- [ ] **For type errors:** Verify the fix compiles AND is semantically correct
- [ ] **For Boolean checks:** All conditional statements use explicit comparisons
- [ ] **For type checking:** Run `make typecheck` to verify type correctness
- [ ] Run `make check` after EACH fix, not just at the end
- [ ] Test that the compiled output is valid (not just that it compiles)

### Radical Honesty

- **Document unresolved items** — Explain why they weren't addressed
- **Acknowledge uncertainty** — Ask if unclear about patterns or requirements
- **Report problems** — Share issues encountered during implementation
- **Share reasoning** — Explain why you rejected or deferred feedback
- **Admit limitations** — Be clear if unable to verify fixes work correctly

**Never claim work is complete with unresolved critical or important issues.**

---

## CI/CD

### Pre-commit Requirements

CI will fail if:

- Ruff linting fails
- Tests fail
- Type checking fails (basedpyright standard mode)
- Docstring coverage below 80%

Run `make check` locally before pushing.

---

## Additional Resources

| Resource | Location |
| -------- | -------- |
| Architecture details | `docs/architecture.md` |
| YAML schema reference | `docs/yaml_reference.md` (generated via `make compile-docs`) |
| Quickstart guide | `docs/quickstart.md` |
| Contributing guide | `CONTRIBUTING.md` |
| CLI documentation | `docs/CLI.md` |
