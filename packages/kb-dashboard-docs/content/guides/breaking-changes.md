# Breaking Changes

This guide tracks user-facing breaking changes and migrations between releases.

Use the CLI to access this guide from a local install:

- `kb-dashboard docs guide breaking-changes`

## 0.2.7 -> main

At release time, update this header to `0.2.7 -> 0.3.0`.

### Migration Checklist

- Datatable: remove `columns` and `metric_columns`.
- Datatable: move per-metric and per-dimension display settings under `appearance`.
- Datatable: replace metric `color_mode` with `appearance.color.apply_to`.
- Datatable: replace metric top-level `color` with `appearance.color`.
- Metric charts (Lens + ES|QL): rename `color_mode` to `apply_to`.
- Datatable validation: ensure each datatable has at least one metric or one dimension.
- Range color mappings: rename `stops` to `thresholds` and nested `stop` to `up_to`.

### Range Color Mapping Threshold Rename

Range-based color mappings now use threshold-oriented YAML keys:

```yaml
color:
  range_type: percent
  thresholds:
    - up_to: 50
      color: '#00BF6F'
    - up_to: 80
      color: '#FFA500'
    - up_to: 100
      color: '#BD271E'
```

Old YAML using `stops` / `stop` must be updated.
