# VS Code Extension

A Visual Studio Code extension that provides live compilation, preview, and visual editing for Kibana YAML dashboards. This extension makes it fast and easy to work with YAML dashboard files by automatically compiling them on save and providing a live preview with interactive layout editing.

- **Auto-complete and Validation** – Schema-based auto-complete, validation, and hover documentation for YAML dashboard files (powered by Red Hat YAML extension)
- **Code Snippets** – Pre-built snippets for all panel types, controls, and layouts - just start typing a prefix like `panel-lens-metric` and press Tab
- **Auto-compile on Save** – Automatically compiles your YAML dashboard files whenever you save them
- **Live Preview Panel** – View your compiled dashboard in a side-by-side preview panel with live reload
- **Visual Grid Layout Editor** – Drag and drop panels to rearrange them, resize panels interactively, with automatic YAML updates
- **Export to NDJSON** – Copy or download compiled dashboards as NDJSON for direct import into Kibana
- **Error Reporting** – Clear error messages when compilation fails
- **Context Menu Integration** – Right-click commands in YAML files for quick access

## Why Use the Extension?

The VS Code extension is the **easiest way to get started** with the Kibana Dashboard Compiler:

### No Python Installation Required

- **Bundled LSP binary** - Extension includes pre-built server binary for all platforms
- **Zero configuration** - Works immediately after installation
- **No dependency management** - No `pip`, `uv`, or virtual environments needed

### Instant Feedback

- **Live preview** - See your dashboard as you type
- **Auto-compile on save** - Background compilation with error reporting
- **Visual validation** - Schema-based validation catches errors before upload

### Productivity Features

- **Code snippets** - 40+ pre-built snippets for panels, controls, layouts
- **Visual grid editor** - Drag-and-drop panel positioning
- **Schema auto-complete** - IntelliSense for all YAML properties
- **One-click upload** - Direct integration with Kibana

**When to use CLI instead:** CI/CD pipelines, batch processing, scripting, environments without VS Code

---

## Installation

### Prerequisites

#### For End Users (Installing from Registry/VSIX)

- VS Code 1.85.0 or higher
- Red Hat YAML extension (automatically installed)
- **No Python required** - Bundled binary included

#### For Extension Developers Only

- Python 3.12+ with `dashboard_compiler` package
- Node.js 18+ for building the extension
- VS Code 1.85.0 or higher

### Installing the Extension

#### Option 1: Install from OpenVSX Registry

Works with Cursor, VSCodium, and other VS Code forks:

1. Open Extensions view (Ctrl+Shift+X)
2. Search for "Kibana Dashboard Compiler"
3. Click Install

#### Option 2: Manual Installation (VSIX)

For restricted environments or offline installation:

1. Download platform-specific `.vsix` from [releases page](https://github.com/strawgate/kb-yaml-to-lens/releases)
2. In VS Code: Extensions view (Ctrl+Shift+X) → "..." menu → "Install from VSIX..."
3. Select the downloaded `.vsix` file

**That's it!** The extension includes everything needed - no additional setup required.

### Verify Installation

After installation, confirm the extension is working:

1. **Check extension is active:**
   - Open Command Palette (Ctrl+Shift+P / Cmd+Shift+P on Mac)
   - Type "YAML Dashboard" - you should see multiple commands listed

2. **Test snippet functionality:**
   - Create a new file: `test-dashboard.yaml`
   - Type `dashboard` and press Tab
   - A complete dashboard structure should be inserted

3. **Troubleshooting:**
   - If commands don't appear: Restart VS Code
   - If snippets don't work: Ensure file extension is `.yaml`
   - Check Output panel: View → Output → "Kibana Dashboard Compiler"

### For Extension Developers

Only needed if you're developing the extension itself:

1. Build the extension using make (from repository root):

   ```bash
   make vscode install
   make vscode compile
   make vscode package
   ```

   Or manually within the packages/vscode-extension directory:

   ```bash
   cd packages/vscode-extension
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

## Setup

### Extension Configuration

Configure in VS Code settings (File → Preferences → Settings, search for "Kibana Dashboard"):

**`yamlDashboard.compileOnSave`** - Enable/disable automatic compilation on save (default: `true`)

**`yamlDashboard.kibana.url`** - Kibana URL for uploads (default: `http://localhost:5601`)

**`yamlDashboard.kibana.sslVerify`** - Verify SSL certificates (default: `true`)

**`yamlDashboard.kibana.browserType`** - Browser for opening dashboards - `external` or `simple` (default: `external`)

**`yamlDashboard.kibana.openOnSave`** - Auto-upload and open in Kibana on save (default: `false`)

**`yamlDashboard.pythonPath`** - Python interpreter path (optional - only needed for development; bundled binary is used by default)

## Usage

### Commands

The extension provides the following commands (accessible via Command Palette - Ctrl+Shift+P):

- **YAML Dashboard: Compile Dashboard** – Manually compile the current YAML file
- **YAML Dashboard: Preview Dashboard** – Open preview panel for the current YAML file
- **YAML Dashboard: Edit Dashboard Layout** – Open visual grid layout editor for drag-and-drop panel positioning
- **YAML Dashboard: Export Dashboard to NDJSON** – Copy compiled NDJSON to clipboard
- **YAML Dashboard: Open in Kibana** – Upload compiled dashboard to Kibana and open in browser
- **YAML Dashboard: Set Kibana API Key** – Store API credentials for Kibana uploads

## Complete Workflow Walkthrough

### First-Time Setup (5 minutes)

1. **Install the extension** (see Installation section above)
2. **Configure Kibana connection** (optional - only needed for uploads):
   - Open Settings (File → Preferences → Settings)
   - Search: "Kibana Dashboard"
   - Set `yamlDashboard.kibana.url` (e.g., `http://localhost:5601`)
   - Run command: **"YAML Dashboard: Set Kibana API Key"** (recommended) or set username/password

### Daily Development Workflow

1. **Create or open** a YAML dashboard file
2. **Use snippets** for rapid scaffolding:
   - Type `dashboard` + Tab for complete dashboard structure
   - Type `panel-lens-metric` + Tab for metric panel
   - Type `grid-half` + Tab for half-width grid layout
3. **Save (Ctrl+S)** - automatic compilation runs in background
4. **Preview** your work:
   - Command: **"YAML Dashboard: Preview Dashboard"**
   - Panel opens side-by-side with live reload
5. **Visual layout adjustment** (optional):
   - Command: **"YAML Dashboard: Edit Dashboard Layout"**
   - Drag panels to reposition, resize by dragging corners
   - Changes auto-save back to YAML
6. **Upload to Kibana**:
   - Command: **"YAML Dashboard: Open in Kibana"**
   - Dashboard uploads and opens in browser automatically

### Quick Commands Reference

Access via Command Palette (Ctrl+Shift+P):

| Command | Purpose | When to Use |
| ------- | ------- | ----------- |
| **Compile Dashboard** | Manual compilation | After disabling auto-compile |
| **Preview Dashboard** | Open live preview | First time or after closing preview |
| **Edit Dashboard Layout** | Visual grid editor | Positioning panels visually |
| **Export to NDJSON** | Copy to clipboard | Manual Kibana import |
| **Open in Kibana** | Upload + open browser | Deploy to Kibana |
| **Set Kibana API Key** | Store credentials | One-time Kibana setup (recommended) |

### Keyboard Shortcuts

You can add custom keyboard shortcuts in VS Code (File → Preferences → Keyboard Shortcuts):

```json
{
  "key": "ctrl+shift+d",
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

## Related Links

- [Main Repository](https://github.com/strawgate/kb-yaml-to-lens)
- [Kibana Lens Documentation](https://github.com/elastic/kibana/tree/main/x-pack/platform/plugins/shared/lens)
- [VS Code Extension API](https://code.visualstudio.com/api)
