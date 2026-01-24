# Code Style: Documentation

## Unusual Requirements

### Link Verification

All links are verified in CI. Broken links fail the build. Test locally: `make docs ci`

### Compilable Examples

YAML examples must compile successfully:

```bash
kb-dashboard compile --input-file packages/kb-dashboard-docs/content/examples/your-file.yaml
```

If example needs specific data, add a comment in the YAML.

### API Documentation Tables

Use this format for configuration options:

```markdown
| Option | Type | Required | Default | Description |
| ------ | ---- | -------- | ------- | ----------- |
| `title` | string | Yes | - | Panel title |
| `color` | string | No | `"#000000"` | Series color |
```

Use `code formatting` for option names, types, and values.

## Standard Markdown

- ATX headers (`#`) with space after
- Fenced code blocks with language tags
- Use `-` for lists (not `*` or `+`)
- Relative links from current file (absolute links are allowed for resources not in this repository)

## Examples

See existing documentation files for patterns:

- API docs: `api/panels.md`, `api/controls.md`
- Panel docs: `panels/xy.md`, `panels/metric.md`
- Examples: `examples/system_otel/`, `examples/docker_otel/`

## Documentation

Files in this component have strict markdown linting and undergo a link verification step during CI which will fail if any links in this component are broken.
