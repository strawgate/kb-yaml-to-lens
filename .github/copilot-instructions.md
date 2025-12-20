# Repository Instructions for GitHub Copilot

## Project Overview

**Dashboard Compiler** - Simplifies Kibana dashboard creation by converting human-readable YAML into complex native Kibana dashboard JSON format.

- **Language:** Python 3.12+
- **Dependency Manager:** uv (not Poetry)
- **Default Branch:** main

## Development Workflow

### Pre-commit Checks

Before committing, run:

```bash
make check  # Runs lint + test + test-smoke
```

Or individually:

1. `make lint` - Ruff formatting and linting
2. `make test` - All tests pass
3. Type checking via basedpyright (runs in CI)

## Architecture Overview

Dashboard Compiler uses three layers:

1. **YAML Loading**: `PyYAML` parses YAML config files into Python dictionaries
2. **Pydantic Models**: Models in `src/dashboard_compiler/*/config.py` define schema, validate data, and handle panel type polymorphism
3. **JSON Compilation**: Each model's `to_json()` or `model_dump_json()` method converts to Kibana JSON format

**Goal:** Maintainability and abstraction from Kibana's complex native JSON.

See `architecture.md` for detailed design documentation.

## Code Style & Conventions

### Python Style

- **Line length:** 140 characters (Ruff enforced)
- **Quote style:** Single quotes for inline code, double quotes for docstrings
- **Type hints:** Required for all function signatures
- **Python version:** 3.12+ with modern type annotations

### Pydantic Model Conventions

**Configuration models** (`BaseCfgModel` in `src/dashboard_compiler/shared/model.py`):

- `strict=True`, `extra='forbid'`, `frozen=True`, `validate_default=True`
- Use attribute docstrings for field descriptions
- Example:

```python
class MyConfigModel(BaseCfgModel):
    field_name: str
    """Description of what this field does."""
```

**View models** (`BaseVwModel` in `src/dashboard_compiler/shared/view.py`):

- Custom serializer omits fields with `OmitIfNone` metadata when value is `None`
- May narrow types in subclasses (e.g., `str` -> `Literal['value']`)
- `reportIncompatibleVariableOverride = false` in basedpyright config allows this intentional design

### Docstrings

- Use attribute docstrings on Pydantic model fields (see example above)
- 80% docstring coverage threshold enforced by code review
- Follow Google-style docstrings for functions and classes

## Key Directories

| Directory | Purpose |
|-----------|---------|
| `src/dashboard_compiler/` | Core logic: YAML parsing, Pydantic models, JSON compilation |
| `src/dashboard_compiler/dashboard/` | Top-level Dashboard config and compilation |
| `src/dashboard_compiler/panels/` | Panel types (markdown, links, charts) |
| `src/dashboard_compiler/panels/charts/` | Lens and ESQL chart compilation (metric, pie, xy) |
| `scripts/` | Utility scripts (compile to NDJSON, generate docs) |
| `inputs/` | Example YAML dashboard configurations |
| `test/` | Unit and snapshot tests |

## Common Make Commands

| Command | Purpose |
|---------|---------|
| `make check` | Run lint + test + test-smoke |
| `make test` | Run full pytest suite (verbose) |
| `make lint` | Run autocorrect + format |
| `make compile` | Compile YAML dashboards to NDJSON |
| `make install` | Install dependencies via uv sync |

## Common Pitfalls

### Type Checking

- **Mode:** `standard` (basedpyright)
- **Python version:** 3.12+
- Pydantic view models have special override allowances (intentional design pattern)

### Tool Usage

- **Always use `uv`** for dependency management, not `pip` or `poetry`
- **Line length:** 140 characters for Python code
- **Testing:** Use `syrupy` for snapshot tests, `pytest-freezer` for time-sensitive tests

### Pattern Consistency

Before making changes:

- Search codebase for similar patterns
- Check how other panels/compilers handle similar cases
- Preserve consistency over isolated best practices
- If pattern exists across multiple files, it's likely intentional

## Testing Practices

- Run `make test` before committing
- Update snapshots with `pytest --snapshot-update` if JSON output changes intentionally
- Use fixture patterns consistent with existing tests
- Focus on compilation correctness and type safety

## Code Review Requirements

Before claiming work is complete:

- All critical issues addressed or documented as out-of-scope
- All important issues addressed or explicitly deferred with rationale
- `make check` passes (lint + test)
- Type checking passes (basedpyright in CI)
- Tests pass with updated snapshots if needed

## Dependencies

- **Runtime:** Python >=3.12, PyYAML >=6.0, Pydantic >=2.11.3
- **Development:** pytest >=7.0, syrupy >=4.9.1, ruff >=0.11.6
- **Toolchain:** uv for package management

## Adding New Features

1. Create samples in the samples directory
2. Define corresponding config in configs
3. Update `yaml_reference.md` if new keys are added
4. Add snapshot tests to ensure exact JSON generation
5. Run `make check` to validate

See `CONTRIBUTING.md` for detailed contribution guidelines.

## Documentation

- Documentation auto-generated from markdown files via `scripts/compile_docs.py`
- CLI output uses Rich/rich-click for formatting
- Update relevant markdown files when changing features
