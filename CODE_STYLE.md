# Code Style Guide

This document consolidates code style conventions across all components of the kb-yaml-to-lens project.

---

## Python Code Style

> Applies to: `src/dashboard_compiler/`, `tests/`, `fixture-generator/python/`

### Explicit Boolean Comparisons

Always use explicit comparisons instead of implicit truthiness to avoid ambiguity.

**✅ Correct:**

```python
if my_var is not None:  # For optional types
if my_var is None:      # For None checks
if len(my_list) > 0:    # For non-empty lists
if len(my_str) > 0:     # For non-empty strings
if my_bool is True:     # For explicit True check
if my_bool:             # For boolean truthiness (acceptable for actual booleans)
```

**❌ Incorrect:**

```python
if my_var:      # Ambiguous: could be None, empty, False, 0, etc.
if not my_var:  # Ambiguous truthiness check
```

**Exception:** `if TYPE_CHECKING:` is standard Python and acceptable.

**Rationale:** Explicit comparisons make the intent clear and prevent bugs when values can be empty containers, zero, False, or None.

---

### Exhaustive Type Checking Pattern

When handling union types, always use explicit `isinstance` checks with a final error handler. **Never rely on type narrowing alone.**

**Why:** When a new type is added to a union, relying on type narrowing means the code silently falls through to a default case. With explicit isinstance checks and a final error, you get a clear runtime error that forces you to handle the new type.

**✅ Correct pattern:**

```python
def handle_panel(panel: PanelTypes) -> str:
    if isinstance(panel, MarkdownPanel):
        return handle_markdown(panel)
    if isinstance(panel, LinksPanel):
        return handle_links(panel)
    if isinstance(panel, (LensPanel, ESQLPanel)):  # pyright: ignore[reportUnnecessaryIsInstance]
        return handle_charts(panel)

    # Explicit error case instead of relying on type narrowing
    msg = f'Unknown panel type: {type(panel).__name__}'
    raise TypeError(msg)
```

**❌ Incorrect pattern:**

```python
def handle_panel(panel: PanelTypes) -> str:
    if isinstance(panel, MarkdownPanel):
        return handle_markdown(panel)
    if isinstance(panel, LinksPanel):
        return handle_links(panel)

    # Relying on type narrowing - if a new type is added to PanelTypes,
    # this silently handles it as a chart without any error
    return handle_charts(panel)
```

**Key principle:** Make adding new types to unions a compile-time or runtime error, not a silent fallthrough.

**Type checker pragmas:** Use `# pyright: ignore[reportUnnecessaryIsInstance]` to document intentional isinstance checks that the type checker considers unnecessary. Do NOT remove these ignores - they document that the pattern is intentional.

---

### Pydantic Model Conventions

#### Base Model Inheritance

All Pydantic configuration models inherit from `BaseCfgModel` or `BaseModel`, defined in:

- `src/dashboard_compiler/shared/model.py` - `BaseModel` with strict configuration
- `src/dashboard_compiler/shared/config.py` - `BaseCfgModel` extends `BaseModel`

**Base Model Configuration** (`BaseModel` in `shared/model.py`):

```python
model_config: ConfigDict = ConfigDict(
    strict=True,
    validate_default=True,
    extra='forbid',
    use_enum_values=True,
    frozen=True,
    use_attribute_docstrings=True,
    serialize_by_alias=True,
)
```

**Do NOT duplicate `model_config` settings** in models that inherit from `BaseCfgModel` or `BaseModel` - they automatically inherit these settings.

#### Field Documentation

Use attribute docstrings for field descriptions:

```python
class MyModel(BaseCfgModel):
    field_name: str
    """Description of what this field does."""

    another_field: int | None = None
    """Optional field with default value."""
```

#### View Models

View models (`BaseVwModel`) have special behaviors:

- Custom serializer omits fields with `OmitIfNone` metadata when value is `None`
- May narrow types in subclasses (e.g., `str` → `Literal['value']`)
- basedpyright's `reportIncompatibleVariableOverride = false` allows type narrowing

---

### Line Length

Maximum line length: **140 characters**

This is enforced by Ruff (configured in `pyproject.toml`).

**Exemptions:**

- Test files (`tests/**/*.py`) - relaxed via `E501` ignore

---

### Documentation Requirements

#### Docstring Coverage

The project maintains **80% docstring coverage** enforced in CI.

**Required docstrings:**

- Public functions and methods
- Public classes
- Module-level code

**Exemptions:**

- `__init__.py` files - excluded by `D100`
- Test functions and methods - excluded by `D104`
- Internal/private functions (prefixed with `_`)
- View models in `**/view.py` files - excluded by `D101`

---

### Linting Configuration

The project uses **Ruff** for linting with configuration in `pyproject.toml`.

#### Per-File Exemptions

**Test files** (`tests/**/*.py`):

- `S101` - `assert` statements allowed
- `PLR2004` - Magic numbers allowed
- `ANN201` - Missing return type annotations allowed
- `E501` - Line length limit relaxed

**View models** (`**/view.py`):

- `N815` - Mixed-case variable names allowed (matching Kibana JSON)
- `N803` - Lowercase argument names allowed
- `D101` - Missing class docstrings allowed
- `ERA001` - Commented-out code allowed (documenting JSON structure)

**Config models** (`**/config.py`):

- `TC001` - Type-checking-only imports at runtime allowed (Pydantic needs types)
- `TC008` - Quotes around type aliases allowed (forward references)

---

## TypeScript Code Style

> Applies to: `vscode-extension/`

See `vscode-extension/AGENTS.md` for TypeScript-specific conventions:

- Use TypeScript strict mode
- Avoid `any` types where possible
- Use async/await for asynchronous operations
- Handle errors explicitly
- Use VS Code webview API for all UI panels
- Sanitize HTML content
- Use message passing for webview ↔ extension communication

---

## JavaScript Code Style

> Applies to: `fixture-generator/`

See `fixture-generator/AGENTS.md` for JavaScript-specific conventions:

- Use ES6+ features (modules, async/await)
- Use the dual-generation pattern for new fixtures
- Always test fixtures in Docker before committing
- Follow Kibana's LensConfigBuilder API patterns

## Dashboard Style

data_view and esql FROM statements should always target either `logs-*` or `metrics-*`. We can have examples that target other things but they wont be importable by users without modification as it will fail to render the dashboard if the data_view or datastream (in the case of esql) is not valid.

---

## Summary

### Python Quick Reference

| Pattern | Correct | Incorrect |
| ------- | ------- | --------- |
| **None checks** | `if x is not None:` | `if x:` |
| **Empty checks** | `if len(items) > 0:` | `if items:` |
| **Union handling** | isinstance chain + final error | Type narrowing alone |
| **Pydantic models** | Inherit from BaseCfgModel | Duplicate model_config |
| **Field docs** | Attribute docstrings | Inline comments |
| **Line length** | 140 chars max | No limit |

### Where to Find More

- **Python details**: This file (CODE_STYLE.md)
- **Python architecture**: `src/dashboard_compiler/AGENTS.md`
- **TypeScript details**: `vscode-extension/AGENTS.md`
- **JavaScript details**: `fixture-generator/AGENTS.md`
- **Linting config**: `pyproject.toml`
- **CodeRabbit guidance**: `CODERABBIT.md`
