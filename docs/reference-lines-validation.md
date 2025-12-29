# Reference Lines Implementation Validation

This document validates that our reference lines implementation matches Kibana's expected structure.

## Kibana Source Code Analysis

Based on analysis of the [Kibana Lens source code](https://github.com/elastic/kibana/tree/main/x-pack/platform/plugins/shared/lens), reference lines in XY charts use the following structure:

### Layer Structure

```typescript
interface XYReferenceLineLayerConfig {
  layerId: string;
  layerType: 'referenceLine';
  accessors: string[];  // Column IDs
  yConfig?: YConfig[];
}
```

### YConfig Structure

```typescript
interface YConfig {
  forAccessor: string;     // Links to accessor ID
  color?: string;          // Hex color (e.g., '#FF0000')
  lineWidth?: number;      // Line width in pixels
  lineStyle?: string;      // 'solid' | 'dashed' | 'dotted'
  fill?: string;           // 'above' | 'below' | 'none'
  icon?: string;           // Icon identifier
  iconPosition?: string;   // Icon position
  axisMode?: {            // Axis assignment
    name: string;         // 'left' | 'right'
  };
}
```

### Column Structure

Reference lines use static value columns:

```typescript
interface StaticValueColumn {
  label: string;
  dataType: 'number';
  customLabel: true;
  operationType: 'static_value';
  isBucketed: false;
  scale: 'ratio';
  isStaticValue: true;
  params: {
    value: string;  // Stored as string (e.g., "500.0")
  };
  references: [];
}
```

## Our Implementation

Our compiler (`src/dashboard_compiler/panels/charts/xy/compile.py`) produces output that exactly matches Kibana's structure:

### Example Output

```json
{
  "layers": [
    {
      "layerId": "data-layer-id",
      "layerType": "data",
      "seriesType": "line",
      "accessors": ["metric-id"],
      "xAccessor": "dimension-id"
    },
    {
      "layerId": "ref-line-layer-id",
      "layerType": "referenceLine",
      "accessors": ["ref_line_ref-line-layer-id"],
      "yConfig": [
        {
          "forAccessor": "ref_line_ref-line-layer-id",
          "color": "#FF0000",
          "lineWidth": 2.0,
          "lineStyle": "dashed",
          "fill": "below",
          "axisMode": {
            "name": "left"
          }
        }
      ]
    }
  ]
}
```

### Columns

```json
{
  "ref_line_ref-line-layer-id": {
    "label": "SLA Threshold",
    "dataType": "number",
    "customLabel": true,
    "operationType": "static_value",
    "isBucketed": false,
    "scale": "ratio",
    "isStaticValue": true,
    "params": {
      "value": "500.0"
    },
    "references": []
  }
}
```

## Validation

✅ **Layer Structure**: Matches Kibana's `XYReferenceLineLayerConfig`

- `layerType` correctly set to `"referenceLine"`
- `accessors` array contains column IDs
- `yConfig` array contains styling configuration

✅ **YConfig Structure**: Matches Kibana's `YConfig`

- `forAccessor` links to the static value column
- `color`, `lineWidth`, `lineStyle`, `fill` all supported
- `axisMode` with `name` field for axis assignment
- Optional `icon` and `iconPosition` supported

✅ **Static Value Columns**: Matches Kibana's column structure

- `operationType: "static_value"`
- `dataType: "number"`
- `isStaticValue: true`
- `params.value` stored as string
- `customLabel: true` when label provided
- Empty `references` array

✅ **Value Handling**: Correctly handles both types

- Plain `float` values (e.g., `500.0`)
- `XYReferenceLineValue` objects with `type: 'static'`

## Test Coverage

Our test suite validates:

1. ✅ Layer count (data + reference lines)
2. ✅ Layer types (`layerType: "referenceLine"`)
3. ✅ Accessor IDs in layers
4. ✅ YConfig styling properties (color, lineWidth, lineStyle)
5. ✅ Axis mode configuration
6. ✅ Static value column creation
7. ✅ Column `operationType` and `dataType`
8. ✅ Value storage (as string in `params.value`)
9. ✅ Label handling with `customLabel` flag

## Conclusion

Our implementation is **fully compliant** with Kibana's reference line structure. The compiler produces output that matches:

- Type definitions from `@kbn/lens-common`
- Implementation patterns from the Lens source code
- Column and layer structures used by Kibana's visualization engine

No changes needed to the implementation.
