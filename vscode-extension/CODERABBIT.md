# CodeRabbit Configuration: VS Code Extension

Instructions for CodeRabbit to improve code review accuracy for the kb-yaml-to-lens VS Code extension.

**Core Principle:** Search codebase for similar patterns before flagging issues.

---

## Code Style

@CODE_STYLE.md

---

## Project Architecture Context

### Hybrid TypeScript + Python

The extension uses TypeScript for UI and command handling, with a Python subprocess for YAML compilation.

**Do NOT suggest** merging the Python server into TypeScript—the separation is intentional.

### Python Server Protocol

The stdio-based JSON-RPC protocol is simple by design:

```json
{"method": "compile", "params": {"file_path": "/path/to/dashboard.yaml"}}
```

**Do NOT suggest** more complex RPC frameworks unless there's a specific need.

### Webview Architecture

Webviews (preview panel, grid editor) communicate via VS Code's webview messaging API.

**Do NOT suggest** using external frameworks for webview state management.

---

## Testing Patterns

### Python Tests

Test files (`python/test_*.py`) focus on business logic:

- Grid extraction and updates
- YAML manipulation
- Input validation

**Do NOT flag** missing tests for simple TypeScript classes—testing priority is on Python business logic.

### E2E Tests

E2E tests run in a headless VS Code instance. They verify:

- Extension activation
- Command registration
- Basic compilation flow

**Do NOT suggest** extensive TypeScript unit tests for VS Code API wrappers.

---

## Review Focus

### What TO Review

1. Logic errors and actual bugs
2. Security issues (path traversal, injection, etc.)
3. Error handling in async code
4. Breaking changes to the Python server protocol
5. Webview security (CSP, input sanitization)

### What NOT To Review

1. TypeScript strict mode choices (project uses strict)
2. Test coverage for VS Code API wrappers
3. Simple class existence tests
4. Hybrid architecture (TypeScript + Python)

---

## Common False Positives to Avoid

### 1. "Add unit tests for this class"

Check if the class is a thin wrapper around VS Code APIs. If yes, **do not flag**—testing priority is on Python business logic.

### 2. "Consider using a typed RPC library"

The current stdio JSON protocol is simple and sufficient. **Do not suggest** complexity unless needed.

### 3. "Missing error handling"

Check if the error is propagated to the caller. VS Code extension patterns often let errors bubble up. **Verify the full call chain** before flagging.

---

## Summary

When reviewing kb-yaml-to-lens extension:

- **DO** focus on logic errors, security, async error handling
- **DO** verify webview security practices
- **DO** check Python server protocol changes for compatibility
- **DON'T** suggest merging Python into TypeScript
- **DON'T** flag missing tests for VS Code API wrappers
- **DON'T** suggest complex RPC frameworks

When in doubt: `vscode-extension/CODE_STYLE.md`, `vscode-extension/DEVELOPING.md`
