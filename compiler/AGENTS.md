# Agent Guidelines: Dashboard Compiler (Python)

> Python 3.12+ compiler converting YAML to Kibana dashboard JSON
> Pydantic · PyYAML · uv package manager

---

## Quick Reference

### Compiler Commands

Run from `compiler/` directory or use `cd compiler && make <command>`:

| Command | Purpose |
| --------- | --------- |
| `make ci` or `make check` | Run compiler CI checks (lint + typecheck + test + docs) |
| `make fix` | Auto-fix Python and YAML linting |
| `make test` | Run Python unit tests |
| `make typecheck` | Run type checking with basedpyright |
| `make compile` | Compile YAML dashboards to NDJSON |
| `make docs-serve` | Start local documentation server |
| `make docker-build` | Build Docker image |
| `make build-binary` | Build standalone binary |

See `make help` for complete command list.

**Workflow example:**

```bash
cd compiler
make fix    # Auto-fix Python and YAML
make ci     # Run compiler CI checks (lint + typecheck + test + docs)
```

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

## Context7 MCP Integration

Query up-to-date library documentation via MCP tools: `resolve-library-id` → `query-docs`. **Rate limited—use sparingly** (max 3 calls/question).

**Compiler libraries:**

| Library | Context7 ID | Use Cases |
| ------- | ----------- | --------- |
| Pydantic | `/websites/pydantic_dev` | Field validators, frozen models, model config patterns |
| Elasticsearch | `/elastic/elasticsearch-py` | Client initialization, search queries, response handling |
| PyYAML | `/yaml/pyyaml` | Safe loading, custom tags, multi-document streams |

**When to use:** Implementing new Pydantic validation patterns, working with Elasticsearch client in `kibana_client.py`, extending YAML parsing in `loader.py`, understanding library-specific best practices during code review.

**Query guidelines:** Be specific ("How to use field validators with mode='after' in Pydantic 2.x?" not "pydantic validators"), include version context, prioritize official documentation sources (High reputation).

---

## Code Conventions

### Python Code Style

#### Explicit Boolean Comparisons

Use explicit comparisons instead of implicit truthiness:

```python
# ✅ Correct
if my_var is not None:
if len(my_list) > 0:
if my_bool:  # OK for actual booleans

# ❌ Incorrect
if my_var:  # Ambiguous
```

**Exception:** `if TYPE_CHECKING:` is standard and acceptable.

#### Exhaustive Type Checking

Always use explicit type checks with a final error handler:

```python
# ✅ Correct - isinstance chain
def handle_panel(panel: PanelTypes) -> str:
    if isinstance(panel, MarkdownPanel):
        return handle_markdown(panel)
    if isinstance(panel, LinksPanel):
        return handle_links(panel)
    if isinstance(panel, (LensPanel, ESQLPanel)):  # pyright: ignore[reportUnnecessaryIsInstance]
        return handle_charts(panel)

    msg = f'Unknown panel type: {type(panel).__name__}'
    raise TypeError(msg)

# ✅ Also correct - match statement
def handle_panel(panel: PanelTypes) -> str:
    match panel:
        case MarkdownPanel():
            return handle_markdown(panel)
        case LinksPanel():
            return handle_links(panel)
        case LensPanel() | ESQLPanel():
            return handle_charts(panel)
        case _:  # pyright: ignore[reportUnnecessaryComparison]
            msg = f'Unknown panel type: {type(panel).__name__}'
            raise TypeError(msg)
```

**Key principle:** Make adding new types to unions a runtime error, not a silent fallthrough.

**Type checker pragmas:** Don't remove `# pyright: ignore` comments—they document intentional patterns.

#### Pydantic Models

**Base Model Inheritance:**

All models inherit from `BaseCfgModel` or `BaseModel` (defined in `src/dashboard_compiler/shared/model.py` and `config.py`).

**Do NOT duplicate `model_config` settings**—they're inherited automatically.

**Field Documentation:**

```python
class MyModel(BaseCfgModel):
    field_name: str
    """Description of what this field does."""
```

**Leverage Pydantic's Features:**

```python
# ✅ Preferred - use validated attributes
@model_validator(mode='after')
def validate(self) -> Self:
    # Work with validated Panel objects
    for panel in self.panels:
        if panel.position.x is not None:  # Type-safe
            ...
    return self

# ❌ Avoid - manual dict manipulation
@model_validator(mode='before')
@classmethod
def validate(cls, data: dict[str, Any]) -> dict[str, Any]:
    for panel_dict in data.get('panels', []):  # No type safety
        ...
    return data
```

**Use `mode='after'` (preferred)** for validated attributes. **Use `mode='before'`** only for raw input transformation.

**Best Practices:**

- Module-level imports (not inside validators)
- Type annotations match runtime types
- Generic types always have arguments: `list[Panel]` not `list`

#### Configuration

- **Line length:** 140 characters max (Ruff enforced)
- **Docstring coverage:** 80% enforced in CI
- **Lint exceptions:** Use inline `# noqa` or `# pyright: ignore`, not pyproject.toml

#### Per-File Exemptions

**Test files** (`tests/**/*.py`): Allow `assert`, magic numbers, relaxed line length

**View models** (`**/view.py`): Allow mixed-case names, missing docstrings, commented code

**Config models** (`**/config.py`): Allow type-checking imports at runtime

---

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
