# Heatmap Support Implementation Plan

**Issue**: #10
**Status**: Planning Complete
**Generated**: 2025-12-31

---

## Overview

This document outlines the implementation plan for adding heatmap visualization support to the kb-yaml-to-lens compiler. Heatmaps in Kibana Lens display data as a 2D grid where cell colors represent metric values.

## Fixtures Generated

Successfully generated Kibana reference fixtures using the fixture generator:

- `fixture-generator/output/v9.2.0/heatmap-esql.json` - ES|QL variant
- `fixture-generator/output/v9.2.0/heatmap-dataview.json` - Data View variant

Both fixtures are committed and available for reference during implementation.

## Key Findings from Fixtures

### Visualization Type
- **Kibana identifier**: `lnsHeatmap`
- **Shape**: `"heatmap"` (literal value in visualization state)

### Required Accessors (from fixtures)

**ES|QL variant** (textBased datasource):
```json
{
  "valueAccessor": "metric_formula_accessor",
  "xAccessor": "x_metric_formula_accessor",
  "yAccessor": "y_metric_formula_accessor"
}
```

**Data View variant** (formBased datasource):
```json
{
  "valueAccessor": "metric_formula_accessor",
  "xAccessor": "x_metric_formula_accessor",  // terms operation
  "yAccessor": "y_metric_formula_accessor"   // terms operation
}
```

### Grid Configuration

Both variants include `gridConfig`:
```json
{
  "type": "heatmap_grid",
  "isCellLabelVisible": false,
  "isXAxisLabelVisible": false,
  "isXAxisTitleVisible": false,
  "isYAxisLabelVisible": false,
  "isYAxisTitleVisible": false
}
```

### Legend Configuration

Both variants include `legend`:
```json
{
  "isVisible": true,
  "position": "right",
  "type": "heatmap_legend"
}
```

---

## Implementation Architecture

Following the established three-layer pattern used by other chart types (pie, xy, metric):

```
src/dashboard_compiler/panels/charts/heatmap/
├── __init__.py
├── config.py          # Pydantic configuration models (YAML schema)
├── view.py            # Kibana JSON view models
└── compile.py         # Transformation logic
```

---

## Detailed Component Specifications

### 1. Configuration Models (`config.py`)

#### `HeatmapLegend`
```python
class HeatmapLegend(BaseCfgModel):
    """Legend configuration for heatmap charts."""

    visible: bool | None = Field(default=None)
    """Whether to show the legend. Kibana defaults to True."""

    position: Literal['top', 'right', 'bottom', 'left'] | None = Field(default=None)
    """Position of the legend. Kibana defaults to 'right'."""
```

#### `HeatmapGridConfig`
```python
class HeatmapGridConfig(BaseCfgModel):
    """Grid configuration for heatmap charts."""

    show_cell_labels: bool | None = Field(default=None)
    """Whether to show values inside cells. Kibana defaults to False."""

    show_x_axis_labels: bool | None = Field(default=None)
    """Whether to show X-axis labels. Kibana defaults to False."""

    show_x_axis_title: bool | None = Field(default=None)
    """Whether to show X-axis title. Kibana defaults to False."""

    show_y_axis_labels: bool | None = Field(default=None)
    """Whether to show Y-axis labels. Kibana defaults to False."""

    show_y_axis_title: bool | None = Field(default=None)
    """Whether to show Y-axis title. Kibana defaults to False."""
```

#### `BaseHeatmapChart`
```python
class BaseHeatmapChart(BaseChart):
    """Base model for heatmap chart configuration."""

    type: Literal['heatmap'] = Field(default='heatmap')

    legend: HeatmapLegend | None = Field(default=None)
    """Legend configuration."""

    grid: HeatmapGridConfig | None = Field(default=None)
    """Grid configuration."""

    color: ColorMapping | None = Field(default=None)
    """Color palette configuration."""
```

#### `LensHeatmapChart`
```python
class LensHeatmapChart(BaseHeatmapChart):
    """Heatmap chart using Lens formBased datasource."""

    data_view: str = Field(...)
    """The data view for the heatmap."""

    x_axis: LensDimensionTypes = Field(...)
    """X-axis dimension (typically terms aggregation)."""

    y_axis: LensDimensionTypes | None = Field(default=None)
    """Y-axis dimension (optional for 1D heatmaps)."""

    value: LensMetricTypes = Field(...)
    """Metric that determines cell color intensity."""
```

#### `ESQLHeatmapChart`
```python
class ESQLHeatmapChart(BaseHeatmapChart):
    """Heatmap chart using ES|QL textBased datasource."""

    x_axis: ESQLDimensionTypes = Field(...)
    """X-axis column from ES|QL query."""

    y_axis: ESQLDimensionTypes | None = Field(default=None)
    """Y-axis column from ES|QL query (optional)."""

    value: ESQLMetricTypes = Field(...)
    """Metric column from ES|QL query."""
```

### 2. View Models (`view.py`)

#### `KbnHeatmapLegend`
```python
class KbnHeatmapLegend(BaseVwModel):
    """Kibana heatmap legend configuration."""

    isVisible: bool
    position: Literal['top', 'right', 'bottom', 'left']
    type: Literal['heatmap_legend'] = 'heatmap_legend'
```

#### `KbnHeatmapGridConfig`
```python
class KbnHeatmapGridConfig(BaseVwModel):
    """Kibana heatmap grid configuration."""

    type: Literal['heatmap_grid'] = 'heatmap_grid'
    isCellLabelVisible: bool
    isXAxisLabelVisible: bool
    isXAxisTitleVisible: bool
    isYAxisLabelVisible: bool
    isYAxisTitleVisible: bool
```

#### `KbnHeatmapStateVisualizationLayer`
```python
class KbnHeatmapStateVisualizationLayer(KbnBaseStateVisualizationLayer):
    """Kibana heatmap visualization layer."""

    layerType: Literal['data'] = 'data'
    xAccessor: str
    yAccessor: str | None = None
    valueAccessor: str | None = None
```

#### `KbnHeatmapVisualizationState`
```python
class KbnHeatmapVisualizationState(KbnBaseStateVisualization):
    """Kibana heatmap visualization state."""

    shape: Literal['heatmap'] = 'heatmap'
    layerId: str
    layerType: Literal['data'] = 'data'
    xAccessor: str
    yAccessor: Annotated[str | None, OmitIfNone()] = None
    valueAccessor: Annotated[str | None, OmitIfNone()] = None
    gridConfig: KbnHeatmapGridConfig
    legend: KbnHeatmapLegend
```

### 3. Compilation Logic (`compile.py`)

#### `compile_heatmap_chart_visualization_state()`
```python
def compile_heatmap_chart_visualization_state(
    *,
    layer_id: str,
    chart: LensHeatmapChart | ESQLHeatmapChart,
    x_accessor_id: str,
    y_accessor_id: str | None,
    value_accessor_id: str,
) -> KbnHeatmapVisualizationState:
    """Compile heatmap config to Kibana visualization state.

    Args:
        layer_id: The layer ID
        chart: The heatmap chart config
        x_accessor_id: Column ID for X-axis
        y_accessor_id: Column ID for Y-axis (optional)
        value_accessor_id: Column ID for value metric

    Returns:
        Kibana heatmap visualization state
    """
```

#### `compile_lens_heatmap_chart()`
```python
def compile_lens_heatmap_chart(
    lens_heatmap_chart: LensHeatmapChart,
) -> tuple[str, dict[str, KbnLensColumnTypes], KbnHeatmapVisualizationState]:
    """Compile LensHeatmapChart to Kibana JSON.

    Args:
        lens_heatmap_chart: The heatmap chart config

    Returns:
        Tuple of (layer_id, columns_dict, visualization_state)
    """
```

#### `compile_esql_heatmap_chart()`
```python
def compile_esql_heatmap_chart(
    esql_heatmap_chart: ESQLHeatmapChart,
) -> tuple[str, list[KbnESQLColumnTypes], KbnHeatmapVisualizationState]:
    """Compile ESQLHeatmapChart to Kibana JSON.

    Args:
        esql_heatmap_chart: The heatmap chart config

    Returns:
        Tuple of (layer_id, columns_list, visualization_state)
    """
```

---

## Integration Points

### 1. Register Chart Type (`src/dashboard_compiler/panels/charts/config.py`)

Add to type unions:
```python
from dashboard_compiler.panels.charts.heatmap import ESQLHeatmapChart, LensHeatmapChart

type SingleLayerChartTypes = LensMetricChart | LensDatatableChart | LensGaugeChart | LensHeatmapChart

type ESQLChartTypes = (
    ESQLMetricChart
    | ESQLGaugeChart
    | ESQLPieChart
    | ESQLBarChart
    | ESQLAreaChart
    | ESQLLineChart
    | ESQLDatatableChart
    | ESQLTagcloudChart
    | ESQLHeatmapChart
)
```

Add panel config classes:
```python
class LensHeatmapPanelConfig(LensHeatmapChart, LensPanelFieldsMixin):
    """Configuration for a Lens heatmap panel."""

class ESQLHeatmapPanelConfig(ESQLHeatmapChart, ESQLPanelFieldsMixin):
    """Configuration for an ES|QL heatmap panel."""
```

Add to discriminated unions:
```python
type LensPanelConfig = Annotated[
    Annotated[LensMetricPanelConfig, Tag('metric')]
    | Annotated[LensGaugePanelConfig, Tag('gauge')]
    | Annotated[LensPiePanelConfig, Tag('pie')]
    | Annotated[LensLinePanelConfig, Tag('line')]
    | Annotated[LensBarPanelConfig, Tag('bar')]
    | Annotated[LensAreaPanelConfig, Tag('area')]
    | Annotated[LensTagcloudPanelConfig, Tag('tagcloud')]
    | Annotated[LensDatatablePanelConfig, Tag('datatable')]
    | Annotated[LensHeatmapPanelConfig, Tag('heatmap')],
    Discriminator('type'),
]

type ESQLPanelConfig = Annotated[
    Annotated[ESQLMetricPanelConfig, Tag('metric')]
    | Annotated[ESQLGaugePanelConfig, Tag('gauge')]
    | Annotated[ESQLPiePanelConfig, Tag('pie')]
    | Annotated[ESQLLinePanelConfig, Tag('line')]
    | Annotated[ESQLBarPanelConfig, Tag('bar')]
    | Annotated[ESQLAreaPanelConfig, Tag('area')]
    | Annotated[ESQLTagcloudPanelConfig, Tag('tagcloud')]
    | Annotated[ESQLDatatablePanelConfig, Tag('datatable')]
    | Annotated[ESQLHeatmapPanelConfig, Tag('heatmap')],
    Discriminator('type'),
]
```

### 2. Update Compilation Logic (`src/dashboard_compiler/panels/charts/compile.py`)

Add imports:
```python
from dashboard_compiler.panels.charts.heatmap.compile import (
    compile_lens_heatmap_chart,
    compile_esql_heatmap_chart,
)
from dashboard_compiler.panels.charts.heatmap.config import (
    LensHeatmapChart,
    ESQLHeatmapChart,
)
```

Update `chart_type_to_kbn_type_lens()`:
```python
if isinstance(chart, (LensHeatmapChart, ESQLHeatmapChart)):
    return KbnVisualizationTypeEnum.HEATMAP
```

Add compilation cases in `compile_lens_chart_state()`:
```python
elif isinstance(chart, LensHeatmapChart):
    layer_id, columns, vis_state = compile_lens_heatmap_chart(chart)
    # ... rest of compilation logic
```

Add compilation cases in `compile_esql_chart_state()`:
```python
elif isinstance(esql_chart, ESQLHeatmapChart):
    layer_id, columns, vis_state = compile_esql_heatmap_chart(esql_chart)
    # ... rest of compilation logic
```

### 3. Add Visualization Type Enum (`src/dashboard_compiler/panels/charts/view.py`)

```python
class KbnVisualizationTypeEnum(StrEnum):
    # ... existing types
    HEATMAP = 'lnsHeatmap'
```

Update visualization state union type:
```python
from dashboard_compiler.panels.charts.heatmap.view import KbnHeatmapVisualizationState

type KbnVisualizationStateTypes = (
    # ... existing types
    | KbnHeatmapVisualizationState
)
```

---

## Testing Strategy

### 1. Create Test Scenarios

Structure similar to existing chart tests:
```
tests/scenarios/heatmap/
├── one-heatmap-basic/
│   ├── config.yaml           # YAML configuration
│   └── from-kibana.json      # Expected output (from fixture)
├── one-heatmap-esql/
│   ├── config.yaml
│   └── from-kibana.json
└── one-heatmap-with-options/
    ├── config.yaml
    └── from-kibana.json
```

### 2. Unit Tests

Add to `tests/test_charts.py` or create `tests/test_heatmap.py`:
- Test basic heatmap compilation
- Test ES|QL heatmap compilation
- Test legend configuration
- Test grid configuration
- Test color mapping
- Test optional Y-axis (1D heatmap)

### 3. Snapshot Tests

Use inline-snapshot library for comparing compiled output against expected JSON.

---

## Example YAML Configurations

### Basic Lens Heatmap
```yaml
panels:
  - lens:
      type: heatmap
      data_view: kibana_sample_data_logs
      x_axis:
        field: geo.src
      y_axis:
        field: geo.dest
      value:
        sum:
          field: bytes
```

### ES|QL Heatmap
```yaml
panels:
  - esql:
      type: heatmap
      query:
        esql: |
          FROM kibana_sample_data_logs
          | STATS bytes = SUM(bytes) BY geo.dest, geo.src
      x_axis:
        field: geo.src
      y_axis:
        field: geo.dest
      value:
        field: bytes
```

### Heatmap with Options
```yaml
panels:
  - lens:
      type: heatmap
      data_view: kibana_sample_data_logs
      x_axis:
        field: machine.os.keyword
      y_axis:
        field: geo.dest
      value:
        average:
          field: bytes
      legend:
        visible: true
        position: bottom
      grid:
        show_cell_labels: true
        show_x_axis_labels: true
        show_y_axis_labels: true
```

---

## Implementation Checklist

### Phase 1: Core Implementation
- [ ] Create `src/dashboard_compiler/panels/charts/heatmap/__init__.py`
- [ ] Create `src/dashboard_compiler/panels/charts/heatmap/config.py`
- [ ] Create `src/dashboard_compiler/panels/charts/heatmap/view.py`
- [ ] Create `src/dashboard_compiler/panels/charts/heatmap/compile.py`

### Phase 2: Integration
- [ ] Update `src/dashboard_compiler/panels/charts/config.py`
- [ ] Update `src/dashboard_compiler/panels/charts/compile.py`
- [ ] Update `src/dashboard_compiler/panels/charts/view.py`
- [ ] Update `src/dashboard_compiler/panels/charts/__init__.py`

### Phase 3: Testing
- [ ] Create test scenarios with YAML configs
- [ ] Copy fixture JSONs to test scenarios
- [ ] Add unit tests
- [ ] Add snapshot tests
- [ ] Run `make check` - all tests pass

### Phase 4: Documentation
- [ ] Create `docs/charts/heatmap.md` with usage examples
- [ ] Update `docs/charts/index.md` to include heatmap
- [ ] Add heatmap examples to `inputs/` directory

### Phase 5: Verification
- [ ] Run `make ci` - all checks pass
- [ ] Manual testing with sample dashboards
- [ ] Cross-reference with Kibana fixtures

---

## Notes and Considerations

1. **Optional Y-axis**: Heatmaps can be 1D (only X-axis) or 2D (X and Y axes). The `yAccessor` field is optional in the fixture.

2. **Palette Support**: The fixtures don't show custom palette configuration, but Kibana supports it. We can add this in a future iteration if needed.

3. **Grid Configuration Defaults**: Most grid visibility options default to `false` in Kibana, making heatmaps quite minimal by default.

4. **Legend Position**: Defaults to `'right'` according to fixture data.

5. **Color Mapping**: Heatmaps support the same color mapping pattern as other charts via the `BaseChart` class.

6. **Single Layer**: Heatmaps are single-layer visualizations like metrics and gauges, not multi-layer like XY charts.

---

## References

- Generated fixtures: `fixture-generator/output/v9.2.0/heatmap-*.json`
- Previous investigation: Issue #10 comments (December 2025)
- Existing implementations: `src/dashboard_compiler/panels/charts/{pie,metric,gauge}/`
- Project patterns: `src/dashboard_compiler/AGENTS.md`
