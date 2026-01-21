# CodeRabbit Configuration: VS Code Extension

Instructions for CodeRabbit to improve code review accuracy for the kb-yaml-to-lens VS Code extension.

**Core Principle:** Search codebase for similar patterns before flagging issues.

---

## Code Style

@CODE_STYLE.md

---

## Intentional Architecture Decisions

These are project conventions—**do not flag**:

| Decision | Rationale |
| -------- | --------- |
| Hybrid TypeScript + Python | TypeScript for UI, Python for compilation—separation is intentional |
| Stdio JSON protocol | Simple by design; don't suggest complex RPC frameworks |
| VS Code webview messaging | Native API; don't suggest external frameworks |

---

## Testing Philosophy

| Test Type | Focus | Do NOT Flag |
| --------- | ----- | ----------- |
| Python tests (`python/test_*.py`) | Business logic (grid extraction, YAML manipulation) | Missing TypeScript unit tests |
| E2E tests | Extension activation, commands | Missing tests for VS Code API wrappers |

Testing priority is on Python business logic, not TypeScript wrappers.

---

## Review Focus

### What TO Review

- Logic errors and actual bugs
- Security issues (path traversal, injection, CSP)
- Error handling in async code
- Breaking changes to Python server protocol
- Webview security

### What NOT To Review

- Hybrid architecture choices
- Test coverage for VS Code API wrappers
- Simple async patterns (errors bubble up in VS Code extensions)

---

## Summary

- **DO** focus on logic errors, security, async error handling
- **DO** verify webview security practices
- **DON'T** suggest architectural changes (TypeScript + Python separation)
- **DON'T** flag missing tests for VS Code wrappers

When in doubt: `CODE_STYLE.md`, `DEVELOPING.md`
