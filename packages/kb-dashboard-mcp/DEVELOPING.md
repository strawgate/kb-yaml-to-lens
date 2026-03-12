# Developing kb-dashboard-mcp

This guide covers development workflows for the MCP server package.

## Prerequisites

- **Python 3.12+**
- **[uv](https://github.com/astral-sh/uv)** (Python package manager)
- **make** (build automation)

## Quick Start

```bash
# From repository root
cd packages/kb-dashboard-mcp

# Install dependencies
make install

# Run all checks
make ci
```

## Development Commands

| Command | Purpose |
| ------- | ------- |
| `make install` | Install dependencies |
| `make ci` | Run all CI checks (lint + typecheck + test) |
| `make fix` | Auto-fix linting issues |
| `make test` | Run unit tests |
| `make typecheck` | Run type checking |
| `make lint-check` | Check linting without fixing |
| `make clean` | Clean cache and temporary files |

## Running the MCP Server Locally

```bash
# Run with stdio transport (default)
uv run kb-mcp --es-url https://localhost:9200 --es-api-key your-key

# Run with SSE transport
uv run kb-mcp --es-url https://localhost:9200 --es-api-key your-key --transport sse
```

## Testing with MCP Inspector

Use the [MCP Inspector](https://github.com/modelcontextprotocol/inspector) to test the server:

```bash
npx @modelcontextprotocol/inspector kb-mcp --es-url https://localhost:9200 --es-api-key your-key
```

## Project Structure

```text
packages/kb-dashboard-mcp/
├── src/kb_dashboard_mcp/
│   ├── __init__.py           # Package exports
│   ├── cli.py                # CLI entry point
│   ├── server.py             # MCP server setup
│   ├── models.py             # Pydantic models
│   └── tools/                # MCP tool implementations
│       ├── __init__.py
│       ├── data_streams.py   # Data stream tools
│       ├── esql.py           # ES|QL query tool
│       └── patterns.py       # Grok/dissect tools
├── tests/                    # Test files
├── Makefile                  # Build automation
└── pyproject.toml           # Package configuration
```

## Code Style

See [CODE_STYLE.md](CODE_STYLE.md) for code conventions.

## Agent Behavior & Integration

See [AGENTS.md](AGENTS.md) for agent responsibilities, capabilities, and MCP integration points when extending this package.

## Adding New Tools

1. Create a new file in `src/kb_dashboard_mcp/tools/`
2. Define Pydantic models for inputs/outputs in `models.py`
3. Implement the tool function following async patterns
4. Register the tool in `server.py`
5. Add tests in `tests/`
