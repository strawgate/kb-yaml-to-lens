# Manual Integration Test Guide

Since Puppeteer automation can be finicky, here's a manual test checklist that achieves the same validation.

## Setup

1. **Load Extension in Chrome**
   - Go to `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select the `browser-extension` directory
   - Note the extension ID (shown on the extension card)

2. **Open Side Panel**
   - Click the extension icon in Chrome toolbar
   - Side panel should open on the right

## Test Checklist

### ✅ Test 1: Side Panel Loads
- [ ] Side panel opens without errors
- [ ] Header shows "📊 Kibana Dashboard Builder"
- [ ] Status shows "Initializing..." initially

### ✅ Test 2: Pyodide Initialization
- [ ] Open DevTools (right-click side panel → Inspect)
- [ ] Check Console tab
- [ ] Should see: `[Pyodide] Starting initialization...`
- [ ] Wait 10-30 seconds
- [ ] Should see: `[Pyodide] Initialization complete in X.XXs`
- [ ] Status should change to "Ready!" (green)

### ✅ Test 3: YAML Compilation
- [ ] Editor shows sample YAML dashboard
- [ ] Edit the YAML (change a title or add a panel)
- [ ] Wait ~500ms (debounce)
- [ ] Status should show "Compiled in Xms"
- [ ] Preview should update automatically

### ✅ Test 4: Preview Rendering
- [ ] Visual tab shows dashboard grid with colored panels
- [ ] Click "JSON" tab
- [ ] Should see formatted JSON output
- [ ] Switch back to "Visual" tab

### ✅ Test 5: Export Functionality
- [ ] Click "Export" button
- [ ] File should download (check Downloads folder)
- [ ] File should be valid NDJSON (can open in text editor)

### ✅ Test 6: Error Handling
- [ ] Type invalid YAML (remove a colon)
- [ ] Should see red error panel at bottom
- [ ] Error message should describe the problem
- [ ] Fix the YAML - error should disappear

## Expected Console Output

When everything works, you should see in the console:

```
[Pyodide] Creating PythonCompiler instance...
[Pyodide] PythonCompiler instance created, ready to initialize
[Editor] DOMContentLoaded fired
[Editor] window.pythonCompiler exists? true
[Editor] Initializing...
[Editor] Monaco (textarea) initialized
[Editor] Starting Python compiler initialization...
[Pyodide] Starting initialization...
[Pyodide] Script loaded, initializing runtime...
[Pyodide] Using local indexURL: chrome-extension://...
[Pyodide] Runtime initialized, installing packages...
[Pyodide] Packages installed, loading compiler...
[Pyodide] Compiler code loaded
[Pyodide] Initialization complete in X.XXs
[Editor] Ready!
```

## Troubleshooting

**"Pyodide not initializing"**
- Check console for errors
- Verify all Pyodide files exist: `ls -la lib/pyodide/`
- Run `./setup.sh` if files are missing

**"CSP errors"**
- Check manifest.json has `content_security_policy` with `wasm-unsafe-eval`
- Reload extension after manifest changes

**"Compilation fails"**
- Check YAML syntax
- Look for Python errors in console
- Try minimal YAML first

## Success Criteria

✅ All tests pass if:
- Side panel opens
- Pyodide initializes in < 30 seconds
- YAML compiles successfully
- Preview updates automatically
- Export downloads valid file
- No console errors (except network warnings are OK)
