# VS Code Extension

A Visual Studio Code extension that provides live compilation, preview, and visual editing for Kibana YAML dashboards. This extension makes it fast and easy to work with YAML dashboard files by automatically compiling them on save and providing a live preview with interactive layout editing.

## Features

- **Auto-compile on Save** – Automatically compiles your YAML dashboard files whenever you save them
- **Live Preview Panel** – View your compiled dashboard in a side-by-side preview panel with live reload
- **Visual Grid Layout Editor** – Drag and drop panels to rearrange them, resize panels interactively, with automatic YAML updates
- **Export to NDJSON** – Copy or download compiled dashboards as NDJSON for direct import into Kibana
- **Error Reporting** – Clear error messages when compilation fails
- **Context Menu Integration** – Right-click commands in YAML files for quick access

## Installation

### Prerequisites

- **Python 3.12 or higher** – The extension requires Python with the dashboard compiler package
- **dashboard_compiler package** – Must be installed and available in your Python environment
- **VS Code 1.85.0 or higher**

### Building and Installing

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

If you're contributing to the extension or want to run the latest development version:

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

The extension requires the `dashboard_compiler` package to be installed in your Python environment.

From the repository root:

```bash
# Using pip
pip install -e .

# Or using uv
uv sync
```

### Extension Configuration

Configure the extension in VS Code settings (File → Preferences → Settings):

**`yamlDashboard.pythonPath`**

Path to your Python interpreter (default: `python`)

Examples:

- Linux/macOS: `/usr/bin/python3`
- PyEnv: `~/.pyenv/versions/3.11.0/bin/python`
- Windows: `C:\\Python311\\python.exe`
- Virtual environment: `/path/to/venv/bin/python`
- Conda environment: `/path/to/conda/envs/yourenv/bin/python`

**`yamlDashboard.compileOnSave`**

Enable/disable automatic compilation on save (default: `true`)

## Usage

### Commands

The extension provides the following commands (accessible via Command Palette - Ctrl+Shift+P):

- **YAML Dashboard: Compile Dashboard** – Manually compile the current YAML file
- **YAML Dashboard: Preview Dashboard** – Open preview panel for the current YAML file
- **YAML Dashboard: Edit Dashboard Layout** – Open visual grid layout editor for drag-and-drop panel positioning
- **YAML Dashboard: Export Dashboard to NDJSON** – Copy compiled NDJSON to clipboard

### Workflow

1. Open a YAML dashboard file (e.g., `my-dashboard.yaml`)
2. The extension activates automatically for YAML files
3. Save the file (Ctrl+S) - it will automatically compile if `compileOnSave` is enabled
4. Run **YAML Dashboard: Preview Dashboard** to see the compiled output
5. Run **YAML Dashboard: Edit Dashboard Layout** to visually rearrange panels:
   - Drag panels to move them on the 48-column Kibana grid
   - Drag the bottom-right corner of panels to resize them
   - Changes are saved automatically to the YAML file
   - Use "Show Grid Lines" and "Snap to Grid" options for easier alignment
6. The preview updates automatically when you save changes
7. Use the **Copy NDJSON** button in the preview to export for Kibana

### Keyboard Shortcuts

You can add custom keyboard shortcuts in VS Code (File → Preferences → Keyboard Shortcuts):

```json
{
  "key": "ctrl+shift+p",
  "command": "yamlDashboard.preview",
  "when": "resourceLangId == yaml"
}
```

### Preview Panel

The preview panel shows:

- **Dashboard Title** – The title from your YAML configuration
- **File Path** – The current file being previewed
- **Export Buttons**:
  - Copy NDJSON to clipboard
  - Download NDJSON file
- **Dashboard Information** – Type, ID, version
- **Compiled Output** – Pretty-printed JSON view of the compiled dashboard

### Grid Layout Editor

The visual grid layout editor provides an interactive way to arrange your dashboard panels:

- **Drag and Drop** – Click and drag panels to reposition them
- **Resize Panels** – Drag the bottom-right corner to resize
- **Grid System** – Works with Kibana's 48-column grid layout
- **Show Grid Lines** – Toggle grid visibility for easier alignment
- **Snap to Grid** – Enable snapping for precise positioning
- **Auto-save** – Changes are automatically written back to your YAML file

## Importing to Kibana

Once you've compiled your dashboard, you can import it into Kibana:

1. Use the **Copy NDJSON** button in the preview panel
2. In Kibana, navigate to: **Stack Management → Saved Objects → Import**
3. Paste or upload the NDJSON file
4. Your dashboard is now available in Kibana!

## Troubleshooting

### Python server not starting

**Problem**: Extension shows "Python server not running" error

**Solutions**:

- Verify `dashboard_compiler` is installed:

  ```bash
  python -c "import dashboard_compiler"
  ```

- Check the Python path in extension settings
- View the Output panel (View → Output) and select "YAML Dashboard Compiler" to see logs

### Compilation errors

**Problem**: "Compilation failed" messages

**Solutions**:

- Check your YAML syntax
- Verify your dashboard structure matches the expected schema
- Review the error message in the preview panel for details
- Test compilation manually:

  ```bash
  python -c "from dashboard_compiler.dashboard_compiler import load; load('your_file.yaml')"
  ```

### Preview not updating

**Problem**: Preview doesn't refresh after saving

**Solutions**:

- Check that `yamlDashboard.compileOnSave` is enabled in settings
- Try manually running **YAML Dashboard: Preview Dashboard**
- Close and reopen the preview panel

### Python path issues

**Problem**: Extension can't find Python or packages

**Solutions**:

- Use absolute path in settings:

  ```json
  {
    "yamlDashboard.pythonPath": "/full/path/to/python"
  }
  ```

- For virtual environments, use the venv Python:

  ```json
  {
    "yamlDashboard.pythonPath": "/path/to/venv/bin/python"
  }
  ```

- For conda environments:

  ```json
  {
    "yamlDashboard.pythonPath": "/path/to/conda/envs/yourenv/bin/python"
  }
  ```

## Related Links

- [Main Repository](https://github.com/strawgate/kb-yaml-to-lens)
- [Kibana Lens Documentation](https://github.com/elastic/kibana/tree/main/x-pack/platform/plugins/shared/lens)
- [VS Code Extension API](https://code.visualstudio.com/api)
