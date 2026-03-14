# kb-dashboard-docs

Documentation and bundled LLM content for kb-yaml-to-lens dashboard compiler.

## Overview

This package provides:

1. **MkDocs documentation site** - User-facing documentation for the kb-yaml-to-lens project
2. **Bundled LLM content** - Pre-processed documentation for LLM context windows

## Installation

```bash
pip install kb-dashboard-docs
```

Or for the full CLI experience:

```bash
pip install kb-dashboard-cli
```

## API Usage

```python
from kb_dashboard_docs import get_full_docs, list_guides, get_guide

# Get complete documentation for LLM context
full_docs = get_full_docs()

# List available workflow guides
guides = list_guides()
# ['dashboard-decompiling-guide', 'dashboard-style-guide', 'esql-language-reference', 'otel-dashboard-guide']

# Get a specific guide
otel_guide = get_guide('otel-dashboard-guide')
```

## CLI Usage

When using `kb-dashboard-cli`:

```bash
# Output full documentation (for piping to LLMs)
kb-dashboard docs llms-full

# Copy to clipboard (macOS)
kb-dashboard docs llms-full | pbcopy

# List available guides
kb-dashboard docs list-guides

# Get a specific guide
kb-dashboard docs guide otel-dashboard-guide
```

## Available Guides

- **otel-dashboard-guide** - Creating dashboards from OpenTelemetry Collector data
- **esql-language-reference** - ES|QL query language reference for dashboards
- **dashboard-decompiling-guide** - Converting Kibana JSON dashboards to YAML
- **dashboard-style-guide** - Layout, sizing, and design patterns
- **color-assignments** - Advanced chart color assignment strategies
- **esql-views** - Advanced ES|QL view patterns for chart panels
- **legend-configuration** - Advanced legend configuration for supported charts

## Development

See [DEVELOPING.md](../../DEVELOPING.md) for development setup.

## License

MIT
