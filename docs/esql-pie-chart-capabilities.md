# ES|QL Pie Chart Capabilities

This document provides a comprehensive comparison of ES|QL pie chart capabilities between Kibana's native schema and the kb-yaml-to-lens implementation.

## Overview

ES|QL pie charts in kb-yaml-to-lens support most of the core features available in Kibana's native partition visualizations. This page documents what's supported, what's missing, and provides guidance on using advanced features.

## Capabilities Comparison

| Feature | Kibana | kb-yaml-to-lens | Priority | Schema Type/Values |
|---------|--------|-----------------|----------|-------------------|
| **Chart Shapes** | 5 shapes | 2 shapes | Medium | `"pie"` \| `"donut"` \| `"treemap"` \| `"mosaic"` \| `"waffle"` |
| **Secondary Groups** | ✅ | ✅ | **HIGH** | `secondaryGroups?: string[]` |
| **Multiple Metrics** | ✅ | ✅ | Medium | `metrics: string[]` + `allowMultipleMetrics?: boolean` |
| **Collapse Functions** | ✅ | ✅ | Low-Med | `collapseFns?: Record<string, "sum"\|"avg"\|"min"\|"max">` |
| **Legend Position** | ✅ | ❌ | Low | `legendPosition?: "top"\|"left"\|"right"\|"bottom"` |
| **Legend Stats** | ✅ | ❌ | Low | `legendStats?: PartitionLegendValue[]` |
| **Percent Decimals** | ✅ | ✅ | Very Low | `percentDecimals?: number` |
| **Modern Color Mapping** | ✅ | ⚠️ | Medium | `colorMapping?: ColorMapping.Config` |
| **Colors by Dimension** | ✅ | ❌ | Medium | `colorsByDimension?: Record<string, string>` |
| **Number Display** | ✅ | ✅ | ✅ | `"hidden"` \| `"percent"` \| `"value"` |
| **Category Display** | ✅ | ✅ | ✅ | `"default"` \| `"inside"` \| `"hide"` |
| **Legend Display** | ✅ | ✅ | ✅ | `"default"` \| `"show"` \| `"hide"` |
| **Empty Size Ratio** | ✅ | ✅ | ✅ | `0.3` (small) \| `0.54` (medium) \| `0.7` (large) |
| **Legend Size/Truncation** | ✅ | ✅ | ✅ | `legendSize`, `truncateLegend`, `legendMaxLines` |
| **Nested Legend** | ✅ | ✅ | ✅ | `nestedLegend?: boolean` |

## Supported Features

### Basic Pie/Donut Charts

Create simple pie or donut charts with ES|QL queries:

```yaml
chart:
  type: pie
  esql: "FROM metrics-* | STATS count(*) BY service.name"
  metric:
    field: "count(*)"
  slice_by:
    - field: "service.name"
  appearance:
    donut: medium  # small, medium, large, or omit for pie chart
```

### Secondary Groups (Hierarchical Slicing)

Create multi-level nested visualizations with primary and secondary dimensions:

```yaml
chart:
  type: pie
  esql: "FROM metrics-* | STATS count(*) BY continent, country"
  metric:
    field: "count(*)"
  slice_by:
    - field: "continent"
  secondary_slice_by:
    - field: "country"
```

### Multiple Metrics

Use multiple metrics in a single pie chart:

```yaml
chart:
  type: pie
  esql: "FROM metrics-* | STATS count(*), sum(bytes) BY service.name"
  metrics:
    - field: "count(*)"
    - field: "sum(bytes)"
  slice_by:
    - field: "service.name"
```

**Note**: When using multiple metrics, you cannot use the single `metric` field. Use `metrics` (plural) instead.

### Collapse Functions

Apply aggregation functions to dimensions for advanced data transformation:

```yaml
chart:
  type: pie
  esql: "FROM metrics-* | STATS count(*) BY service.name"
  metric:
    field: "count(*)"
  slice_by:
    - field: "service.name"
      collapse: sum  # sum, avg, min, or max
```

### Legend Configuration

Control legend appearance and behavior:

```yaml
chart:
  type: pie
  esql: "FROM metrics-* | STATS count(*) BY service.name"
  metric:
    field: "count(*)"
  slice_by:
    - field: "service.name"
  legend:
    visible: show  # show, hide, auto
    width: large   # small, medium, large, extra_large
    truncate_labels: 2  # 0-5, where 0 = no truncation
```

### Slice Labels and Values

Configure how labels and values appear on slices:

```yaml
chart:
  type: pie
  esql: "FROM metrics-* | STATS count(*) BY service.name"
  metric:
    field: "count(*)"
  slice_by:
    - field: "service.name"
  titles_and_text:
    slice_labels: auto  # hide, inside, auto
    slice_values: percent  # hide, integer, percent
    value_decimal_places: 2  # 0-10
```

## Missing Capabilities

### Chart Shapes

**Status**: Not supported
**Impact**: Medium

Kibana supports five chart shapes: `pie`, `donut`, `treemap`, `mosaic`, and `waffle`. Currently, kb-yaml-to-lens only supports `pie` and `donut`.

**Workaround**: Use standard pie or donut charts. For hierarchical data visualization needs, consider using secondary groups with pie/donut charts.

### Legend Position

**Status**: Not supported
**Impact**: Low

Kibana allows specifying legend position (`top`, `left`, `right`, `bottom`). kb-yaml-to-lens uses Kibana's default positioning.

**Workaround**: None needed - default positioning works for most use cases.

### Legend Stats

**Status**: Not supported
**Impact**: Low

Kibana allows controlling which statistics appear in legend items (value, percent, comparison values).

**Workaround**: Use the `titles_and_text` configuration to control label and value display on slices.

### Advanced Color Mapping

**Status**: Partially supported
**Impact**: Medium

kb-yaml-to-lens creates basic color mappings with palette IDs but doesn't support:

- Custom color assignments for specific values
- Special assignment rules
- Color mode configuration

**Workaround**: Use the default color palettes. Custom colors can be configured in Kibana UI after import.

### Colors by Dimension

**Status**: Not supported
**Impact**: Medium

Kibana allows mapping specific dimension values to hex colors (e.g., "USA" → "#0000FF").

**Workaround**: Configure colors in Kibana UI after importing the dashboard.

## Schema Reference

### Kibana Native Schema

The following TypeScript interfaces define Kibana's native pie chart schema:

```typescript
// Main visualization state
interface LensPartitionVisualizationState {
  shape: PartitionChartType;  // "pie" | "donut" | "treemap" | "mosaic" | "waffle"
  layers: LensPartitionLayerState[];
  palette?: PaletteOutput;  // @deprecated - use layer.colorMapping instead
}

// Layer configuration
interface SharedPartitionLayerState {
  metrics: string[];
  primaryGroups: string[];
  secondaryGroups?: string[];
  allowMultipleMetrics?: boolean;
  colorsByDimension?: Record<string, string>;
  collapseFns?: Record<string, CollapseFunction>;  // "sum" | "avg" | "min" | "max"
  numberDisplay: NumberDisplayType;  // "hidden" | "percent" | "value"
  categoryDisplay: CategoryDisplayType;  // "default" | "inside" | "hide"
  legendDisplay: LegendDisplayType;  // "default" | "show" | "hide"
  legendPosition?: Position;  // "top" | "left" | "right" | "bottom"
  legendStats?: PartitionLegendValue[];
  nestedLegend?: boolean;
  percentDecimals?: number;
  emptySizeRatio?: number;  // 0.3 (small), 0.54 (medium), 0.7 (large)
  legendMaxLines?: number;
  legendSize?: LegendSize;
  truncateLegend?: boolean;
  colorMapping?: ColorMapping.Config;
}
```

### kb-yaml-to-lens Implementation

The kb-yaml-to-lens implementation uses Pydantic models to define the YAML schema:

**Configuration Model** (`src/dashboard_compiler/panels/charts/pie/config.py`):

```python
class ESQLPieChart(BasePieChart):
    """ES|QL pie chart configuration"""
    esql: str | list[str]
    metric: ESQLMetricTypes = Field(default=...)  # Single metric
    metrics: list[ESQLMetricTypes] | None = None  # Multiple metrics
    slice_by: list[ESQLDimensionTypes] = Field(default_factory=list)
    secondary_slice_by: list[ESQLDimensionTypes] | None = None
```

**View Model** (`src/dashboard_compiler/panels/charts/pie/view.py`):

```python
class KbnPieStateVisualizationLayer(BaseModel):
    primaryGroups: list[str]
    secondaryGroups: list[str] | None = None
    metrics: list[str]
    allowMultipleMetrics: bool | None = None
    numberDisplay: Literal['hidden', 'percent', 'value']
    categoryDisplay: Literal['default', 'inside', 'hide']
    legendDisplay: Literal['default', 'show', 'hide']
    nestedLegend: bool
    legendMaxLines: int
    legendSize: Literal['small', 'medium', 'large', 'extra_large']
    truncateLegend: bool
    emptySizeRatio: float | None = None
    collapseFns: dict[str, str] | None = None
```

## Implementation Notes

### Backward Compatibility

The implementation maintains backward compatibility:

- Single `metric` field still works for simple charts
- Use `metrics` (plural) when you need multiple metrics
- Cannot use both `metric` and `metrics` simultaneously

### Compilation Logic

During compilation (`src/dashboard_compiler/panels/charts/pie/compile.py`):

1. Configuration models are validated using Pydantic
2. Dimensions are compiled to column references
3. Collapse functions are extracted from dimension properties
4. Visualization state is built with all supported features
5. Output is serialized to Kibana-compatible JSON

### Testing

The implementation includes comprehensive test coverage:

- Unit tests: `test/panels/charts/pie/test_pie.py`
- Test fixtures: `test/panels/charts/pie/test_pie_data.py`
- Snapshot tests ensure output matches expected Kibana JSON

## Related Documentation

- [YAML Reference](yaml_reference.md) - Complete schema documentation
- [ES|QL Documentation](api/panels.md) - ES|QL panel configuration
- [Pie Chart Configuration](../src/dashboard_compiler/panels/charts/pie/config.md) - Detailed pie chart options

## Source References

Kibana source code references (elastic/kibana repository):

- Schema: `src/platform/packages/shared/kbn-lens-common/visualizations/partition/types.ts`
- Constants: `src/platform/packages/shared/kbn-lens-common/visualizations/constants.ts`
- Implementation: `x-pack/platform/plugins/shared/lens/public/visualizations/partition/visualization.tsx`
