# YAML Dashboard Compiler - VS Code Extension

A VS Code extension that provides live compilation and preview for Kibana YAML dashboards. This extension makes it fast and easy to edit and work with YAML dashboard files by automatically compiling them on save and providing a live preview.

## Features

- **Auto-complete and Validation**: Schema-based auto-complete, validation, and hover documentation for YAML dashboard files (powered by Red Hat YAML extension)
- **Code Snippets**: Pre-built snippets for all panel types, controls, and layouts - just start typing a prefix like `panel-lens-metric` and press Tab
- **Auto-compile on Save**: Automatically compiles your YAML dashboard files whenever you save them
- **Live Preview**: View your compiled dashboard in a side-by-side preview panel with live reload functionality
- **Visual Grid Layout Editor**: Drag and drop panels to rearrange them, resize panels interactively, with automatic YAML updates
- **Export to NDJSON**: Copy or download compiled dashboards as NDJSON for direct import into Kibana
- **Open in Kibana**: Upload dashboards directly to Kibana and open them in your browser with one command
- **Secure Credential Storage**: Kibana credentials stored encrypted using VS Code's SecretStorage API (OS keychain)
- **Error Reporting**: Clear error messages when compilation fails
- **Python Integration**: Leverages the existing `dashboard_compiler` Python package

## Requirements

- Python 3.12 or higher
- The `dashboard_compiler` package must be installed and available in your Python environment
- VS Code 1.85.0 or higher
- Red Hat YAML extension (automatically installed as a dependency)

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

Or using uv:

```bash
uv sync
```

### Extension Configuration

Configure the extension in VS Code settings:

- **`yamlDashboard.pythonPath`**: Path to your Python interpreter (default: `python`)
  - Example: `/usr/bin/python3`
  - Example: `~/.pyenv/versions/3.11.0/bin/python`
  - Example (Windows): `C:\\Python311\\python.exe`

- **`yamlDashboard.compileOnSave`**: Enable/disable automatic compilation on save (default: `true`)

- **`yamlDashboard.kibana.url`**: Kibana base URL for uploading dashboards (default: `http://localhost:5601`)

- **`yamlDashboard.kibana.sslVerify`**: Verify SSL certificates when connecting to Kibana (default: `true`)

- **`yamlDashboard.kibana.browserType`**: Browser to use when opening Kibana dashboards (default: `external`)
  - `external`: Open in system default browser
  - `simple`: Open in VS Code's built-in simple browser

- **`yamlDashboard.kibana.uploadOnSave`**: Automatically upload dashboard to Kibana when YAML file is saved (default: `false`)
  - Requires Kibana URL and credentials to be configured
  - Shows subtle status messages in the status bar
  - Errors are displayed in the status bar (no intrusive popups)

## Usage

### Commands

The extension provides the following commands (accessible via Command Palette - Ctrl+Shift+P):

- **YAML Dashboard: Compile Dashboard** - Manually compile the current YAML file
- **YAML Dashboard: Preview Dashboard** - Open preview panel for the current YAML file
- **YAML Dashboard: Edit Dashboard Layout** - Open visual grid layout editor for drag-and-drop panel positioning
- **YAML Dashboard: Export Dashboard to NDJSON** - Copy compiled NDJSON to clipboard
- **YAML Dashboard: Open in Kibana** - Upload dashboard to Kibana and open it in your browser
- **YAML Dashboard: Set Kibana Username** - Store Kibana username securely
- **YAML Dashboard: Set Kibana Password** - Store Kibana password securely
- **YAML Dashboard: Set Kibana API Key** - Store Kibana API key securely (recommended)
- **YAML Dashboard: Clear Kibana Credentials** - Remove all stored Kibana credentials

### Keyboard Shortcuts

You can add custom keyboard shortcuts in VS Code:

```json
{
  "key": "ctrl+shift+p",
  "command": "yamlDashboard.preview",
  "when": "resourceLangId == yaml"
}
```

### Using Code Snippets

The extension provides comprehensive code snippets to speed up dashboard creation:

1. **Start typing a snippet prefix** - e.g., `panel-lens-metric`, `panel-markdown`, `control-options`
2. **Press Tab** to insert the snippet (or Ctrl+Space to see available completions)
3. **Tab through placeholders** to fill in values
4. **Use dropdown menus** where provided (e.g., aggregation types)

**Available Snippet Prefixes:**

| Prefix | Description |
| ------ | ----------- |
| `dashboard` | Complete dashboard structure with panels array |
| `panel-markdown` | Markdown content panel |
| `panel-search` | Saved search panel |
| `panel-links` | Links panel with multiple links |
| `panel-image` | Image panel |
| `panel-lens-metric` | Lens metric visualization |
| `panel-lens-pie` | Lens pie chart |
| `panel-lens-line` | Lens line chart |
| `panel-lens-bar` | Lens bar chart |
| `panel-lens-area` | Lens area chart |
| `panel-lens-datatable` | Lens data table |
| `panel-lens-gauge` | Lens gauge |
| `panel-esql-metric` | ES\|QL metric panel |
| `panel-esql-line` | ES\|QL line chart |
| `panel-esql-bar` | ES\|QL bar chart |
| `panel-esql-datatable` | ES\|QL data table |
| `grid-full` | Full width grid layout (48 units) |
| `grid-half` | Half width grid layout (24 units) |
| `grid-third` | Third width grid layout (16 units) |
| `grid-quarter` | Quarter width grid layout (12 units) |
| `control-options` | Options list control |
| `control-range` | Range slider control |
| `control-time` | Time slider control |

**Note for Cursor Users:** In Cursor, IntelliSense auto-complete is disabled by default. Press **Ctrl+Space** (or **Cmd+Space** on Mac) to manually trigger auto-complete suggestions and see available snippets.

### Workflow

1. Open a YAML dashboard file (e.g., `inputs/aerospike-cluster/metrics-cluster.yaml`)
2. The extension activates automatically for YAML files
3. **Use snippets** to quickly insert panels - start typing a prefix like `panel-lens-metric` and press Tab
4. Save the file (Ctrl+S) - it will automatically compile
5. Run "YAML Dashboard: Preview Dashboard" to see the compiled output
6. Run "YAML Dashboard: Edit Dashboard Layout" to visually rearrange panels
   - Drag panels to move them on the 48-column Kibana grid
   - Drag the bottom-right corner of panels to resize them
   - Changes are saved automatically to the YAML file
   - Use "Show Grid Lines" and "Snap to Grid" options for easier alignment
7. The preview updates automatically when you save changes
8. Use the "Copy NDJSON" button in the preview to export for Kibana
9. **(Optional)** Enable `yamlDashboard.kibana.uploadOnSave` to automatically upload to Kibana on every save

## Preview Panel

The preview panel shows:

- **Dashboard Title**: The title from your YAML configuration
- **File Path**: The current file being previewed
- **Export Buttons**:
  - Copy NDJSON to clipboard
  - Download NDJSON file
- **Dashboard Information**: Type, ID, version
- **Compiled Output**: Pretty-printed JSON view of the compiled dashboard

## Uploading to Kibana

### Option 1: Direct Upload (Recommended)

The extension can upload dashboards directly to Kibana and open them in your browser:

1. **Configure Kibana URL** (one-time setup):
   - Open VS Code settings
   - Set `yamlDashboard.kibana.url` to your Kibana instance (e.g., `https://my-kibana.example.com`)

2. **Set Kibana credentials** (one-time setup):
   - Open Command Palette (Ctrl+Shift+P)
   - Run **"YAML Dashboard: Set Kibana API Key"** (recommended)
     - Or use **"Set Kibana Username"** and **"Set Kibana Password"** for basic auth
   - Credentials are stored securely using your OS keychain (macOS Keychain, Windows Credential Manager, Linux Secret Service)

3. **Upload and open dashboard**:
   - Open a YAML dashboard file
   - Run **"YAML Dashboard: Open in Kibana"** from the Command Palette or right-click menu
   - The dashboard is compiled, uploaded, and opened in your browser automatically

**Security Note**: Credentials are encrypted and stored in your operating system's secure credential storage. They are never stored in plaintext or synced to the cloud.

### Option 2: Manual Import

If you prefer manual import or don't have direct Kibana access:

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

### Kibana upload issues

**Problem**: "Failed to open in Kibana" or authentication errors

**Solutions**:

- Verify Kibana URL is correct in settings (including http/https protocol)
- Check credentials are set using the credential commands
- For self-signed certificates, set `yamlDashboard.kibana.sslVerify` to `false` (not recommended for production)
- Verify Kibana is accessible from your machine (try opening the URL in a browser)
- For API key issues, ensure the key has permissions to create saved objects
- Check the Output panel (View → Output → YAML Dashboard Compiler) for detailed error messages

**Problem**: Credentials not persisting

**Solutions**:

- Credentials are stored in OS keychain - ensure your keychain is unlocked
- On Linux, ensure `libsecret` is installed for credential storage
- Try clearing and re-setting credentials using the "Clear Kibana Credentials" command

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
