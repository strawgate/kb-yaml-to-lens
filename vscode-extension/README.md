# Kibana Dashboard Compiler

Build Kibana dashboards using simple YAML syntax with live preview and visual editing.

**No Python required** — bundled binary works out of the box.

![YAML to Kibana-768](https://github.com/user-attachments/assets/89ea7a4b-5a72-4fb2-8a2b-211704501a07)

## Features

- **IntelliSense auto-complete** — Press `Ctrl+Space` (⌃Space on macOS) anywhere in your YAML to see available options, with live validation and hover documentation
- **40+ code snippets** — Quickly insert panels, controls, layouts, and common patterns. Type a prefix like `panel-`, `control-`, or `layout-` and press `Tab` to expand
- **Live preview panel** — See your dashboard update in real-time as you edit, with auto-compile on save
- **Visual grid editor** — Drag-and-drop panel positioning for intuitive layout design
- **One-click Kibana upload** — Upload dashboards directly to Kibana with secure credential storage

## Installation

1. Open Extensions (`Ctrl/Cmd+Shift+X`)
2. Search "Kibana Dashboard Compiler"
3. Click Install

## Quick Start

1. Create a file: `my-dashboard.yaml`
2. Type `dashboard` + Tab to insert a starter template
3. Press `Ctrl+Space` (⌃Space on macOS) to explore available options at any position
4. Save (`Ctrl/Cmd+S`) to compile and see your changes
5. Run command: **YAML Dashboard: Preview Dashboard**

## Commands

Open Command Palette (`Ctrl/Cmd+Shift+P`):

| Command | Description |
| ------- | ----------- |
| Preview Dashboard | Open live preview panel |
| Edit Dashboard Layout | Visual grid editor |
| Open in Kibana | Upload and open in browser |
| Export to NDJSON | Copy compiled output |

## Documentation

For complete documentation including configuration, troubleshooting, and advanced usage:

- [Full Extension Guide](https://github.com/strawgate/kb-yaml-to-lens/blob/main/packages/kb-dashboard-docs/content/vscode-extension.md)
- [Dashboard Syntax Reference](https://github.com/strawgate/kb-yaml-to-lens/blob/main/packages/kb-dashboard-docs/content/index.md)
- [Main Repository](https://github.com/strawgate/kb-yaml-to-lens)

## License

MIT
