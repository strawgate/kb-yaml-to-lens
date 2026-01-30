# Code Style Guide: kb-dashboard-mcp

This document defines code conventions for the MCP server package.

## General Principles

- Follow the [root CODE_STYLE.md](../../CODE_STYLE.md) for project-wide conventions
- See [kb-dashboard-cli CODE_STYLE.md](../kb-dashboard-cli/CODE_STYLE.md) for Python-specific patterns

## Python Conventions

### Line Length

- Maximum 140 characters per line

### Quotes

- Single quotes for code: `'hello'`
- Double quotes for docstrings: `"""Docstring."""`

### Type Annotations

- All functions must have type annotations
- **Do NOT use** `from __future__ import annotations` (same as kb-dashboard-cli and kb-dashboard-core)
- Use Pydantic models for complex data structures

### Async Patterns

- All Elasticsearch operations must be async
- Use `KibanaClient` from `kb-dashboard-tools` for all cluster operations
- Follow existing async patterns from kb-dashboard-tools

### Pydantic Models

```python
from pydantic import BaseModel, Field


class MyModel(BaseModel):
    """Model description."""

    field_name: str = Field(description='Field description')
```

### Explicit Boolean Comparisons

```python
# Correct
if my_var is not None:
    ...
if len(my_list) > 0:
    ...

# Avoid
if my_var:
    ...
if my_list:
    ...
```

### Error Messages

```python
# Correct - use intermediate variable
msg = f'Invalid value: {value}'
raise ValueError(msg)

# Avoid - inline f-string
raise ValueError(f'Invalid value: {value}')
```

## Linting

- Ruff for linting and formatting
- BasedPyright for type checking

Run checks:

```bash
make lint-check   # Check linting
make typecheck    # Type checking
make ci           # All checks
```

Auto-fix issues:

```bash
make fix          # Auto-fix linting
```
