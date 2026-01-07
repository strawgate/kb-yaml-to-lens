# Code Style Guide

Code style conventions for kb-yaml-to-lens project.

---

## Component-Specific Style Guides

Each component has detailed style guidelines in their respective AGENTS.md files:

### Python (Compiler)

> Applies to: `compiler/src/dashboard_compiler/`, `compiler/tests/`

**Key conventions:**

- Explicit boolean comparisons (`if x is not None:` not `if x:`)
- Exhaustive type checking with final error handlers
- Pydantic validators using `mode='after'`
- Line length: 140 characters max (Ruff enforced)
- Docstring coverage: 80% enforced in CI

**See:** `compiler/AGENTS.md` for complete Python code style guidelines

---

### TypeScript (VS Code Extension)

> Applies to: `vscode-extension/`

**Key conventions:**

- Use TypeScript strict mode
- Avoid `any` types
- Use async/await for async operations
- Handle errors explicitly
- Sanitize HTML in webviews

**See:** `vscode-extension/AGENTS.md` for details

---

### JavaScript/TypeScript (Fixture Generator)

> Applies to: `fixture-generator/`

**Key conventions:**

- Use ES6+ features
- Use dual-generation pattern for new fixtures
- Test fixtures in Docker before committing
- Follow Kibana's LensConfigBuilder API patterns
- Use TypeScript type checking for generators

**See:** `fixture-generator/AGENTS.md` for details

---

## Global Conventions

### Dashboard Style

`data_view` and `esql FROM` statements should target `logs-*` or `metrics-*` for importability.

### Where to Find More

| Topic | Location |
| ----- | -------- |
| **Python/Compiler** | `compiler/AGENTS.md` |
| **TypeScript/Extension** | `vscode-extension/AGENTS.md` |
| **JavaScript/Fixtures** | `fixture-generator/AGENTS.md` |
| **Linting config** | `pyproject.toml` (Python), component configs (TS/JS) |
| **CodeRabbit guidance** | `CODERABBIT.md` (root), `compiler/CODERABBIT.md` (Python) |
