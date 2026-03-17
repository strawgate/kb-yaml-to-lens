# Breaking Changes

This guide tracks user-facing breaking changes and migrations between releases.

Use the CLI to access this guide from a local install:

- `kb-dashboard docs guide breaking-changes`

## 0.2.7 -> 0.4.0

!!! important
    Starting with `0.4.0`, we only support compatibility from `0.2.7` directly to `0.4.0`.
    Compatibility behavior specific to intermediate `0.3.x` releases is intentionally dropped.
    Use `kb-dashboard upgrade` to rewrite legacy `0.2.7` YAML into the canonical `0.4.0` schema.

### Migration Checklist

#### Run the upgrader first

Run the schema upgrader before compiling:

```bash
kb-dashboard upgrade --input-dir inputs --write
```

For CI validation (without writing files):

```bash
kb-dashboard upgrade --input-dir inputs --fail-on-change
```

#### Datatable

- Remove `columns` and `metric_columns` lists. Display settings (width, alignment, hidden, etc.) now live directly on each metric or breakdown under `appearance`.
- Replace `color_mode` (`none`/`cell`/`text`) with `color.apply_to` on each metric.
- Rename `dimensions` to `breakdowns` and `dimensions_by` to `metrics_split_by`.

#### Metric

- The old chart-level `color` field (palette name + assignments) is no longer supported. Color thresholds are now configured on the primary metric via `primary.color` with `thresholds`, `range_type`, `range_min`, `range_max`, and `apply_to`.

#### XY

- Rename `legend.size` to `legend.width`.
- Lowercase `appearance.missing_values` and `appearance.end_values` enum values (e.g., `'Linear'` becomes `'linear'`).

#### Pie

- Rename `dimensions` to `breakdowns`.

#### Heatmap

- Rename `value` to `metric` on heatmap charts. The `value` field is now `metric` to align with other chart types.

#### Dimensions / Breakdowns

- `collapse` is now only valid on breakdown fields. If you had `collapse` on a plain dimension (e.g., XY `dimension`), move it to a breakdown instead.
- ES|QL: `collapse` has moved from `ESQLDimension` to `ESQLBreakdown`. Move `dimension.collapse` to `breakdown.collapse`.
- Lens top values: rename `other_bucket` to `show_other_bucket` and `missing_bucket` to `include_missing_values`.
- Lens intervals: rename `empty_bucket` to `include_empty_intervals`.
