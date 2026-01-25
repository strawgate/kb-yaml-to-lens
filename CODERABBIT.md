# CodeRabbit Configuration: Project-Wide

Instructions for CodeRabbit to improve code review accuracy across the kb-yaml-to-lens project.

**Core Principle:** Search codebase for similar patterns before flagging issues.

---

## Project Architecture

@DEVELOPING.md

---

## Code Style

@CODE_STYLE.md

---

## Component-Specific Instructions

See component-specific CODERABBIT.md files for detailed review instructions:

- **Compiler (Python):** [packages/kb-dashboard-compiler/CODERABBIT.md](packages/kb-dashboard-compiler/CODERABBIT.md)
- **VS Code Extension (TypeScript):** [packages/vscode-extension/CODERABBIT.md](packages/vscode-extension/CODERABBIT.md)

---

## Review Focus

### What TO Review

1. Logic errors and actual bugs
2. Security issues (SQL injection, XSS, command injection, etc.)
3. Performance problems
4. Missing error handling
5. Breaking changes
6. Code not following established patterns

### What NOT To Review

1. Style choices that match existing patterns
2. Intentional deviations documented with pragmas
3. Test file relaxations (asserts, magic numbers)

---

## Summary

When reviewing kb-yaml-to-lens:

- **DO** focus on logic errors, security, actual bugs
- **DO** check patterns match codebase
- **DO** verify changes don't break functionality
- **DON'T** flag intentional patterns
- **DON'T** contradict project style guidelines

When in doubt, check `CODE_STYLE.md` and component-specific documentation.
