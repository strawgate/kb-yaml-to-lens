# CodeRabbit Configuration

Instructions for CodeRabbit to improve code review accuracy for kb-yaml-to-lens.

**Core Principle:** Search codebase for similar patterns before flagging issues.

---

## Project Architecture Context

### Pydantic Model Inheritance

All Pydantic models inherit from `BaseCfgModel` or `BaseModel` (defined in `src/dashboard_compiler/shared/model.py` and `config.py`).

Base `model_config` includes: `strict=True`, `validate_default=True`, `extra='forbid'`, `use_enum_values=True`, `frozen=True`, `use_attribute_docstrings=True`, `serialize_by_alias=True`.

**Do NOT flag missing `model_config`** on models inheriting from these base classes.

### Ruff Configuration

Parent rule codes enable all sub-rules. Examples:

- `PLR` enables `PLR0911`, `PLR2004`, etc.
- `PLW` enables all `PLW*` rules

**Do NOT flag rules as missing** when their parent category is in `extend-select`.

### Intentional isinstance Patterns

Exhaustive isinstance checking with final error handlers is intentional:

```python
if isinstance(panel, MarkdownPanel):
    return handle_markdown(panel)
if isinstance(panel, LinksPanel):
    return handle_links(panel)
if isinstance(panel, (LensPanel, ESQLPanel)):  # pyright: ignore[reportUnnecessaryIsInstance]
    return handle_charts(panel)

msg = f'Unknown panel type: {type(panel).__name__}'
raise TypeError(msg)  # Final error handler - KEEP THIS
```

**Do NOT suggest** removing isinstance checks or final error handlers.

### Python Code Style

Key project styles:

- Explicit boolean comparisons: `if x is not None:` not `if x:`
- Exhaustive isinstance chains with final error handlers
- Pydantic validators using `mode='after'`

**Do NOT suggest style changes** contradicting these patterns.

### Testing Patterns

Test files (`tests/**/*.py`) have relaxed rules: allow `assert`, magic numbers, missing annotations, longer lines.

**Do NOT flag these in test files**.

### Documentation Requirements

**Flag missing docstrings** on:

- Public functions and methods
- Public classes
- Module-level code (except `__init__.py`)

**Do NOT flag missing docstrings** on:

- Test functions/methods
- Private functions (prefixed with `_`)
- View models in `**/view.py` files

### Per-File Exemptions

**View models** (`**/view.py`): Allow mixed-case names, missing docstrings, commented code

**Config models** (`**/config.py`): Allow type-checking imports at runtime

---

## Review Focus

### What TO Review

1. Logic errors and actual bugs
2. Security issues (SQL injection, XSS, etc.)
3. Performance problems
4. Missing error handling
5. Breaking changes
6. Code not following established patterns

### What NOT To Review

1. Inherited Pydantic settings
2. Ruff rules when parent category enabled
3. Intentional isinstance chains
4. Explicit boolean comparisons
5. Test file relaxations
6. View model exemptions
7. Type checker pragmas documenting intentional patterns

---

## Common False Positives to Avoid

### 1. "Missing model_config on Pydantic Models"

Check if model inherits from `BaseCfgModel` or `BaseModel`. If yes, **do not flag**.

### 2. "Ruff rule not found in pyproject.toml"

Check if parent code (e.g., `PLR` for `PLR0911`) is in `extend-select`. If yes, **do not flag**.

### 3. "Unnecessary isinstance check"

Check if part of exhaustive dispatch pattern with final error handler. If yes, **do not flag**.

### 4. "Use implicit truthiness"

**Do not suggest**—project uses explicit comparisons.

### 5. "Remove assert from production code"

Check if file is in `tests/`. If yes, **do not flag**.

---

## Summary

When reviewing kb-yaml-to-lens:

✅ **DO** focus on logic errors, security, actual bugs
✅ **DO** check patterns match codebase
✅ **DO** verify changes don't break functionality
❌ **DON'T** flag inherited Pydantic settings
❌ **DON'T** suggest adding rules when parent enabled
❌ **DON'T** suggest removing intentional isinstance patterns
❌ **DON'T** contradict project style guidelines

When in doubt: `pyproject.toml`, `src/dashboard_compiler/AGENTS.md`, `src/dashboard_compiler/shared/model.py`, `CLAUDE.md`
