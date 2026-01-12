# Agent Guidelines: VS Code Extension

> TypeScript extension for live YAML dashboard compilation and preview

---

## Commands

| Command | Purpose |
| ------- | ------- |
| `make install` | Install dependencies |
| `make ci` | Run all CI checks |
| `make fix` | Auto-fix linting |
| `make compile` | Build TypeScript |
| `make watch` | Watch mode |
| `make test` | Run tests |
| `make package` | Create .vsix package |

**Development:** `make install && make watch`, then F5 in VS Code

---

## Architecture

**Hybrid TypeScript + Python:**

- **TypeScript Extension** manages UI, commands, Python subprocess
- **Python Server** handles compilation using `dashboard_compiler`

| File | Purpose |
| ---- | ------- |
| `src/extension.ts` | Main entry, command registration |
| `src/compiler.ts` | Python subprocess management |
| `src/previewPanel.ts` | Webview preview panel |
| `src/gridEditorPanel.ts` | Visual grid editor |
| `python/compile_server.py` | Stdio-based Python server |

---

## Extension Commands

- `yamlDashboard.compile` - Compile current file
- `yamlDashboard.preview` - Open preview
- `yamlDashboard.editLayout` - Open grid editor
- `yamlDashboard.export` - Export to NDJSON

---

## Python Server Protocol

Stdio-based JSON-RPC:

**Request:** `{"method": "compile", "params": {"file_path": "/path/to/dashboard.yaml"}}`

**Response:** `{"success": true, "result": {...}}` or `{"success": false, "error": "message"}`

---

## Development Guidelines

- Use strict TypeScript mode, avoid `any` types
- Handle errors explicitly with async/await
- Test in Extension Development Host (F5)
- When modifying `python/compile_server.py`, maintain stdio protocol

---

## Common Issues

- **Python server not starting:** Verify `dashboard_compiler` installed, check Python path
- **Preview not updating:** Check `compileOnSave` setting, run compile command manually
