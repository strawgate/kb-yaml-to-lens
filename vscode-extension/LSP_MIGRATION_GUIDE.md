# LSP Migration Guide - Proof of Concept

This guide shows how to migrate from the current custom JSON-RPC implementation to a full LSP-based solution using pygls and vscode-languageclient.

## Overview

The POC demonstrates two approaches to using LSP for dashboard compilation:

1. **Standard LSP approach**: Using `workspace/executeCommand`
2. **Custom LSP methods**: Using custom request handlers (`dashboard/compile`, `dashboard/getDashboards`)

Both are implemented in the POC files for comparison.

## Files Created

- `python/compile_server_lsp.py` - LSP server using pygls
- `src/compiler-lsp.ts` - LSP client using vscode-languageclient
- This migration guide

## Dependencies Required

### TypeScript/VSCode Extension

Add to `package.json`:

```json
{
  "dependencies": {
    "vscode-languageclient": "^9.0.1"
  }
}
```

### Python Server

Add to `requirements.txt` or `pyproject.toml`:

```
pygls>=2.0.0
lsprotocol>=2024.0.0
```

Install with:
```bash
pip install pygls lsprotocol
```

## Implementation Approaches

### Approach 1: workspace/executeCommand (Standard LSP)

This uses the standard LSP `workspace/executeCommand` request. It's fully compliant with LSP spec.

**Python server (compile_server_lsp.py):**
```python
@server.command("dashboard.compile")
def compile_command(ls: LanguageServer, args):
    path = args[0]
    dashboard_index = args[1] if len(args) > 1 else 0
    # ... compilation logic
    return {"success": True, "data": result}
```

**TypeScript client (compiler-lsp.ts):**
```typescript
const result = await this.client.sendRequest(
    'workspace/executeCommand',
    {
        command: 'dashboard.compile',
        arguments: [filePath, dashboardIndex]
    }
);
```

**Pros:**
- ✅ Standard LSP, no protocol extension needed
- ✅ Works with any LSP-compliant client

**Cons:**
- ❌ More verbose (wrapped in executeCommand)
- ❌ Arguments are positional array, not named parameters

### Approach 2: Custom LSP Methods (Cleaner)

This uses custom request types (`dashboard/compile`). Requires extending the protocol but is cleaner.

**Python server (compile_server_lsp.py):**
```python
@server.feature("dashboard/compile")
def compile_custom(params: dict):
    path = params.get("path")
    dashboard_index = params.get("dashboard_index", 0)
    # ... compilation logic
    return {"success": True, "data": result}
```

**TypeScript client (compiler-lsp.ts):**
```typescript
const result = await this.client.sendRequest(
    'dashboard/compile',
    { path: filePath, dashboard_index: dashboardIndex }
);
```

**Pros:**
- ✅ Cleaner API with named parameters
- ✅ Easier to understand and maintain
- ✅ Can add custom TypeScript types

**Cons:**
- ❌ Non-standard LSP extension
- ❌ Requires documentation for custom methods

## File Watching with LSP

One major benefit of LSP is built-in file watching. The POC shows how to:

1. **Client side**: Register file watchers in `LanguageClientOptions`
```typescript
synchronize: {
    fileEvents: vscode.workspace.createFileSystemWatcher('**/*.yaml'),
}
```

2. **Server side**: Handle file change events
```python
@server.feature(types.TEXT_DOCUMENT_DID_SAVE)
def did_save(ls: LanguageServer, params: types.DidSaveTextDocumentParams):
    # Send notification to client that file changed
    ls.send_notification("dashboard/fileChanged", {"uri": file_path})
```

3. **Client side**: React to notifications
```typescript
this.client.onNotification('dashboard/fileChanged', (params) => {
    // Trigger recompilation or update UI
});
```

This eliminates the need for manual file system watchers!

## Migration Steps

If you decide to migrate to LSP, here's the recommended approach:

### Phase 1: Set up LSP infrastructure (2 hours)

1. Install dependencies:
   ```bash
   npm install vscode-languageclient
   pip install pygls lsprotocol
   ```

2. Replace `src/compiler.ts` with `src/compiler-lsp.ts`

3. Replace `python/compile_server.py` with `python/compile_server_lsp.py`

4. Update `src/extension.ts` to use the new compiler:
   ```typescript
   import { DashboardCompilerLSP } from './compiler-lsp';

   const compiler = new DashboardCompilerLSP(context);
   await compiler.start(); // Start LSP server
   ```

### Phase 2: Test basic functionality (1 hour)

1. Test compilation commands still work
2. Test multi-dashboard support
3. Test error handling

### Phase 3: Add LSP-specific features (optional, 2-4 hours)

1. Real-time diagnostics (validation as you type)
2. File watching and auto-recompile
3. Custom notifications for progress updates

## Comparison: Current vs LSP

| Feature | Current Implementation | LSP Implementation |
|---------|----------------------|-------------------|
| **Protocol** | Custom JSON-RPC (line-delimited) | Standard LSP (JSON-RPC 2.0) |
| **Transport** | stdio (child_process.spawn) | stdio (via LanguageClient) |
| **Dependencies** | None (Node.js stdlib only) | vscode-languageclient, pygls, lsprotocol |
| **Request handling** | Manual ID tracking, timeouts | Automatic (handled by libraries) |
| **Error handling** | Manual JSON parsing | Structured LSP error types |
| **File watching** | Manual (would need fs.watch) | Built-in (synchronize.fileEvents) |
| **Server lifecycle** | Manual spawn/kill | Auto-restart on crash |
| **Logging** | console.log/error | OutputChannel (visible in VSCode) |
| **Bidirectional notifications** | Not implemented | Built-in (server can notify client) |
| **Code size** | ~195 lines TS + ~106 lines Python | ~180 lines TS + ~170 lines Python |
| **Complexity** | Low (all custom code) | Medium (framework abstractions) |
| **Chunking support** | Would need manual implementation | Would still need manual implementation |

## When to Use LSP

LSP makes sense if you want:

✅ **Auto-restart on crash** - LanguageClient handles this automatically
✅ **File watching** - Built into LSP, no manual fs.watch needed
✅ **Bidirectional communication** - Server can send notifications to client
✅ **Real-time validation** - Diagnostics, error highlighting as you type
✅ **Future extensibility** - Easy to add hover, autocomplete, etc.
✅ **Industry standard** - Well-documented, widely used protocol

LSP might be overkill if:

❌ You only need simple request/response (no notifications, no file watching)
❌ You want zero dependencies
❌ Your current implementation works fine

## Recommended Approach for kb-yaml-to-lens

**Use Approach 2 (Custom LSP Methods)** if you decide to migrate:

1. It's cleaner than executeCommand
2. Named parameters are more maintainable
3. Can add TypeScript types for better IDE support
4. Only slightly non-standard (custom methods are common in LSP)

**Sample implementation:**

```typescript
// Define custom types
interface CompileParams {
    path: string;
    dashboard_index?: number;
}

interface CompileResult {
    success: boolean;
    data?: CompiledDashboard;
    error?: string;
}

// Use with type safety
const result = await client.sendRequest<CompileResult>(
    'dashboard/compile',
    { path: filePath, dashboard_index: 0 }
);
```

## Testing the POC

To test the LSP implementation:

1. Install dependencies:
   ```bash
   cd vscode-extension
   npm install vscode-languageclient
   pip install pygls lsprotocol
   ```

2. Update `extension.ts` to import and use `DashboardCompilerLSP`:
   ```typescript
   import { DashboardCompilerLSP } from './compiler-lsp';
   const compiler = new DashboardCompilerLSP(context);
   await compiler.start();
   ```

3. Press F5 to launch Extension Development Host

4. Open a YAML dashboard file and run compile command

## Chunking Note

**Important**: LSP does NOT solve the chunking problem mentioned in PR #107. Both LSP and the current implementation would need manual chunking for large responses (>1MB). LSP doesn't have built-in support for streaming large payloads.

If chunking is your main concern, you'd need to implement it the same way in both approaches:
- Send response in chunks
- Reassemble on client side
- Use response IDs to match chunks

## Questions?

This POC is meant to help you evaluate whether LSP is the right choice. The code is functional and demonstrates both standard and custom approaches to using LSP for compilation tasks.

Key decision points:
1. Do you value the LSP infrastructure (auto-restart, file watching, notifications)?
2. Are you okay with the new dependencies (pygls, vscode-languageclient)?
3. Do you plan to add more features (diagnostics, hover, autocomplete)?

If yes to most of these, LSP is a good fit. If not, the current implementation with incremental improvements (chunking, health checks) is perfectly fine.
