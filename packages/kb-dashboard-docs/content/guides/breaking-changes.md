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
- Datatable validation: ensure each datatable has at least one metric or one breakdown.
- Range color mappings: rename `stops` to `thresholds` and nested `stop` to `up_to`.
- Pie charts (Lens + ES|QL): rename `dimensions` to `breakdowns`. Old name emits `DeprecationWarning`.
- Treemap charts (Lens + ES|QL): rename `dimensions` to `breakdowns`. Treemap now requires 1–2 breakdowns. Old name emits `DeprecationWarning`.
- Waffle charts (Lens + ES|QL): rename `dimension` to `breakdown`. The secondary `breakdown` field has been removed; waffle charts support exactly one breakdown. Old name emits `DeprecationWarning`.
- Datatable charts (Lens + ES|QL): rename `dimensions` (row groupings) to `breakdowns`, and rename `dimensions_by` (split metrics by) to `metrics_split_by`. Old names emit `DeprecationWarning`.
- All Lens charts: `collapse` is now only valid on breakdown fields (pie, treemap, waffle breakdowns; mosaic `breakdown`). The `collapse` field has been removed from plain dimension types used in XY chart `dimension`/`breakdown` axes.
- XY charts: rename legend `size` to `width`.
- XY charts: lowercase `appearance.missing_values` and `appearance.end_values` enum values.
- Lens top values dimensions: rename `other_bucket` to `show_other_bucket`.
- Lens top values dimensions: rename `missing_bucket` to `include_missing_values`.
- Lens intervals dimensions: rename `empty_bucket` to `include_empty_intervals`.
- Range color mappings: remove configurable range extension; `continuity` and `extend_beyond_range` are deprecated and ignored.

### Field Rename Reference

| Old field | New field | Notes |
| --------- | --------- | ----- |
| `stops[].stop` | `thresholds[].up_to` | Range color mappings |
| `stops` | `thresholds` | Range color mappings |
| `continuity` | removed (ignored) | Range color mappings always compile with `continuity: above` |
| `extend_beyond_range` | removed (ignored) | Range color mappings always compile with `continuity: above` |
| `dimensions` (pie/treemap) | `breakdowns` | Old name emits `DeprecationWarning` |
| `dimension` (waffle) | `breakdown` | Old name emits `DeprecationWarning` |
| `dimensions` (datatable row groupings) | `breakdowns` | Old name emits `DeprecationWarning` |
| `dimensions_by` (datatable split metrics by) | `metrics_split_by` | Old name emits `DeprecationWarning` |
| `legend.size` (XY) | `legend.width` | |
| `other_bucket` | `show_other_bucket` | Lens top values dimensions |
| `missing_bucket` | `include_missing_values` | Lens top values dimensions |
| `empty_bucket` | `include_empty_intervals` | Lens intervals dimensions |

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
