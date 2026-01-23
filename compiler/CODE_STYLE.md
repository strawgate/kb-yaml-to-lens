# Code Style: Python Compiler

This document describes Python code style conventions that are **atypical** but **mandatory** in this project.

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

All models should inherit from `BaseCfgModel` (defined in `src/dashboard_compiler/shared/config.py`) or `BaseVwModel` (defined in `src/dashboard_compiler/shared/model.py`).

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
