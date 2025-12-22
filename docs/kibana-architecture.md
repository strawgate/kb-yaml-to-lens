# Kibana Dashboard Architecture Reference

This document provides a comprehensive technical reference for Kibana's
dashboard and panel architecture, specifically designed to support the
development and understanding of YAML-to-Kibana compilation tools.

## Overview

Kibana dashboards are stored as **saved objects** in Elasticsearch using a
specific schema. The most critical architectural pattern is that complex
configuration data is stored as **stringified JSON** within the `attributes`
field of saved objects. Understanding this pattern is essential for any tool
that generates Kibana dashboards programmatically.

### Key Architectural Principles

1. **Saved Objects Model**: Dashboards are persisted as saved objects with
   type `"dashboard"` in Elasticsearch
2. **Stringified JSON**: Fields like `panelsJSON`, `optionsJSON`, and
   `searchSourceJSON` contain JSON serialized as strings
3. **Reference System**: External dependencies (data views, saved
   visualizations) are normalized into a `references` array
4. **By-Value vs By-Reference**: Panels can either embed full visualization
   configurations inline (by-value) or link to separately saved visualizations
   (by-reference)
5. **Lens as Primary Target**: Legacy visualization types are deprecated;
   modern dashboards should exclusively use Lens

## Version Evolution

### Timeline Overview

| Version | Key Changes | Impact on Compilers |
|---------|-------------|---------------------|
| **7.x** | Introduced modern `gridData` format, Lens visualizations | Foundation for current architecture |
| **8.0** | Globally unique IDs across spaces, removed legacy import API | Must use Saved Objects API |
| **8.8+** | Index splitting (`.kibana` → multiple indices) | Transparent to API users |
| **8.10+** | Model versions replace legacy migrations | New version tracking system |
| **8.19+** | Collapsible sections, custom grid layout | New panel grouping mechanism |
| **9.0** | Disabled creation of legacy viz types, internal API restrictions | Must target Lens exclusively |
| **9.0+** | ES\|QL variable controls, Content Management v3 API | New filter/query capabilities |
| **10.0** | Full removal of TSVB, aggregation-based, Timelion | Complete deprecation |

### Migration from 8.x to 9.x

The core dashboard JSON structure remains backward compatible between 8.x and
9.x. Key differences:

#### Content Management v3 API (9.x)

The new API layer destringifies JSON for easier programmatic access:

| Storage Field | v3 API Field | Compiler Target |
|--------------|--------------|-----------------|
| `panelsJSON` (string) | `panels` (array) | Use stringified format |
| `optionsJSON` (string) | `options` (object) | Use stringified format |
| `searchSourceJSON` (string) | `searchSource` (object) | Use stringified format |

**Recommendation**: Compilers should output the stringified format for maximum
compatibility with both direct saved object operations and older Kibana
versions.

#### Model Versions System

After Kibana 8.10.0, the legacy `migrations` property is deprecated. The new
`modelVersions` system uses consecutive integers (1, 2, 3...) decoupled from
Kibana release versions.

Version field changes:

| Field | Status | Usage |
|-------|--------|-------|
| `migrationVersion` (map) | Being phased out | Legacy version tracking |
| `typeMigrationVersion` | Current standard | Primary version field |
| `coreMigrationVersion` | Active | Tracks core Kibana version |

#### Legacy Visualization Deprecations

| Visualization Type | 9.x Status | Full Removal |
|-------------------|------------|--------------|
| **TSVB** | Creation disabled, existing work | 10.0 |
| **Aggregation-based** | Creation disabled, existing work | 10.0 |
| **Timelion (viz)** | Creation disabled, existing work | 10.0 |
| **Vega** | Fully supported | No removal planned |
| **Logs Stream panel** | **REMOVED** | 9.0 |
| **Legacy Input Controls** | Hidden by default | TBD |

**Critical for compilers**: Target Lens (`lns*` visualization types) as the
primary output format since legacy visualization creation is disabled in 9.0
and scheduled for full removal in 10.0.

## Saved Object Structure

### Top-Level Schema

Every dashboard saved object follows this structure:

```json
{
  "id": "730ea5e4-dc12-4b1c-aee4-a6af849be9be",
  "type": "dashboard",
  "namespaces": ["default"],
  "updated_at": "2024-01-08T22:30:30.879Z",
  "created_at": "2024-01-08T22:30:30.879Z",
  "version": "Wzg1LDdd",
  "typeMigrationVersion": "8.7.0",
  "managed": false,
  "attributes": { /* Dashboard-specific data */ },
  "references": [ /* External object references */ ]
}
```

### Dashboard Attributes

The `attributes` object contains all dashboard-specific configuration:

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `title` | string | Dashboard display name | Yes |
| `description` | string | Optional dashboard description | No |
| `version` | number | Internal schema version (typically `1`) | Yes |
| `timeRestore` | boolean | Whether to restore saved time range on load | No |
| `timeFrom` | string | Saved time range start (e.g., `"now-15m"`) | No |
| `timeTo` | string | Saved time range end (e.g., `"now"`) | No |
| `refreshInterval` | object | Auto-refresh: `{pause: boolean, value: number}` | No |
| `kibanaSavedObjectMeta` | object | Contains `searchSourceJSON` (stringified) | Yes |
| `optionsJSON` | string | **Stringified dashboard display options** | Yes |
| `panelsJSON` | string | **Stringified array of panel configurations** | Yes |
| `controlGroupInput` | object | Filter controls configuration | No |

**Critical**: The `panelsJSON`, `optionsJSON`, and `searchSourceJSON` fields
are **stringified JSON strings**, not native objects. Compilers must serialize
these fields as escaped JSON strings within the final output.

### Search Source JSON

Controls dashboard-level queries and filters:

```json
{
  "query": {
    "query": "",
    "language": "kuery"
  },
  "filter": [
    {
      "$state": { "store": "appState" },
      "meta": {
        "alias": null,
        "disabled": false,
        "negate": false,
        "type": "phrase",
        "key": "field_name",
        "params": { "query": "value" },
        "indexRefName": "kibanaSavedObjectMeta.searchSourceJSON.filter[0].meta.index"
      },
      "query": {
        "match_phrase": { "field_name": "value" }
      }
    }
  ]
}
```

The `language` field accepts `"kuery"` (KQL) or `"lucene"`. Filter index
references use the `indexRefName` convention, which must match entries in the
top-level `references` array.

### Dashboard Options

The `optionsJSON` field contains display preferences:

```json
{
  "useMargins": true,
  "syncColors": false,
  "syncCursor": true,
  "syncTooltips": false,
  "hidePanelTitles": false
}
```

### References Array

The `references` array extracts object relationships from panel configurations:

**Reference Naming Conventions**:

| Pattern | Usage | Example |
|---------|-------|---------|
| `panel_N` | By-reference panel linking to saved visualization | `panel_5` |
| `kibanaSavedObjectMeta.searchSourceJSON.index` | Dashboard's default data view | Main index pattern |
| `kibanaSavedObjectMeta.searchSourceJSON.filter[N].meta.index` | Filter data view references | Per-filter index |
| `{panelIndex}:indexpattern-datasource-layer-{layerId}` | Lens layer data view reference | `panel-uuid:indexpattern-datasource-layer-layer1` |
| `controlGroup_N:optionsListDataView` | Control group data views | Control filter index |

Example references:

```json
{
  "references": [
    {
      "type": "index-pattern",
      "id": "logs-*",
      "name": "kibanaSavedObjectMeta.searchSourceJSON.index"
    },
    {
      "type": "index-pattern",
      "id": "01d64a72-a702-4a41-8ba3-b87d45c40814",
      "name": "panel-uuid:indexpattern-datasource-layer-layer1"
    },
    {
      "type": "visualization",
      "id": "50643b60-3dd3-11e8-b2b9-5d5dc1715159",
      "name": "panel_5"
    }
  ]
}
```

## Panel Configuration

Panels represent individual visualizations within a dashboard. The grid system
uses a **48-column layout** where panels are positioned using `gridData`
coordinates.

### Panel Object Structure

Each panel in the `panelsJSON` array follows this structure:

```typescript
interface PanelState {
  version: string;          // Kibana version (e.g., "8.6.0")
  type: string;             // 'lens', 'visualization', 'map', 'search', 'links'
  panelIndex: string;       // UUID matching gridData.i
  panelRefName?: string;    // For by-reference: 'panel_{panelIndex}'
  title?: string;           // Custom panel title
  gridData: {
    x: number;              // 0-47 (48-column grid)
    y: number;              // 0+ (infinite rows)
    w: number;              // Width 1-48
    h: number;              // Height in row units
    i: string;              // Panel ID (must match panelIndex)
    row?: string;           // NEW in 9.x: parent section ID
  };
  embeddableConfig: {
    attributes?: object;    // By-value: full visualization state
    enhancements?: object;  // Drilldowns, actions
    hidePanelTitles?: boolean;
  };
}
```

### Grid Positioning Rules

- **x**: Horizontal position (0-47, max 48 columns total)
- **y**: Vertical position (rows from top, no maximum)
- **w**: Width in grid columns (1-48)
- **h**: Height in grid units (minimum varies by panel type)
- **i**: Unique identifier string (must match `panelIndex`)

**Common Layout Patterns**:

| Layout | Grid Configuration |
|--------|-------------------|
| Full width | `{"x":0,"y":0,"w":48,"h":8}` |
| Half width (left) | `{"x":0,"y":0,"w":24,"h":15}` |
| Half width (right) | `{"x":24,"y":0,"w":24,"h":15}` |
| Three columns | `w:16` at `x:0`, `x:16`, `x:32` |

### By-Reference vs By-Value Panels

This is the **most critical distinction** for compiler implementations.

#### By-Reference Panels

Link to separately saved visualization objects:

```json
{
  "type": "visualization",
  "gridData": {"x":0,"y":21,"w":24,"h":10,"i":"5"},
  "panelIndex": "5",
  "embeddableConfig": { "enhancements": {} },
  "panelRefName": "panel_5"
}
```

The `panelRefName` must match an entry in the dashboard's `references` array:

```json
{
  "type": "visualization",
  "id": "50643b60-3dd3-11e8-b2b9-5d5dc1715159",
  "name": "panel_5"
}
```

#### By-Value Panels (Recommended)

Embed the complete visualization inline:

```json
{
  "type": "lens",
  "gridData": {"x":0,"y":0,"w":24,"h":15,"i":"uuid-here"},
  "panelIndex": "uuid-here",
  "embeddableConfig": {
    "hidePanelTitles": false,
    "attributes": {
      "title": "",
      "visualizationType": "lnsXY",
      "type": "lens",
      "references": [
        {
          "type": "index-pattern",
          "id": "logs-*",
          "name": "indexpattern-datasource-layer-layer1"
        }
      ],
      "state": { /* Full Lens state */ }
    },
    "enhancements": {}
  }
}
```

**For YAML compilers targeting Lens, by-value panels are the recommended
approach** as they create self-contained dashboards that are easier to version
control and deploy.

### Panel Type Compatibility

| Panel Type | `type` Value | 8.x | 9.x | Recommended |
|-----------|--------------|-----|-----|-------------|
| Lens | `lens` | ✓ | ✓ | **Yes** |
| Legacy Viz | `visualization` | ✓ | Existing only | No |
| TSVB | `visualization` | ✓ | Existing only | No |
| Maps | `map` | ✓ | ✓ | Yes |
| Saved Search | `search` | ✓ | ✓ | Yes |
| Links | `links` | ✓ | ✓ | Yes |
| Collapsible Section | `section` | — | ✓ | Yes (9.x+) |
| Vega | `visualization` | ✓ | ✓ | Yes |

### Collapsible Sections (8.19+, 9.x)

Collapsible sections allow panels to be grouped into expandable/collapsible
rows:

```json
{
  "rows": {
    "section-1": {
      "id": "section-1",
      "title": "Section Title",
      "collapsed": false,
      "panels": {
        "panel-1": { "type": "lens", "gridData": {...} }
      }
    }
  },
  "panels": {
    "ungrouped-panel": { "type": "lens", "gridData": {...} }
  }
}
```

Key implications:
- Collapsed sections **lazy-load content**, improving performance
- The `gridData.row` property links panels to their parent section
- Uses custom CSS grid layout engine (`kbn-grid-layout`) replacing
  `react-grid-layout`

## Lens Visualization Architecture

Lens is Kibana's modern visualization editor and the primary target for new
dashboards. Its state object is complex but follows a consistent schema.

### Lens Attributes Structure

```json
{
  "title": "My Chart",
  "visualizationType": "lnsXY",
  "type": "lens",
  "references": [
    {
      "type": "index-pattern",
      "id": "01d64a72-a702-4a41-8ba3-b87d45c40814",
      "name": "indexpattern-datasource-layer-layer1"
    }
  ],
  "state": {
    "datasourceStates": {
      "formBased": {
        "layers": {
          "layer1": {
            "columns": { /* Column definitions */ },
            "columnOrder": ["col1", "col2"],
            "indexPatternId": "01d64a72-a702-4a41-8ba3-b87d45c40814"
          }
        }
      }
    },
    "visualization": { /* Visualization-specific config */ },
    "query": {"query": "", "language": "kuery"},
    "filters": []
  }
}
```

### Lens Visualization Types

| visualizationType | Description | Common Use Cases |
|-------------------|-------------|------------------|
| `lnsXY` | Line, area, bar charts | Time series, comparisons |
| `lnsPie` | Pie and donut charts | Proportions, distributions |
| `lnsMetric` | Single metric display | KPIs, counts |
| `lnsDatatable` | Data tables | Raw data, breakdowns |
| `lnsGauge` | Gauge visualizations | Progress, thresholds |
| `lnsHeatmap` | Heatmaps | Density, correlations |
| `lnsTagcloud` | Tag clouds | Word frequency |
| `lnsMosaic` | Mosaic charts | Multi-dimensional proportions |

### Lens Column Configuration

Columns define the data transformations (metrics and buckets):

```json
{
  "col1": {
    "dataType": "date",
    "isBucketed": true,
    "label": "@timestamp",
    "operationType": "date_histogram",
    "params": {"interval": "auto"},
    "sourceField": "@timestamp"
  },
  "col2": {
    "dataType": "number",
    "isBucketed": false,
    "label": "Count",
    "operationType": "count",
    "sourceField": "Records"
  }
}
```

**Operation types include**:
- **Metrics**: `count`, `sum`, `avg`, `max`, `min`, `cardinality`, `percentile`,
  `median`, `last_value`, `unique_count`
- **Buckets**: `date_histogram`, `terms`, `filters`, `range`
- **Advanced**: Formula-based operations

### Lens XY Visualization State

For `lnsXY` charts, the visualization state specifies how columns map to visual
elements:

```json
{
  "visualization": {
    "layers": [{
      "layerId": "layer1",
      "accessors": ["col2"],
      "xAccessor": "col1",
      "seriesType": "bar"
    }],
    "preferredSeriesType": "bar",
    "legend": {"isVisible": true, "position": "right"},
    "valueLabels": "hide"
  }
}
```

**Series types**: `bar`, `line`, `area`, `bar_stacked`, `bar_horizontal`,
`bar_horizontal_stacked`, `area_stacked`.

### Lens Datasources

Kibana 9.x introduces multiple datasource types:

| Datasource | State Key | Usage |
|------------|-----------|-------|
| Form-based | `formBased` | Standard aggregation-based queries |
| Text-based | `textBased` | ES\|QL queries (9.x+) |

**Form-based datasource** (most common):

```json
{
  "formBased": {
    "layers": {
      "layer1": {
        "columns": { /* column configurations */ },
        "columnOrder": ["col1", "col2"],
        "indexPatternId": "data-view-id"
      }
    }
  }
}
```

**Text-based datasource** (ES|QL):

```json
{
  "textBased": {
    "layers": {
      "layer1": {
        "query": {
          "esql": "FROM logs* | STATS count() BY @timestamp"
        },
        "columns": [...],
        "timeField": "@timestamp"
      }
    }
  }
}
```

## Advanced Features

### ES|QL Variable Controls (9.x+)

New control types enable dynamic dashboard filtering through ES|QL queries:

| Version | Naming |
|---------|--------|
| 9.0-9.1 | "ES\|QL controls" |
| 9.2+ | "Variable controls" |

Variable prefixes in ES|QL queries:
- `?variableName` — value variables (filter values)
- `??variableName` — field/function variables

```json
{
  "controlGroupInput": {
    "controls": [
      {
        "id": "esql-control-1",
        "type": "esqlControl",
        "variableName": "myVariable",
        "variableType": "value",
        "options": {
          "type": "query",
          "query": "FROM logs* | STATS count() BY field | LIMIT 100"
        }
      }
    ],
    "chainingSystem": "HIERARCHICAL",
    "labelPosition": "oneLine"
  }
}
```

### Drilldown Configuration

Panel drilldowns enable interactive navigation:

```json
{
  "embeddableConfig": {
    "enhancements": {
      "dynamicActions": {
        "events": [{
          "eventId": "drilldown-1",
          "triggers": ["VALUE_CLICK_TRIGGER"],
          "action": {
            "factoryId": "DASHBOARD_TO_DASHBOARD_DRILLDOWN",
            "name": "View Details",
            "config": {
              "dashboardId": "target-dashboard-id",
              "useCurrentFilters": true,
              "useCurrentDateRange": true
            }
          }
        }]
      }
    }
  }
}
```

**Trigger types**: `VALUE_CLICK_TRIGGER`, `RANGE_SELECT_TRIGGER`,
`ROW_CLICK_TRIGGER`.

## API Reference

### Saved Objects API Endpoints

The primary API for dashboard management:

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/api/saved_objects/_export` | Export dashboards (NDJSON) |
| `POST` | `/api/saved_objects/_import` | Import dashboards |
| `GET` | `/api/saved_objects/dashboard/{id}` | Retrieve single dashboard |
| `POST` | `/api/saved_objects/dashboard` | Create dashboard |
| `PUT` | `/api/saved_objects/dashboard/{id}` | Update dashboard |

**Space-aware endpoints** use the format: `/s/{space_id}/api/saved_objects/...`

### NDJSON Export Format

Kibana exports use Newline Delimited JSON, where each line is a complete saved
object:

```
{"id":"index-pattern-id","type":"index-pattern","attributes":{...}}
{"id":"dashboard-id","type":"dashboard","attributes":{...},"references":[...]}
```

**Export request body**:

```json
{
  "objects": [{"id": "dashboard-id", "type": "dashboard"}],
  "includeReferencesDeep": true,
  "excludeExportDetails": false
}
```

### Internal APIs Blocked in 9.0

**Critical 9.0 change**: Internal Kibana HTTP APIs now return `400 Bad Request`
when accessed without proper internal headers. This restriction is **enabled by
default** and affects undocumented `/api/*` and `/internal/*` routes.

Compilers should use only publicly documented APIs listed above.

Required headers for all API calls:

```
kbn-xsrf: true
Content-Type: application/json
```

### Deprecated/Removed APIs

| Removed API | Replacement |
|-------------|-------------|
| `GET /api/kibana/dashboards/export` | `POST /api/saved_objects/_export` |
| `POST /api/kibana/dashboards/import` | `POST /api/saved_objects/_import` |

## Complete Example: By-Value Lens Dashboard

```json
{
  "id": "my-dashboard",
  "type": "dashboard",
  "typeMigrationVersion": "8.9.0",
  "attributes": {
    "title": "Application Metrics",
    "version": 1,
    "timeRestore": true,
    "timeFrom": "now-24h",
    "timeTo": "now",
    "refreshInterval": {"pause": false, "value": 30000},
    "kibanaSavedObjectMeta": {
      "searchSourceJSON": "{\"query\":{\"query\":\"\",\"language\":\"kuery\"},\"filter\":[]}"
    },
    "optionsJSON": "{\"useMargins\":true,\"syncColors\":false,\"syncCursor\":true,\"syncTooltips\":false,\"hidePanelTitles\":false}",
    "panelsJSON": "[{\"type\":\"lens\",\"gridData\":{\"x\":0,\"y\":0,\"w\":24,\"h\":15,\"i\":\"panel1\"},\"panelIndex\":\"panel1\",\"embeddableConfig\":{\"attributes\":{\"title\":\"Request Count Over Time\",\"visualizationType\":\"lnsXY\",\"type\":\"lens\",\"references\":[{\"type\":\"index-pattern\",\"id\":\"logs-*\",\"name\":\"indexpattern-datasource-layer-layer1\"}],\"state\":{\"datasourceStates\":{\"formBased\":{\"layers\":{\"layer1\":{\"columns\":{\"col1\":{\"dataType\":\"date\",\"isBucketed\":true,\"label\":\"@timestamp\",\"operationType\":\"date_histogram\",\"params\":{\"interval\":\"auto\"},\"sourceField\":\"@timestamp\"},\"col2\":{\"dataType\":\"number\",\"isBucketed\":false,\"label\":\"Count\",\"operationType\":\"count\",\"sourceField\":\"Records\"}},\"columnOrder\":[\"col1\",\"col2\"]}}}},\"visualization\":{\"layers\":[{\"layerId\":\"layer1\",\"accessors\":[\"col2\"],\"xAccessor\":\"col1\",\"seriesType\":\"bar\"}],\"preferredSeriesType\":\"bar\",\"legend\":{\"isVisible\":true,\"position\":\"right\"}},\"query\":{\"query\":\"\",\"language\":\"kuery\"},\"filters\":[]}},\"enhancements\":{}}}]"
  },
  "references": [
    {
      "type": "index-pattern",
      "id": "logs-*",
      "name": "panel1:indexpattern-datasource-layer-layer1"
    }
  ]
}
```

## Compiler Implementation Guidelines

### Version Detection Strategy

Check `typeMigrationVersion` or response headers to determine target version:
- **8.x**: Use stringified JSON format with SavedObjects API
- **9.x**: Same stringified format works; new Dashboard API (when available)
  accepts destringified

### Output Generation for Dual Compatibility

For a YAML-to-Kibana compiler, the output generation process should:

1. **Stringify** `options` → `optionsJSON`
2. **Stringify** `panels` → `panelsJSON`
3. **Stringify** `searchSource` → `searchSourceJSON`
4. **Extract** panel references → `references` array
5. **Generate** unique UUIDs for `panelIndex` and `gridData.i` (must match)
6. **Include** `typeMigrationVersion` appropriate to target version
7. **Flatten** embedded Lens references to dashboard's top-level `references`
   array with proper naming

### Critical Implementation Details

1. **JSON Stringification**: The `panelsJSON`, `optionsJSON`, and
   `searchSourceJSON` fields must be properly escaped JSON strings within the
   final output.

2. **UUID Generation**: Each panel needs a unique identifier that appears in
   both `panelIndex` and `gridData.i`.

3. **Reference Extraction**: When generating by-value Lens panels, extract
   index pattern references from the embedded `attributes.references` and add
   them to the dashboard's top-level `references` array with the naming
   convention `{panelIndex}:indexpattern-datasource-layer-{layerId}`.

4. **Reference Naming**: Follow established naming patterns for different
   reference types (see "Reference Naming Conventions" section above).

5. **Target Lens Exclusively**: For future-proof compilation, generate only
   Lens visualizations (`lns*` types) as legacy visualization creation is
   disabled in 9.0 and scheduled for removal in 10.0.

### Future-Proofing Considerations

- **Prefer by-value panels** for self-contained, version-controllable dashboards
- **Target Lens exclusively** for long-term compatibility
- **Use formBased datasource** for standard aggregations
- **Consider textBased datasource** for ES|QL queries (9.x+)
- **Support collapsible sections** for improved organization (8.19+, 9.x)
- **Implement variable controls** for dynamic filtering (9.x+)

## Source Code References

For deeper implementation details, these Kibana repository paths contain
authoritative type definitions:

| Path | Contents |
|------|----------|
| `src/plugins/dashboard/common/types.ts` | Core dashboard TypeScript types |
| `src/plugins/dashboard/common/bwc/types.ts` | Backward compatibility types |
| `src/plugins/dashboard/common/saved_dashboard_references.ts` | Reference extraction/injection logic |
| `x-pack/platform/plugins/shared/lens/` | Lens plugin implementation |
| `src/plugins/embeddable/README.md` | Embeddable system documentation |
| `packages/core/saved-objects/` | Core saved object schemas |

## OpenAPI Specifications

Official Kibana API schemas are available at:
- **JSON**: `https://www.elastic.co/docs/api/doc/kibana.json`
- **YAML**: `https://www.elastic.co/docs/api/doc/kibana.yaml`

## Summary: Key Takeaways for AI Agents

When working with Kibana dashboard compilation:

1. **Understand the stringified JSON pattern** - Most complex data in
   `attributes` is stringified JSON
2. **Use by-value panels** - Embed full Lens configurations inline for
   self-contained dashboards
3. **Target Lens exclusively** - Legacy visualization types are deprecated and
   will be removed in Kibana 10.0
4. **Follow reference naming conventions** - Proper naming is critical for
   linking panels to data views
5. **Generate matching UUIDs** - `panelIndex` and `gridData.i` must match
6. **Respect the 48-column grid** - Use standard layout patterns for consistent
   positioning
7. **Use the Saved Objects API** - This is the primary interface for dashboard
   management
8. **Support version evolution** - Use `typeMigrationVersion` for compatibility
   tracking
9. **Consider collapsible sections** - Modern dashboards benefit from
   organizational features (8.19+, 9.x)
10. **Leverage ES|QL controls** - Variable controls enable dynamic filtering
    (9.x+)

This architecture reference provides the foundation for building robust
YAML-to-Kibana compilation tools that generate compatible, future-proof
dashboard configurations.
