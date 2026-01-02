# Agent Guidelines: VS Code Extension

> TypeScript extension providing live YAML dashboard compilation and preview for VS Code

---

## Quick Reference

### Essential Commands

| Command | Purpose |
| ------- | ------- |
| `npm install` | Install dependencies |
| `npm run compile` | Build TypeScript |
| `npm run watch` | Watch mode for development |
| `npm run lint` | Run ESLint |
| `npm test` | Run tests |
| `npm run package` | Create .vsix package |

### Development Workflow

```bash
# First time setup
npm install

# Development
npm run watch  # Start watch mode
# Press F5 in VS Code to launch Extension Development Host

# Before committing (from repository root)
make fix  # Auto-fix all linting issues
make ci   # Run all CI checks (linting + typecheck + tests)
```

---

## Architecture

### Overview

The extension uses a hybrid TypeScript + Python architecture:

- **TypeScript Extension** manages UI, commands, and Python subprocess
- **Python Server** handles actual compilation using `dashboard_compiler` package

### File Structure

| File | Purpose |
| ---- | ------- |
| `src/extension.ts` | Main entry point, command registration |
| `src/compiler.ts` | Python subprocess management, compilation requests |
| `src/previewPanel.ts` | Webview preview panel management |
| `src/gridEditorPanel.ts` | Visual grid layout editor |
| `src/fileWatcher.ts` | File change detection |
| `python/compile_server.py` | Stdio-based Python compilation server |

### Key Components

**Compiler Service** (`compiler.ts`):

- Manages Python subprocess lifecycle
- Sends compilation requests via stdin
- Receives JSON responses via stdout
- Handles errors and subprocess crashes

**Schema Registration** (`extension.ts`):

- Registers JSON schema with Red Hat YAML extension
- Fetches schema from LSP server (`dashboard/getSchema` endpoint)
- Provides auto-complete, validation, and hover documentation
- Automatically matches YAML files for dashboard editing

**Preview Panel** (`previewPanel.ts`):

- Webview-based dashboard preview
- Auto-refreshes on file save
- Export to NDJSON (copy/download)

**Grid Editor** (`gridEditorPanel.ts`):

- Drag-and-drop panel repositioning
- Interactive panel resizing
- Automatic YAML updates on changes

---

## Extension Commands

The extension provides these commands (accessible via Command Palette):

- `yamlDashboard.compile` - Compile current YAML file
- `yamlDashboard.preview` - Open preview panel
- `yamlDashboard.editLayout` - Open grid layout editor
- `yamlDashboard.export` - Export to NDJSON

---

## Configuration

Extension settings (VS Code settings.json):

| Setting | Type | Description | Default | Required |
| ------- | ---- | ----------- | ------- | -------- |
| `yamlDashboard.pythonPath` | string | Path to Python interpreter (must have dashboard_compiler package installed) | `"python"` | No |
| `yamlDashboard.compileOnSave` | boolean | Automatically compile dashboard when YAML file is saved | `true` | No |

---

## Development Guidelines

### TypeScript Style

- Use TypeScript strict mode
- Avoid `any` types where possible
- Use async/await for asynchronous operations
- Handle errors explicitly

### Python Server Protocol

The Python server uses stdio-based JSON-RPC:

**Request:**

```json
{
  "method": "compile",
  "params": {
    "file_path": "/path/to/dashboard.yaml"
  }
}
```

**Response (success):**

```json
{
  "success": true,
  "result": {
    "dashboard": { ... },
    "data_view": { ... }
  }
}
```

**Response (error):**

```json
{
  "success": false,
  "error": "Error message here"
}
```

### Webview Guidelines

- Use VS Code webview API for all UI panels
- Sanitize HTML content
- Use message passing for webview ↔ extension communication
- Handle webview lifecycle (dispose, reveal, etc.)

---

## Testing

### Manual Testing

1. Press F5 in VS Code to launch Extension Development Host
2. Open a test YAML file (e.g., `inputs/esql-controls-example.yaml`)
3. Test commands:
   - Compile Dashboard
   - Preview Dashboard
   - Edit Dashboard Layout
   - Export to NDJSON

### Automated Testing

```bash
npm test
```

Tests are located in `src/test/`:

- `suite/` - Integration tests
- `unit/` - Unit tests

---

## Common Issues

### Python Server Not Starting

**Symptoms:** "Python server not running" error

**Solutions:**

- Verify `dashboard_compiler` is installed: `python -c "import dashboard_compiler"`
- Check Python path in extension settings
- View Output panel (View → Output) → "YAML Dashboard Compiler"

### Compilation Errors

**Symptoms:** "Compilation failed" in preview

**Solutions:**

- Check YAML syntax
- Verify dashboard schema
- Test manually: `python -c "from dashboard_compiler.dashboard_compiler import load; load('file.yaml')"`

### Preview Not Updating

**Symptoms:** Preview doesn't refresh after save

**Solutions:**

- Check `yamlDashboard.compileOnSave` is enabled
- Manually run "Preview Dashboard" command
- Close and reopen preview panel

---

## AI Agent Guidelines

### Before Making Changes

1. **Read relevant files first** — Never modify TypeScript without reading it
2. **Understand the architecture** — Know the TypeScript ↔ Python boundary
3. **Check existing patterns** — Look at how other commands are implemented
4. **Test in Extension Development Host** — Always verify changes work

### Verification Checklist

Before claiming work is complete:

- [ ] TypeScript compiles without errors (`npm run compile`)
- [ ] ESLint passes (`npm run lint`)
- [ ] Extension loads in Development Host (press F5)
- [ ] All commands work as expected
- [ ] No console errors in Extension Host
- [ ] Python server starts and responds correctly

### Working with Python Server

When modifying the Python server (`python/compile_server.py`):

1. Changes must maintain the stdio JSON-RPC protocol
2. Test both success and error paths
3. Ensure proper error handling and logging
4. Remember: This runs as a subprocess, not in-process

---

## Related Resources

| Resource | Location |
| -------- | -------- |
| Main repository | `../README.md` |
| Python compiler | `../src/dashboard_compiler/` |
| Extension README | `README.md` |
| VS Code Extension API | <https://code.visualstudio.com/api> |
