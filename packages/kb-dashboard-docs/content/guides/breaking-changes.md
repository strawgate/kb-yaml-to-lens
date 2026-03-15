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
- Metric charts (Lens + ES|QL): move top-level `color_mode` to `appearance.color.apply_to`.
- Metric charts (Lens + ES|QL): move top-level `color` to `appearance.color`.
- Datatable validation: ensure each datatable has at least one metric or one dimension.
