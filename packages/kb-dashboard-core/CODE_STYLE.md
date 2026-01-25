# Code Style: Dashboard Core (Python)

This document describes Python code style conventions that are **atypical** but **mandatory** in this project.

## No `from __future__ import annotations`

Do **not** use `from __future__ import annotations`. This project requires explicit type annotations at runtime for Pydantic model validation.

```python
# Incorrect - do not use
from __future__ import annotations

# Correct - use explicit types or TYPE_CHECKING blocks
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from some_module import SomeType
```

**Rationale:** `from __future__ import annotations` makes all annotations strings at runtime (PEP 563), which breaks Pydantic's runtime type introspection.

## No `hasattr`/`getattr` for Typed Models

When working with strongly-typed Pydantic models, use `isinstance` checks for type narrowing instead of `hasattr`/`getattr`:

```python
# Incorrect - do not use
if hasattr(config, 'secondary') and config.secondary is not None:
    ...
description = getattr(panel, 'description', None)

# Correct - use isinstance for type narrowing
from kb_dashboard_core.panels.charts.metric import LensMetricChart

if isinstance(config, LensMetricChart) and config.secondary is not None:
    ...
description = panel.description  # All panels have description field
```

**Rationale:** With discriminated unions and explicit type definitions, `hasattr`/`getattr` bypasses the type system. Use `isinstance` to properly narrow types and access known attributes.

**Exception:** `hasattr` is acceptable when interfacing with external libraries (e.g., checking for `lc` attribute on ruamel.yaml objects).

## Explicit Boolean Comparisons

Always use explicit comparisons. This project rejects implicit truthiness.

```python
# Correct
if my_var is not None:
    ...
if len(my_list) > 0:
    ...

# Incorrect - do not use
if my_var:      # Ambiguous: could be None, empty, or False
if my_list:     # Ambiguous
```

**Rationale:** Explicit comparisons make intent clear and prevent bugs from unexpected falsy values.

## Exhaustive Type Checking

Use explicit isinstance checks with a final error handler for type unions:

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

**Key principle:** Adding new types to unions should cause a runtime error, not silent fallthrough.

The `# pyright: ignore[reportUnnecessaryIsInstance]` pragma documents that the check is intentional.

## Pydantic Models

### Base Classes

All models should inherit from `BaseCfgModel` (defined in `src/kb_dashboard_core/shared/config.py`) or `BaseVwModel` (defined in `src/kb_dashboard_core/shared/model.py`).

Do **not** duplicate `model_config` settings—they're inherited from base classes:

- `strict=True`
- `validate_default=True`
- `extra='forbid'`
- `use_enum_values=True`
- `frozen=True`
- `use_attribute_docstrings=True`
- `serialize_by_alias=True`

### Validators

- Use `mode='after'` validators (preferred) for validated attributes
- Use `mode='before'` only for raw input transformation

### Field Documentation

Document fields with docstrings after the field definition:

```python
field_name: str = Field(...)
"""Description of what this field does."""
```

## Configuration

| Setting | Value | Enforced By |
| ------- | ----- | ----------- |
| Line length | 140 characters | Ruff |
| Docstring coverage | 80% minimum | CI |
| Lint exceptions | Inline `# noqa` or `# pyright: ignore` | Ruff/pyright |

See pyproject.toml for the full list of rules.

**Avoid** adding exceptions to `pyproject.toml`—use inline comments to keep exceptions localized.

## When in doubt

Search the codebase for similar patterns!
