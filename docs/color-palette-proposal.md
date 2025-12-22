# Color Palette Configuration Schema Proposal

## Executive Summary

This document outlines the proposed configuration schema for color palettes in kb-yaml-to-lens, based on a thorough review of Kibana Lens color mapping capabilities and the existing codebase.

## Current State

### Existing Implementation (Pie Charts Only)

Color palette support currently exists only for pie charts:

- **Config**: `ColorMapping` class in `src/dashboard_compiler/panels/charts/pie/config.py`
- **View**: `KbnLayerColorMapping` class in `src/dashboard_compiler/panels/charts/base/view.py`
- **Current YAML syntax**:
  ```yaml
  color:
    palette: eui_amsterdam_color_blind
  ```

### Kibana JSON Structure

Generated Kibana JSON includes:
```json
{
  "colorMapping": {
    "assignments": [],
    "specialAssignments": [{
      "rule": {"type": "other"},
      "color": {"type": "loop"},
      "touched": false
    }],
    "paletteId": "eui_amsterdam_color_blind",
    "colorMode": {"type": "categorical"}
  }
}
```

## Kibana Color Palette Capabilities

### Available Palette IDs

**Categorical Palettes:**
- `default` - Standard EUI palette
- `eui_amsterdam_color_blind` - Color-blind safe (recommended)
- `kibana_palette` / `legacy` - Legacy Kibana colors
- `elastic_brand` - Elastic brand colors
- `gray` - Grayscale

**Gradient Palettes:**
- Various sequential and diverging gradients

### Color Mapping Schema

| Field | Type | Description |
|-------|------|-------------|
| `paletteId` | string | Base palette for unassigned values |
| `colorMode` | object | `{type: 'categorical'}` or `{type: 'gradient'}` |
| `assignments` | array | Manual color assignments to specific values |
| `specialAssignments` | array | Default/fallback rules for unassigned values |

### Advanced Features (Kibana 8.11+)

- **Manual Assignments**: Map specific data values to custom hex colors
- **Assignment Types**: Plain categories, ranges, formulas, regex patterns
- **Gradients**: Single, sequential (two-color), or divergent (three-color)
- **Theme Awareness**: Colors adapt between light/dark themes
- **Neutral Colors**: Theme-aware grayscale options

## Proposed YAML Schema

### Phase 1: Simple Palette Selection (All Charts)

Extend current simple palette support to all chart types:

```yaml
panels:
  - type: line
    color:
      palette: eui_amsterdam_color_blind
```

**Pros:**
- Simple, intuitive syntax
- Backwards compatible
- Covers 80% of use cases
- Low implementation complexity

### Phase 2: Manual Color Assignments

Add support for custom color mappings:

```yaml
panels:
  - type: pie
    color:
      palette: eui_amsterdam_color_blind  # Default for unassigned
      mode: categorical
      assignments:
        - value: "production"
          color: "#FF0000"
        - value: "staging"
          color: "#00FF00"
        - values: ["dev", "test"]  # Multiple values → same color
          color: "#0000FF"
```

**Pros:**
- Precise control over colors
- Supports brand guidelines
- Consistent colors across dashboards

**Cons:**
- More complex configuration
- Requires maintenance as data changes

### Phase 3: Gradient Configuration

Add gradient palette support:

```yaml
panels:
  - type: metric
    color:
      mode: gradient
      gradient:
        type: sequential  # or 'divergent'
        colors:
          - "#00FF00"  # Start (low values)
          - "#FF0000"  # End (high values)
      range_assignments:
        - min: 0
          max: 50
          color: "#00FF00"
        - min: 50
          max: 100
          color: "#FF0000"
```

**Use cases:**
- Heatmaps
- Metric visualizations with thresholds
- Likert scales

## Implementation Plan

### Phase 1: Palette Support for All Charts

#### 1. Refactor ColorMapping Model

Move from pie-specific to shared:

```python
# src/dashboard_compiler/panels/charts/base/config.py

class ColorMapping(BaseCfgModel):
    """Color configuration for charts."""

    palette: str = Field(default='eui_amsterdam_color_blind')
    """The palette ID to use for chart colors."""
```

#### 2. Add Color Field to Chart Types

Update config models:
- `src/dashboard_compiler/panels/charts/xy/config.py` - BaseXYChart
- `src/dashboard_compiler/panels/charts/metric/config.py` - MetricChart
- Update pie chart to use shared model

#### 3. Update Compilation Functions

Modify compile functions to apply color mapping:
- `src/dashboard_compiler/panels/charts/xy/compile.py`
- `src/dashboard_compiler/panels/charts/metric/compile.py`

#### 4. Add Tests

Add test cases for each chart type with color palettes.

### Phase 2: Manual Assignments (Future)

#### 1. Enhance ColorMapping Model

```python
class ColorAssignment(BaseCfgModel):
    """Manual color assignment to specific values."""

    value: str | None = None
    """Single value to assign color to."""

    values: list[str] | None = None
    """Multiple values to assign same color to."""

    color: str = Field(...)
    """Hex color code (e.g., '#FF0000')."""

class ColorMapping(BaseCfgModel):
    """Color configuration for charts."""

    palette: str = Field(default='eui_amsterdam_color_blind')
    """Base palette for unassigned values."""

    mode: Literal['categorical', 'gradient'] = Field(default='categorical')
    """Color assignment mode."""

    assignments: list[ColorAssignment] = Field(default_factory=list)
    """Manual color assignments."""
```

#### 2. Enhance View Model

Update `KbnLayerColorMapping` to populate `assignments` array:

```python
class KbnColorAssignment(BaseVwModel):
    """Kibana color assignment."""

    rule: dict[str, Any]  # {type: 'matchExactly', values: [...]}
    color: dict[str, Any]  # {type: 'colorCode', colorCode: '#FF0000'}
    touched: bool = False

class KbnLayerColorMapping(BaseVwModel):
    """Color mapping configuration for a visualization layer."""

    assignments: list[KbnColorAssignment] = Field(default_factory=list)
    specialAssignments: list[KbnLayerColorMappingSpecialAssignment] = ...
    paletteId: str = 'eui_amsterdam_color_blind'
    colorMode: dict[str, str] = Field(default_factory=lambda: {'type': 'categorical'})
```

#### 3. Compilation Logic

Transform YAML assignments to Kibana format:

```python
def compile_color_assignments(
    assignments: list[ColorAssignment]
) -> list[KbnColorAssignment]:
    """Convert YAML color assignments to Kibana format."""
    kbn_assignments = []

    for assignment in assignments:
        # Determine values
        if assignment.value:
            values = [assignment.value]
        elif assignment.values:
            values = assignment.values
        else:
            continue

        # Create Kibana assignment
        kbn_assignment = KbnColorAssignment(
            rule={'type': 'matchExactly', 'values': values},
            color={'type': 'colorCode', 'colorCode': assignment.color},
            touched=False
        )
        kbn_assignments.append(kbn_assignment)

    return kbn_assignments
```

### Phase 3: Gradient Support (Future)

Add gradient-specific models and compilation logic.

## Recommendations

### Recommended Starting Point: Phase 1

**Why Phase 1 First:**
1. **Immediate Value**: Enables palette selection for all chart types
2. **Low Risk**: Simple extension of existing pattern
3. **Backwards Compatible**: Doesn't break existing pie chart configs
4. **High Coverage**: Addresses most common use cases

**Estimated Effort**: 2-4 hours
- 1 hour: Refactor and extend config models
- 1 hour: Update compilation functions
- 1-2 hours: Tests and documentation

### When to Implement Phase 2

Implement manual assignments when users need:
- Brand-specific colors (e.g., production=red, staging=yellow)
- Consistent colors across multiple dashboards
- Custom color schemes for specific categories

**Estimated Effort**: 4-8 hours
- 2-3 hours: Enhanced models and compilation
- 2-3 hours: Tests and validation
- 1-2 hours: Documentation and examples

### When to Implement Phase 3

Implement gradients when users need:
- Heatmap visualizations
- Threshold-based color coding
- Divergent color schemes (good/neutral/bad)

**Estimated Effort**: 4-6 hours

## Files to Modify

### Phase 1
- `src/dashboard_compiler/panels/charts/base/config.py` - Shared ColorMapping
- `src/dashboard_compiler/panels/charts/xy/config.py` - Add color field
- `src/dashboard_compiler/panels/charts/metric/config.py` - Add color field
- `src/dashboard_compiler/panels/charts/pie/config.py` - Use shared ColorMapping
- `src/dashboard_compiler/panels/charts/xy/compile.py` - Apply color mapping
- `src/dashboard_compiler/panels/charts/metric/compile.py` - Apply color mapping
- `tests/panels/charts/xy/test_xy_data.py` - Add color tests
- `tests/panels/charts/metric/test_metric_data.py` - Add color tests

### Phase 2
- `src/dashboard_compiler/panels/charts/base/config.py` - Enhanced ColorMapping
- `src/dashboard_compiler/panels/charts/base/view.py` - Enhanced KbnLayerColorMapping
- All compile.py files - Assignment transformation logic

## References

- [Kibana Color Mapping Discussion](https://discuss.elastic.co/t/dec-19th-2023-en-kibana-lens-color-mapping-color-palettes/347298)
- [Chart Level Categorical Palettes PR](https://github.com/elastic/kibana/pull/69800)
- [Color Mappings MVP Issue](https://github.com/elastic/kibana/issues/155037)
- Existing implementation: `src/dashboard_compiler/panels/charts/pie/` directory

## Questions for Product Owner

1. **Scope**: Should we implement Phase 1 now, or is this just a research/planning exercise?
2. **Priority**: Which chart types need color palette support most urgently?
   - XY charts (line, bar, area)?
   - Metric charts?
   - Table charts?
3. **Use Cases**: Do you foresee needing manual color assignments (Phase 2), or is palette selection sufficient?
4. **Timeline**: When would you like this capability available?
