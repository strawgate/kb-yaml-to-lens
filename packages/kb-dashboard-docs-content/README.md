# kb-dashboard-docs-content

Bundled LLM documentation content for the kb-yaml-to-lens dashboard compiler.

This package contains:

- `llms-full.txt`: Complete documentation for LLM context
- `guides/`: Workflow guides for dashboard creation

## Usage

```python
from kb_dashboard_docs_content import get_full_docs, list_guides, get_guide

# Get the complete documentation
docs = get_full_docs()
print(docs)

# List available guides
guides = list_guides()
print(guides)  # ['esql-language-reference', 'otel-dashboard-guide', ...]

# Get a specific guide
guide_content = get_guide('otel-dashboard-guide')
print(guide_content)
```

## CLI Usage

When used with the kb-dashboard-cli:

```bash
# Output full documentation (for piping to LLMs)
kb-dashboard docs

# List available guides
kb-dashboard docs list-guides

# Get a specific guide
kb-dashboard docs guide otel-dashboard-guide
```
