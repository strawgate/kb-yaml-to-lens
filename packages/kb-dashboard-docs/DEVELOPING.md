# Developing Documentation

Documentation is built with **MkDocs** using the Material theme.

## Structure

```text
packages/kb-dashboard-docs/
├── content/
│   ├── index.md                 # Home page
│   ├── api/                     # API reference (auto-generated from Python)
│   ├── panels/                  # Panel type docs
│   └── examples/                # Example YAML files
└── hooks/                       # MkDocs build hooks (Python)
```

Navigation is defined in `mkdocs.yml`.

## Commands

Run from the repository root using the passthrough pattern:

```bash
# Serve locally
make docs serve

# Build
make docs build

# Full check (lint + link verification)
make docs ci
```

**From within component directory:** You can also run `make <target>` directly from `packages/kb-dashboard-docs/`, or use `mkdocs` commands directly.

## Adding Pages

1. Create markdown file in appropriate folder
2. Add to `nav:` in `mkdocs.yml`
3. Use relative links: `[text](../path/file.md)`

## Examples

All YAML examples should compile:

```bash
kb-dashboard compile --input-file packages/kb-dashboard-docs/content/examples/your-file.yaml
```

See existing files in `content/examples/` for patterns.

## Link Verification

CI verifies all internal and external links. Run `make docs ci` before committing.

## Build Hooks

Python hooks in `hooks/` run during build (e.g., generating llms.txt). Test with `make docs build` from the repository root, or `mkdocs build` from within `packages/kb-dashboard-docs/`.
