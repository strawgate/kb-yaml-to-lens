# YAML Dashboard Compiler - VS Code Extension

A VS Code extension that provides live compilation and preview for Kibana YAML dashboards. This extension makes it fast and easy to edit and work with YAML dashboard files by automatically compiling them on save and providing a live preview.

## Features

- **Auto-compile on Save**: Automatically compiles your YAML dashboard files whenever you save them
- **Live Preview**: View your compiled dashboard in a side-by-side preview panel with live reload functionality
- **Export to NDJSON**: Copy or download compiled dashboards as NDJSON for direct import into Kibana
- **Error Reporting**: Clear error messages when compilation fails
- **Python Integration**: Leverages the existing `dashboard_compiler` Python package

## Requirements

- Python 3.10 or higher
- The `dashboard_compiler` package must be installed and available in your Python environment
- VS Code 1.85.0 or higher

## Installation

### From VSIX (Manual Installation)

1. Build the extension:

   ```bash
   cd vscode-extension
   npm install
   npm run compile
   npm run package
   ```

2. Install in VS Code:
   - Open VS Code
   - Go to Extensions view (Ctrl+Shift+X)
   - Click the "..." menu at the top of the Extensions view
   - Select "Install from VSIX..."
   - Choose the generated `.vsix` file

### For Development

1. Clone the repository
2. Navigate to the extension folder:

   ```bash
   cd vscode-extension
   npm install
   ```

3. Open the folder in VS Code:

   ```bash
   code .
   ```

4. Press F5 to launch the Extension Development Host

## Setup

### Python Environment

The extension requires the `dashboard_compiler` package to be installed in your Python environment:

```bash
# From the repository root
pip install -e .
```

Or if you're using Poetry:

```bash
poetry install
```

### Extension Configuration

Configure the extension in VS Code settings:

- **`yamlDashboard.pythonPath`**: Path to your Python interpreter (default: `python`)
  - Example: `/usr/bin/python3`
  - Example: `~/.pyenv/versions/3.11.0/bin/python`
  - Example (Windows): `C:\\Python311\\python.exe`

- **`yamlDashboard.compileOnSave`**: Enable/disable automatic compilation on save (default: `true`)

## Usage

### Commands

The extension provides the following commands (accessible via Command Palette - Ctrl+Shift+P):

- **YAML Dashboard: Compile Dashboard** - Manually compile the current YAML file
- **YAML Dashboard: Preview Dashboard** - Open preview panel for the current YAML file
- **YAML Dashboard: Export Dashboard to NDJSON** - Copy compiled NDJSON to clipboard

### Keyboard Shortcuts

You can add custom keyboard shortcuts in VS Code:

```json
{
  "key": "ctrl+shift+p",
  "command": "yamlDashboard.preview",
  "when": "resourceLangId == yaml"
}
```

### Workflow

1. Open a YAML dashboard file (e.g., `inputs/aerospike-cluster/metrics-cluster.yaml`)
2. The extension activates automatically for YAML files
3. Save the file (Ctrl+S) - it will automatically compile
4. Run "YAML Dashboard: Preview Dashboard" to see the compiled output
5. The preview updates automatically when you save changes
6. Use the "Copy NDJSON" button in the preview to export for Kibana

## Preview Panel

The preview panel shows:

- **Dashboard Title**: The title from your YAML configuration
- **File Path**: The current file being previewed
- **Export Buttons**:
  - Copy NDJSON to clipboard
  - Download NDJSON file
- **Dashboard Information**: Type, ID, version
- **Compiled Output**: Pretty-printed JSON view of the compiled dashboard

## Importing to Kibana

1. Use the "Copy NDJSON for Kibana Import" button in the preview
2. In Kibana, navigate to: **Stack Management → Saved Objects → Import**
3. Paste or upload the NDJSON file
4. Your dashboard is now available in Kibana!

## Troubleshooting

### Python server not starting

**Problem**: Extension shows "Python server not running" error

**Solutions**:
- Verify `dashboard_compiler` is installed: `python -c "import dashboard_compiler"`
- Check the Python path in extension settings
- View the Output panel (View → Output) and select "YAML Dashboard Compiler" to see logs

### Compilation errors

**Problem**: "Compilation failed" messages

**Solutions**:
- Check your YAML syntax
- Verify your dashboard structure matches the expected schema
- Review the error message in the preview panel for details
- Test compilation manually: `python -c "from dashboard_compiler.dashboard_compiler import load; load('your_file.yaml')"`

### Preview not updating

**Problem**: Preview doesn't refresh after saving

**Solutions**:
- Check that `yamlDashboard.compileOnSave` is enabled
- Try manually running "YAML Dashboard: Preview Dashboard"
- Close and reopen the preview panel

### Python path issues

**Problem**: Extension can't find Python or packages

**Solutions**:
- Use absolute path in settings: `"yamlDashboard.pythonPath": "/full/path/to/python"`
- For virtual environments, use the venv Python: `"yamlDashboard.pythonPath": "/path/to/venv/bin/python"`
- For conda: `"yamlDashboard.pythonPath": "/path/to/conda/envs/yourenv/bin/python"`

## Architecture

The extension uses a hybrid TypeScript + Python architecture:

- **TypeScript Extension** (`src/`):
  - `extension.ts`: Main extension entry point and command registration
  - `compiler.ts`: Manages Python subprocess and compilation requests
  - `previewPanel.ts`: Handles webview preview panel
  - `fileWatcher.ts`: Watches for file changes and triggers compilation

- **Python Server** (`python/compile_server.py`):
  - Stdio-based server that handles compilation requests
  - Uses the existing `dashboard_compiler` package
  - Runs as a subprocess managed by the TypeScript extension

## Development

### Building

```bash
npm run compile      # Compile TypeScript
npm run watch        # Watch mode for development
npm run lint         # Run ESLint
npm run package      # Create .vsix package
```

### Testing

1. Press F5 in VS Code to launch Extension Development Host
2. Open a test YAML file (e.g., `tests/scenarios/one-pie-chart/config.yaml`)
3. Test the commands and preview functionality

### Contributing

Contributions are welcome! Please see the main repository's [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## License

MIT - See [LICENSE](../LICENSE) for details.

## Related Links

- [Main Repository](https://github.com/strawgate/kb-yaml-to-lens)
- [Kibana Lens Documentation](https://github.com/elastic/kibana/tree/main/x-pack/platform/plugins/shared/lens)
- [VS Code Extension API](https://code.visualstudio.com/api)
