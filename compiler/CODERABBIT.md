# CodeRabbit Configuration: Compiler (Python)

Instructions for CodeRabbit to improve code review accuracy for the kb-yaml-to-lens compiler.

**Core Principle:** Search codebase for similar patterns before flagging issues.

---

## Code Style

@CODE_STYLE.md

---

## Intentional Patterns

These patterns are project conventions—**do not flag**:

| Pattern | Rationale |
| ------- | --------- |
| Missing `model_config` on Pydantic models | Inherited from `BaseCfgModel`/`BaseModel` base classes |
| Explicit boolean comparisons (`if len(x) > 0`) | Project rejects implicit truthiness |
| isinstance chains with final `raise TypeError` | Exhaustive type dispatch pattern |
| `# pyright: ignore` pragmas | Documents intentional patterns |
| Ruff parent codes (e.g., `PLR`) | Enable all sub-rules (`PLR0911`, etc.) |

---

## Per-File Exemptions

| File Pattern | Allowed |
| ------------ | ------- |
| `tests/**/*.py` | `assert`, magic numbers, missing annotations |
| `**/view.py` | Mixed-case names, missing docstrings |
| `**/config.py` | Runtime type-checking imports |

---

## Review Focus

### What TO Review

- Logic errors and actual bugs
- Security issues
- Performance problems
- Missing error handling
- Breaking changes

### What NOT To Review

- Patterns listed in "Intentional Patterns" above
- Test file relaxations
- Type checker pragmas
- Style choices matching existing code

---

## Summary

- **DO** focus on logic errors, security, actual bugs
- **DO** check patterns match codebase
- **DON'T** flag intentional patterns (see table above)
- **DON'T** contradict `CODE_STYLE.md`

When in doubt: check `pyproject.toml`, `CODE_STYLE.md`, or `src/dashboard_compiler/shared/model.py`
