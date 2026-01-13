# Agent Guidelines: Dashboard Compiler (Python)

> Python 3.12+ compiler converting YAML to Kibana dashboard JSON
> Pydantic · PyYAML · uv package manager

---

## Commands

Run from `compiler/` directory:

| Command | Purpose |
| ------- | ------- |
| `make ci` | Run all CI checks (lint + typecheck + test + docs) |
| `make fix` | Auto-fix Python and YAML linting |
| `make test` | Run Python unit tests |
| `make typecheck` | Run type checking with basedpyright |
| `make compile` | Compile YAML dashboards to NDJSON |

---

## Architecture

**Data Flow:** `YAML → PyYAML → Config Models → Compile Functions → View Models → JSON`

| Directory | Purpose |
| --------- | ------- |
| `src/dashboard_compiler/dashboard/` | Top-level dashboard config and compilation |
| `src/dashboard_compiler/panels/` | Panel types (markdown, links, images, search, charts) |
| `src/dashboard_compiler/panels/charts/` | Lens/ESQL chart types (metric, pie, xy) |
| `src/dashboard_compiler/controls/` | Dashboard control groups |

**Three-Layer Pattern:** Each component has `config.py` (YAML schema), `view.py` (JSON output), `compile.py` (config → view).

---

## Code Conventions

### Explicit Boolean Comparisons

```python
# ✅ Correct
if my_var is not None:
if len(my_list) > 0:

# ❌ Incorrect
if my_var:  # Ambiguous
```

### Exhaustive Type Checking

Always use explicit type checks with a final error handler:

```python
def handle_panel(panel: PanelTypes) -> str:
    if isinstance(panel, MarkdownPanel):
        return handle_markdown(panel)
    if isinstance(panel, LinksPanel):
        return handle_links(panel)
    if isinstance(panel, (LensPanel, ESQLPanel)):  # pyright: ignore[reportUnnecessaryIsInstance]
        return handle_charts(panel)

    msg = f'Unknown panel type: {type(panel).__name__}'
    raise TypeError(msg)
```

**Key principle:** Make adding new types to unions a runtime error, not a silent fallthrough.

### Pydantic Models

- All models inherit from `BaseCfgModel` or `BaseModel` (in `shared/model.py` and `config.py`)
- Don't duplicate `model_config` settings—they're inherited
- Use `mode='after'` validators (preferred) for validated attributes, `mode='before'` only for raw input transformation
- Document fields with docstrings after the field definition

### Configuration

- **Line length:** 140 characters (Ruff enforced)
- **Docstring coverage:** 80% enforced in CI
- **Lint exceptions:** Use inline `# noqa` or `# pyright: ignore`, not pyproject.toml

---

## Verification

- Run `make typecheck` and `make check` after changes
- Schema changes: cross-reference official docs
- Boolean checks: explicit comparisons only
- Test compiled output validity

**CI fails on:** Ruff/Markdown/YAML lint failures, test failures, type errors, docstring coverage <80%

---

## Context7 MCP Integration

Query library docs via `resolve-library-id` → `query-docs` (max 3 calls/question).

| Library | Context7 ID |
| ------- | ----------- |
| Pydantic | `/websites/pydantic_dev` |
| Elasticsearch | `/elastic/elasticsearch-py` |
| PyYAML | `/yaml/pyyaml` |
