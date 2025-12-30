# CodeRabbit Configuration and Guidelines

This document provides specific instructions for CodeRabbit to improve the accuracy and relevance of code reviews for the kb-yaml-to-lens project.

## Project Architecture Context

### Pydantic Model Inheritance

**Important**: All Pydantic configuration models in this project inherit from `BaseCfgModel` or `BaseModel`, which are defined in `src/dashboard_compiler/shared/model.py` and `src/dashboard_compiler/shared/config.py`.

#### Base Model Configuration

The `BaseModel` class (in `src/dashboard_compiler/shared/model.py`) includes the following `model_config`:

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

The `BaseCfgModel` class (in `src/dashboard_compiler/shared/config.py:15`) extends `BaseModel` and inherits all these settings.

**Do NOT flag missing `model_config` settings on models that inherit from `BaseCfgModel` or `BaseModel`**. These models automatically inherit the strict configuration from the base classes.

### Ruff Configuration

The project uses Ruff for linting with configuration in `pyproject.toml`.

#### Rule Selection Pattern

When a parent rule code is enabled (e.g., `PLR`), it automatically enables **all** sub-rules in that category. For example:

- `PLR` in `extend-select` enables: `PLR0`, `PLR1`, `PLR2`, `PLR0###`, `PLR091`, `PLR0911`, `PLR0912`, `PLR0913`, etc.
- `PLW` enables all `PLW*` rules
- `PT` enables all `PT*` rules

**Do NOT flag rules as "not found in pyproject.toml" when their parent category is enabled**. Check if the parent code (first 3 characters for numbered rules, first 2-3 letters for others) exists in `extend-select` before suggesting the rule is missing.

Examples:

- `PLR0911` (too many return statements) → covered by `PLR`
- `PLR2004` (magic numbers) → covered by `PLR`
- `PTH123` (Path usage) → covered by `PTH`

### Intentional isinstance Patterns

#### Exhaustive Type Checking with isinstance

The codebase uses `isinstance` checks in dispatch functions as part of an **intentional exhaustive type checking pattern**. These checks are NOT unnecessary even when the type checker flags them as such.

**Pattern Location**: Files like `src/dashboard_compiler/panels/compile.py`, `src/dashboard_compiler/filters/compile.py`, and similar dispatch functions.

**Why This Pattern Exists**:

1. **Runtime Safety**: Provides clear runtime errors when new types are added to unions but not handled in dispatch logic
2. **Developer Guidance**: The `NotImplementedError` or `TypeError` at the end of isinstance chains guides developers to add handling for new types
3. **Type Narrowing**: Each isinstance check narrows the type for the code block, enabling proper type checking

**Example from `src/dashboard_compiler/panels/compile.py`**:

```python
def compile_dashboard_panel(panel: PanelTypes) -> tuple[list[KbnReference], KbnBasePanel]:
    if isinstance(panel, MarkdownPanel):
        # ... handle markdown
    if isinstance(panel, LinksPanel):
        # ... handle links
    if isinstance(panel, ImagePanel):
        # ... handle images
    if isinstance(panel, SearchPanel):
        msg = f'Panel type {type(panel).__name__} is not yet supported'
        raise NotImplementedError(msg)  # Intentional - guides development
    if isinstance(panel, (LensPanel, LensMultiLayerPanel, ESQLPanel)):
        # ... handle charts

    # Final safety net - should never be reached if PanelTypes is exhaustive
    msg = f'Unknown panel type: {type(panel).__name__}'
    raise TypeError(msg)
```

**Do NOT suggest**:

- Removing these isinstance checks
- Removing the final error-raising statements
- Marking these as "unnecessary" or "unreachable"

**These patterns are intentional defensive programming** that makes the codebase more maintainable when types are added or modified.

### Type Annotations and pyright Ignores

#### Intentional Type Ignores

The codebase uses `# pyright: ignore[reportUnnecessaryIsInstance]` in specific locations where:

1. The isinstance check is part of an exhaustive dispatch pattern (see above)
2. The type checker cannot understand the runtime necessity
3. Removing the check would reduce code maintainability

**Do NOT suggest removing these ignores** - they document that the isinstance check is intentional despite type checker warnings.

### Python Code Style

#### Explicit Boolean Comparisons

Per `src/dashboard_compiler/AGENTS.md`, the codebase uses **explicit boolean comparisons** instead of implicit truthiness:

**Preferred**:

```python
if x is not None:
if len(items) > 0:
if my_bool is True:
```

**Not preferred**:

```python
if x:
if items:
if my_bool:
```

**Do NOT suggest replacing explicit comparisons with implicit truthiness checks**. This is an intentional project style.

### Testing Patterns

#### Test File Rules

Test files in `tests/**/*.py` have relaxed linting rules (see `pyproject.toml:110-122`):

- `S101`: `assert` statements are allowed
- `PLR2004`: Magic numbers are allowed
- `ANN201`: Missing return type annotations are allowed
- `E501`: Line length limit is relaxed

**Do NOT flag these as issues in test files** - they are intentionally excluded from these rules.

### Documentation Requirements

#### Docstring Coverage

The project maintains an 80% docstring coverage threshold. This is enforced in CI.

**Flag missing docstrings** on:

- Public functions and methods
- Public classes
- Module-level code (except `__init__.py` - see `D100` in pyproject.toml)

**Do NOT flag missing docstrings** on:

- Test functions and methods (excluded by `D104`)
- Internal/private functions (prefixed with `_`)
- View models in `**/view.py` files (excluded by `D101` per-file ignore)

### Line Length

Maximum line length: **140 characters** (configured in `pyproject.toml:72`)

Flag lines exceeding this limit, but be aware that:

- Test files have this relaxed via `E501` ignore
- Some view model files may have exemptions

### Component-Specific Patterns

#### View Models (`**/view.py`)

View model files have specific exemptions (see `pyproject.toml:136-141`):

- `N815`: Mixed-case variable names are allowed (matching Kibana JSON format)
- `N803`: Lowercase argument names are allowed
- `D101`: Missing class docstrings are allowed
- `ERA001`: Commented-out code is allowed (used for documenting JSON structure)

**Do NOT flag these issues in view.py files**.

#### Config Models (`**/config.py`)

Config model files have specific exemptions (see `pyproject.toml:142-145`):

- `TC001`: Type-checking-only imports at runtime are allowed (Pydantic needs types at runtime)
- `TC008`: Quotes around type aliases are allowed (for forward references)

**Do NOT flag these as issues in config.py files**.

## Review Focus Areas

### What TO Review

1. **Logic Errors**: Actual bugs, incorrect implementations, off-by-one errors
2. **Security Issues**: SQL injection, command injection, XSS, path traversal, etc.
3. **Performance Problems**: Inefficient algorithms, unnecessary loops, memory leaks
4. **Missing Error Handling**: Unhandled edge cases, missing validation
5. **Breaking Changes**: Changes that would break existing functionality
6. **Inconsistencies**: Code that doesn't follow established patterns in the codebase

### What NOT To Review

1. **Inherited Pydantic Settings**: Don't flag missing `strict=True`, `extra='forbid'`, etc. on models inheriting from `BaseCfgModel`/`BaseModel`
2. **Enabled Ruff Rules**: Don't suggest adding rules to pyproject.toml when their parent category is already enabled
3. **Intentional isinstance Chains**: Don't suggest removing isinstance checks or final error handlers in dispatch functions
4. **Explicit Boolean Comparisons**: Don't suggest `if x:` instead of `if x is not None:`
5. **Test File Relaxations**: Don't flag assert usage, magic numbers, or missing annotations in test files
6. **View Model Exemptions**: Don't flag mixed-case names or missing docstrings in `**/view.py` files
7. **Type Checker Pragmas**: Don't suggest removing `# pyright: ignore` comments that document intentional patterns

## Common False Positives to Avoid

### 1. "Missing model_config on Pydantic Models"

**Before flagging**, check if the model inherits from `BaseCfgModel` or `BaseModel`. If yes, **do not flag**.

### 2. "Ruff rule PLR0911 not found in pyproject.toml"

**Before flagging**, check if `PLR` is in `extend-select` (it is). If yes, **do not flag** - the rule is enabled.

### 3. "Unnecessary isinstance check - type is already known"

**Before flagging**, check if this is part of an exhaustive dispatch pattern (multiple isinstance checks with a final error handler). If yes, **do not flag** - this is intentional.

### 4. "Use implicit truthiness instead of explicit comparison"

**Do not suggest this** - the project uses explicit boolean comparisons as a style guideline.

### 5. "Remove assert from production code"

**Before flagging**, check if the file is in `tests/` directory. If yes, **do not flag** - asserts are allowed in tests.

## Summary

When reviewing code for kb-yaml-to-lens:

1. ✅ **DO** focus on logic errors, security issues, and actual bugs
2. ✅ **DO** check that new patterns match existing codebase conventions
3. ✅ **DO** verify that changes don't break existing functionality
4. ❌ **DON'T** flag inherited Pydantic settings as missing
5. ❌ **DON'T** suggest adding rules when parent categories are enabled
6. ❌ **DON'T** suggest removing intentional isinstance patterns
7. ❌ **DON'T** suggest style changes that contradict project guidelines

When in doubt, check the relevant configuration files:

- `pyproject.toml` - Ruff rules and exemptions
- `src/dashboard_compiler/AGENTS.md` - Coding standards
- `src/dashboard_compiler/shared/model.py` - Base Pydantic configuration
- `CLAUDE.md` - Overall project guidelines
