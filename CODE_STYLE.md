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

When handling union types, always use explicit type checks with a final error handler. **Never rely on type narrowing alone.**

**Why:** When a new type is added to a union, relying on type narrowing means the code silently falls through to a default case. With explicit type checks and a final error, you get a clear runtime error that forces you to handle the new type.

**✅ Correct patterns:**

Both `isinstance` chains and `match` statements (Python 3.10+) are acceptable. Both achieve the same exhaustive checking goal.

#### Pattern 1: isinstance chain (traditional)

```python
def handle_panel_isinstance(panel: PanelTypes) -> str:
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

#### Pattern 2: match statement (Python 3.10+)

```python
def handle_panel_match(panel: PanelTypes) -> str:
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

**Type checker pragmas:**

- For `isinstance` chains: Use `# pyright: ignore[reportUnnecessaryIsInstance]` to document intentional isinstance checks that the type checker considers unnecessary
- For `match` statements: Use `# pyright: ignore[reportUnnecessaryComparison]` on the wildcard case to document that it's intentionally kept for exhaustive checking

Do NOT remove these ignores - they document that the exhaustive checking pattern is intentional.

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

#### Leverage Pydantic's Features

**Core Principle: Take advantage of Pydantic's validation and type safety. Avoid manual dictionary manipulation.**

Pydantic is designed to give you type-safe, validated objects. Work with those objects directly instead of falling back to dict operations.

##### Working with Validated Data

**✅ Preferred - Use validated attributes:**

```python
from pydantic import model_validator
from typing_extensions import Self

class Dashboard(BaseCfgModel):
    panels: list[Panel]
    auto_layout: bool = False

    @model_validator(mode='after')
    def apply_auto_layout(self) -> Self:
        """Apply auto-layout to panels if enabled."""
        if not self.auto_layout:
            return self

        # Work with validated Panel objects
        for panel in self.panels:
            if panel.position.x is not None:  # Type-safe attribute access
                # ... positioning logic using panel.width, panel.height, etc.
        return self
```

**❌ Avoid - Manual dict manipulation:**

```python
@model_validator(mode='before')
@classmethod
def apply_auto_layout(cls, data: dict[str, Any]) -> dict[str, Any]:
    """Apply auto-layout to panels if enabled."""
    if not data.get('auto_layout'):
        return data

    # Manually manipulating dicts defeats the purpose of Pydantic
    for panel_dict in data.get('panels', []):
        if 'position' in panel_dict and panel_dict['position'].get('x') is not None:
            # No type safety, harder to read, easy to make mistakes
            # ...
    return data
```

##### When to Use Each Validator Mode

**Use `mode='after'` (the default and preferred choice):**

- Working with validated model attributes (most validators)
- Cross-field validation that reads multiple attributes
- Business logic that depends on fully validated data
- Any time you need type-safe access to model fields

**Use `mode='before'` only when necessary:**

- Raw input transformation before validation (e.g., converting date strings, normalizing keys)
- Data migrations (e.g., handling renamed fields from legacy schemas)
- Preprocessing data that can't be validated in its raw form

##### Best Practices

**Module-level imports:**

```python
# ✅ Correct - imports at module level
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from some_module import SomeType

class MyModel(BaseCfgModel):
    @model_validator(mode='after')
    def validate_something(self) -> Self:
        # Use SomeType here
        ...

# ❌ Incorrect - importing inside validator
class MyModel(BaseCfgModel):
    @model_validator(mode='after')
    def validate_something(self) -> Self:
        from some_module import SomeType  # Don't do this
        ...
```

**Type annotations match runtime types:**

Field annotations should reflect the actual type after validation completes:

```python
# ✅ Correct - annotation matches runtime type
w: int = Field(...)

@field_validator('w', mode='before')
@classmethod
def resolve_width(cls, value: int | SemanticWidth) -> int:
    """Convert semantic width to pixels."""
    return resolve_semantic_width(value)

# ❌ Incorrect - annotation includes types that never exist at runtime
w: int | SemanticWidth = Field(...)  # Misleading - always int after validation
```

**Generic types always have arguments:**

```python
# ✅ Correct - specific type arguments
panels: list[Panel]
metadata: dict[str, Any]

# ❌ Incorrect - bare generic types
panels: list  # Missing type argument
metadata: dict  # Missing type arguments
```

---

### Lint and Type Checking Exceptions

We do not add exceptions to pyproject.toml for linting and type checking. If you need to add an exception, you should add it with an inline ignore statement in the code.

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
| **Validators** | Work with validated attributes | Manipulate dicts manually |
| **Field docs** | Attribute docstrings | Inline comments |
| **Line length** | 140 chars max | No limit |

### Where to Find More

- **Python details**: This file (CODE_STYLE.md)
- **Python architecture**: `src/dashboard_compiler/AGENTS.md`
- **TypeScript details**: `vscode-extension/AGENTS.md`
- **JavaScript details**: `fixture-generator/AGENTS.md`
- **Linting config**: `pyproject.toml`
- **CodeRabbit guidance**: `CODERABBIT.md`
