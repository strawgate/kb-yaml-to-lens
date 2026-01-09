# Kibana Dashboard Compiler - VS Code Extension

A VS Code extension that provides live compilation and preview for Kibana YAML dashboards. This extension makes it fast and easy to edit and work with YAML dashboard files by automatically compiling them on save and providing a live preview.

![YAML to Kibana-768](https://github.com/user-attachments/assets/89ea7a4b-5a72-4fb2-8a2b-211704501a07)

## Features

- **Auto-complete and Validation**: Schema-based auto-complete, validation, and hover documentation for YAML dashboard files (powered by Red Hat YAML extension)
- **Code Snippets**: Pre-built snippets for all panel types, controls, and layouts - just start typing a prefix like `panel-lens-metric` and press Tab
- **Auto-compile on Save**: Automatically compiles your YAML dashboard files whenever you save them
- **Live Preview**: View your compiled dashboard in a side-by-side preview panel with live reload functionality
- **Visual Grid Layout Editor**: Drag and drop panels to rearrange them, resize panels interactively, with automatic YAML updates
- **Export to NDJSON**: Copy or download compiled dashboards as NDJSON for direct import into Kibana
- **Open in Kibana**: Upload dashboards directly to Kibana and open them in your browser with one command
- **Secure Credential Storage**: Kibana credentials stored encrypted using VS Code's SecretStorage API (OS keychain)

## Requirements

### For End Users

- VS Code 1.85.0 or higher
- Red Hat YAML extension (automatically installed)
- **No Python required** - The extension includes a bundled binary for the LSP server

### For Developers

- Python 3.12+ with `dashboard_compiler` package installed (only needed for local development)
- VS Code 1.85.0 or higher

## Installation

### From OpenVSX Registry (Cursor and VS Code Forks)

1. Open your IDE's Extensions view (Ctrl+Shift+X)
2. Search for "Kibana Dashboard Compiler"
3. Click Install

Note: Cursor and other VS Code forks use the [OpenVSX Registry](https://open-vsx.org/) instead of the VS Code Marketplace.

### From VS Code Marketplace (Coming Soon)

Install directly from the VS Code Extensions marketplace.

### From VSIX (Manual)

1. Download the platform-specific `.vsix` file from releases
2. In VS Code/Cursor: Extensions view (Ctrl+Shift+X) → "..." menu → "Install from VSIX..."

Or use the Makefile for automated installation:

```bash
# From repository root - install to VS Code
make install-extension-vscode

# From repository root - install to Cursor
make install-extension-cursor
```

**Prerequisites for Makefile installation:**
- Node.js and npm (required to package the extension and read package.json metadata)
- The `code` (VS Code) or `cursor` (Cursor) CLI must be installed and available in your PATH
- The packaged VSIX file must exist (automatically built by the Makefile targets)
- The extension package name follows the format: `<extension-name>-<version>.vsix`
  - Derived from `vscode-extension/package.json` `name` and `version` fields
  - Example: `kb-dashboard-compiler-0.1.0.vsix` (current version)

### For Development

See [BUILDING.md](./BUILDING.md) for build and development instructions.

## Setup

### Python Environment (Development Only)

If developing the extension, install the `dashboard_compiler` package:

```bash
# From repository root
pip install -e .
# or: uv sync
```

### Extension Configuration

Configure in VS Code settings (File → Preferences → Settings, search for "Kibana Dashboard"):

- **`yamlDashboard.pythonPath`**: Python interpreter path (optional - only needed for development; bundled binary is used by default)
- **`yamlDashboard.compileOnSave`**: Auto-compile on save (default: `true`)
- **`yamlDashboard.kibana.url`**: Kibana URL for uploads (default: `http://localhost:5601`)
- **`yamlDashboard.kibana.sslVerify`**: Verify SSL certificates (default: `true`)
- **`yamlDashboard.kibana.browserType`**: Browser for opening dashboards - `external` or `simple` (default: `external`)
- **`yamlDashboard.kibana.uploadOnSave`**: Auto-upload on save (default: `false`)

## Usage

### Commands

Open Command Palette (Ctrl+Shift+P) and search for:

- **YAML Dashboard: Compile Dashboard** - Manually compile current YAML file
- **YAML Dashboard: Preview Dashboard** - Open preview panel
- **YAML Dashboard: Edit Dashboard Layout** - Visual grid layout editor
- **YAML Dashboard: Export Dashboard to NDJSON** - Copy NDJSON to clipboard
- **YAML Dashboard: Open in Kibana** - Upload and open in browser
- **YAML Dashboard: Set Kibana Username** - Store username securely
- **YAML Dashboard: Set Kibana Password** - Store password securely
- **YAML Dashboard: Set Kibana API Key** - Store API key securely (recommended)
- **YAML Dashboard: Clear Kibana Credentials** - Remove stored credentials

### Using Code Snippets

Speed up dashboard creation with built-in snippets:

1. Start typing a prefix (e.g., `panel-lens-metric`)
2. Press Tab to insert (or Ctrl+Space for completions)
3. Tab through placeholders to fill in values

**Available Prefixes:**

| Prefix | Description |
| ------ | ----------- |
| `dashboard` | Complete dashboard structure |
| `panel-markdown` | Markdown panel |
| `panel-lens-metric` | Lens metric visualization |
| `panel-lens-pie` | Lens pie chart |
| `panel-lens-line` | Lens line chart |
| `panel-lens-bar` | Lens bar chart |
| `panel-lens-datatable` | Lens data table |
| `panel-esql-metric` | ES\|QL metric panel |
| `grid-full` | Full width layout (48 units) |
| `grid-half` | Half width layout (24 units) |
| `control-options` | Options list control |

...and many more! See full list in the extension's snippet definitions.

**Cursor Users**: Press Ctrl+Space (Cmd+Space on Mac) to trigger completions.

### Workflow

1. Open a YAML dashboard file
2. Use snippets to quickly insert panels
3. Save (Ctrl+S) - auto-compiles
4. Run "Preview Dashboard" to see compiled output
5. Run "Edit Dashboard Layout" to visually arrange panels
6. Use "Copy NDJSON" button to export for Kibana

## Uploading to Kibana

### Quick Setup

1. **Set Kibana URL** in settings: `yamlDashboard.kibana.url`
2. **Set credentials**: Run "Set Kibana API Key" command (recommended) or use username/password
3. **Upload**: Run "Open in Kibana" command

Credentials are stored securely in your OS keychain (macOS Keychain, Windows Credential Manager, Linux Secret Service).

### Manual Import Alternative

1. Use "Copy NDJSON" button in preview
2. In Kibana: Stack Management → Saved Objects → Import
3. Paste/upload the NDJSON

## Troubleshooting

### Extension Issues

#### LSP server not starting

Most users won't encounter this issue since the bundled binary works automatically. If you see issues:

- **End users**: Try reinstalling the extension or downloading a fresh VSIX for your platform
- **Developers**: Verify `dashboard_compiler` is installed: `python -c "import dashboard_compiler"`
- Check the Output panel (View → Output → "Kibana Dashboard Compiler") for detailed logs
- The extension will automatically fall back to Python if the bundled binary isn't available

#### Compilation errors

- Check YAML syntax using the built-in validation (Red Hat YAML extension)
- Review error message in preview panel or Output panel
- Ensure your YAML follows the dashboard schema

#### Preview not updating

- Ensure `yamlDashboard.compileOnSave` is enabled in settings
- Try running the "Preview Dashboard" command manually (Ctrl+Shift+P)
- Close and reopen the preview panel

### Kibana Upload Issues

#### Authentication errors

- Verify Kibana URL is correct (include http/https)
- Check credentials are set using credential commands
- For self-signed certs, set `yamlDashboard.kibana.sslVerify` to `false`
- Ensure API key has permission to create saved objects
- Check Output panel for detailed errors

#### Credentials not persisting

- Ensure OS keychain is unlocked
- On Linux, install `libsecret` for credential storage
- Try clearing and re-setting credentials

## Development

For build instructions, cross-platform packaging, and publishing details, see [BUILDING.md](./BUILDING.md).

For testing guidelines, see [TESTING.md](./TESTING.md).

## License

MIT - See [LICENSE](../LICENSE) for details.

## Related Links

- [Main Repository](https://github.com/strawgate/kb-yaml-to-lens)
- [Kibana Lens Documentation](https://github.com/elastic/kibana/tree/main/x-pack/platform/plugins/shared/lens)
- [VS Code Extension API](https://code.visualstudio.com/api)
