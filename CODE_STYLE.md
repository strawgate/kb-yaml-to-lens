# Code Style Guide

Code style conventions for kb-yaml-to-lens project.

---

## Python Code Style

> Applies to: `src/dashboard_compiler/`, `tests/`, `fixture-generator/python/`

### Explicit Boolean Comparisons

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

### Exhaustive Type Checking

Always use explicit type checks with a final error handler. Make adding new types to unions a runtime error, not a silent fallthrough:

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

### Pydantic Models

**Base Model Inheritance:**

All config and view models inherit from `BaseCfgModel` or `BaseModel` (defined in `src/dashboard_compiler/shared/model.py` and `config.py`).

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

### Other Best Practices

We use module-level imports (not inside validators) and type annotations match runtime types. Generic types always have arguments: `list[Panel]` not `list`. Use inline `# noqa xxx` or `# pyright: ignore[xxx]`, not global rules in pyproject.toml

---

## TypeScript Code Style

> Applies to: `vscode-extension/`

- Use TypeScript strict mode
- Avoid `any` types
- Use async/await for async operations
- Handle errors explicitly
- Sanitize HTML in webviews

See `vscode-extension/AGENTS.md` for details.

---

## JavaScript Code Style

> Applies to: `fixture-generator/`

- Use ES6+ features
- Use dual-generation pattern for new fixtures
- Test fixtures in Docker before committing
- Follow Kibana's LensConfigBuilder API patterns

See `fixture-generator/AGENTS.md` for details.

---

## Dashboard Style

`data_view` and `esql FROM` statements should target `logs-*` or `metrics-*` for importability.

---

## Quick Reference

| Pattern | Correct | Incorrect |
| ------- | ------- | --------- |
| **None checks** | `if x is not None:` | `if x:` |
| **Empty checks** | `if len(items) > 0:` | `if items:` |
| **Union handling** | isinstance chain + final error | Type narrowing alone |
| **Pydantic models** | Inherit from BaseCfgModel | Duplicate model_config |
| **Validators** | Work with validated attributes | Manipulate dicts manually |
| **Line length** | 140 chars max | No limit |

### Where to Find More

- **Python architecture**: `src/dashboard_compiler/AGENTS.md`
- **TypeScript details**: `vscode-extension/AGENTS.md`
- **JavaScript details**: `fixture-generator/AGENTS.md`
- **Linting config**: `pyproject.toml`
- **CodeRabbit guidance**: `CODERABBIT.md`
