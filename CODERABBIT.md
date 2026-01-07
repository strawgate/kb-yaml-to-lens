# CodeRabbit Configuration

Instructions for CodeRabbit to improve code review accuracy for kb-yaml-to-lens.

**Core Principle:** Search codebase for similar patterns before flagging issues.

---

## Component-Specific Guidelines

This is a multi-language project. Review guidelines vary by component:

### Python (Compiler)

For files in `compiler/`:

**See:** `compiler/CODERABBIT.md` for complete Python/compiler-specific review guidelines

**Key patterns to understand:**

- Pydantic model inheritance (`BaseCfgModel`)
- Ruff parent rule codes
- Intentional isinstance chains with final error handlers
- Explicit boolean comparisons
- Test file exemptions

### TypeScript (VS Code Extension)

For files in `vscode-extension/`:

**See:** `vscode-extension/AGENTS.md` for TypeScript conventions

**Key patterns:**

- Strict mode TypeScript
- Webview security requirements
- Python subprocess management patterns

### JavaScript/TypeScript (Fixture Generator)

For files in `fixture-generator/`:

**See:** `fixture-generator/AGENTS.md` for fixture generator conventions

**Key patterns:**

- Dual-generation pattern (ES|QL + Data View)
- LensConfigBuilder API usage
- Docker-based generation workflow

---

## Global Review Focus

### What TO Review (All Components)

1. Logic errors and actual bugs
2. Security issues
3. Performance problems
4. Missing error handling
5. Breaking changes
6. Code not following established patterns

### What NOT To Review (All Components)

1. Style issues already covered by linters
2. Patterns that are intentional (documented in component AGENTS.md)
3. Component-specific conventions (check component docs first)

---

## When in Doubt

Consult these files based on the component being reviewed:

| Component | Primary Reference | Secondary Reference |
| --------- | ----------------- | ------------------- |
| **Compiler** (`compiler/`) | `compiler/CODERABBIT.md` | `compiler/AGENTS.md` |
| **VS Code Extension** (`vscode-extension/`) | `vscode-extension/AGENTS.md` | - |
| **Fixture Generator** (`fixture-generator/`) | `fixture-generator/AGENTS.md` | - |
| **Global** | `AGENTS.md` | `CODE_STYLE.md` |
