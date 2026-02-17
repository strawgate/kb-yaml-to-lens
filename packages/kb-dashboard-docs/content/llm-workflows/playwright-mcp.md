# Playwright MCP for Dashboard Development

This guide covers using Microsoft's `@playwright/mcp` server for AI-assisted dashboard development, enabling browser-based verification and interactive exploration of Kibana dashboards.

## Overview

The [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) enables AI assistants to interact with external tools and services. For dashboard development, Playwright MCP provides browser automation capabilities that complement the kb-dashboard CLI tools.

**Recommended Solution:** Microsoft's official [`@playwright/mcp`](https://github.com/microsoft/playwright-mcp) server.

### Why @playwright/mcp?

| Feature | Benefit |
| ------- | ------- |
| **Official support** | Maintained by Microsoft/Playwright team |
| **Accessibility-tree interaction** | More reliable than pixel-based automation |
| **Structured element references** | Consistent element identification across sessions |
| **Multi-tab management** | Navigate complex Kibana workflows |
| **Screenshot capture** | Visual verification of dashboard rendering |

## Installation

### Using npx (Recommended)

No installation required - run directly:

```bash
npx @playwright/mcp@latest
```

### Global Installation

```bash
npm install -g @playwright/mcp
```

### Claude Desktop Configuration

Add to your Claude Desktop `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

## Key Capabilities

### Navigation

Navigate to Kibana dashboards and apps:

- `browser_navigate` - Navigate to a URL
- `browser_back` / `browser_forward` - Browser history navigation
- `browser_wait` - Wait for page elements or network idle

### Element Interaction

Interact with dashboard elements using accessibility snapshots:

- `browser_snapshot` - Get accessibility tree snapshot
- `browser_click` - Click elements by reference
- `browser_type` - Type into form fields
- `browser_select_option` - Select dropdown options

### Visual Verification

Capture dashboard state for review:

- `browser_screenshot` - Capture full page or viewport screenshots
- `browser_pdf_save` - Save page as PDF

### Tab Management

Handle complex workflows across multiple views:

- `browser_tab_list` - List open tabs
- `browser_tab_new` - Open new tab
- `browser_tab_select` - Switch between tabs
- `browser_tab_close` - Close tabs

---

## Kibana Configuration

### Basic Configuration

Configure the MCP server to start at your Kibana instance:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--url", "http://localhost:5601"
      ]
    }
  }
}
```

### Kibana Spaces

Kibana spaces use URL paths like `/s/{space-id}/app/dashboards`. Configure the starting URL to include your target space:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--url", "http://localhost:5601/s/my-space/app/dashboards"
      ]
    }
  }
}
```

### Authentication

#### Interactive Login

For development environments, allow interactive login through the browser:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--url", "http://localhost:5601/login"
      ]
    }
  }
}
```

The AI agent can then navigate to the login page and authenticate using `browser_type` and `browser_click` tools.

#### Stored Browser Context

For repeated sessions, use a persistent browser context with stored credentials:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--url", "http://localhost:5601",
        "--user-data-dir", "/path/to/browser-profile"
      ]
    }
  }
}
```

### SSL/TLS Considerations

For development environments with self-signed certificates:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--url", "https://localhost:5601",
        "--ignore-https-errors"
      ]
    }
  }
}
```

!!! warning "Production Use"
    Never use `--ignore-https-errors` in production environments. Configure proper SSL certificates instead.

---

## Environment Variables

### Standard kb-dashboard Variables

The kb-dashboard CLI uses these environment variables for Kibana access:

| Variable | Purpose |
| -------- | ------- |
| `KIBANA_URL` | Base URL for Kibana instance |
| `KIBANA_API_KEY` | API key for authentication |
| `KIBANA_USERNAME` | Username for basic auth |
| `KIBANA_PASSWORD` | Password for basic auth |

### Using Variables in MCP Configuration

Reference environment variables in your MCP configuration:

**Unix/macOS:**

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--url", "${KIBANA_URL}"
      ]
    }
  }
}
```

**Windows:**

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--url", "%KIBANA_URL%"
      ]
    }
  }
}
```

### Security Best Practices

!!! danger "Credential Security"
    - Never hardcode credentials in configuration files
    - Use environment variables for sensitive values
    - Avoid logging or displaying credentials in AI conversations
    - Rotate API keys regularly

**Recommended workflow:**

1. Set environment variables in your shell profile or `.env` file
2. Reference variables in MCP configuration
3. Provide Kibana URL as context to AI agent before browser automation
4. Use API keys instead of username/password when possible

---

## Additional Resources

- [Playwright MCP Repository](https://github.com/microsoft/playwright-mcp) - Official documentation and source
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP specification and guides
- [AI Dashboard Iteration Workflows](ai-dashboard-workflows.md) - Using Playwright MCP for dashboard development
- [CLI Reference](../CLI.md) - kb-dashboard CLI commands
