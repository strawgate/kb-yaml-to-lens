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
| --------- | ------------- | --------------------- |
| **7.x** | Introduced modern `gridData` format, Lens visualizations | Foundation for current architecture |
| **8.0** | Globally unique IDs across spaces, removed legacy import API | Must use Saved Objects API |
| **8.8+** | Index splitting (`.kibana` → multiple indices) | Transparent to API users |
| **8.10+** | Model versions replace legacy migrations | New version tracking system |
| **8.19+** | Collapsible sections, custom grid layout | New panel grouping mechanism |
| **9.0** | Disabled creation of legacy viz types, internal API restrictions | Must target Lens exclusively |
| **9.0+** | ES\|QL variable controls, Content Management v3 schema | New filter/query capabilities |
| **9.x** | Dashboard CRUD API (Technical Preview), destringified JSON | New API option (preview) |
| **10.0** | Full removal of TSVB, aggregation-based, Timelion | Complete deprecation |

### Migration from 8.x to 9.x

The core dashboard JSON structure remains backward compatible between 8.x and
9.x. Key differences:

#### Content Management v3 API (9.x)

The new API layer destringifies JSON for easier programmatic access:

| Storage Field | v3 API Field | Compiler Target |
| -------------- | -------------- | ----------------- |
| `panelsJSON` (string) | `panels` (array) | Use stringified format |
| `optionsJSON` (string) | `options` (object) | Use stringified format |
| `searchSourceJSON` (string) | `searchSource` (object) | Use stringified format |
| `controlGroupInput.panelsJSON` (dict) | `controlGroupInput.controls` (array) | Use stringified format |

**Recommendation**: Compilers should output the stringified format for maximum
compatibility with both direct saved object operations and older Kibana
versions.

##### New Dashboard CRUD API (Technical Preview)

As of Kibana 9.x, a dedicated Dashboard API is available in Technical Preview
([Issue #174497](https://github.com/elastic/kibana/issues/174497), implemented in
[PR #193067](https://github.com/elastic/kibana/pull/193067)):

```
POST   /api/dashboards/dashboard           (create)
POST   /api/dashboards/dashboard/{id}      (create with ID)
GET    /api/dashboards/dashboard/{id}      (retrieve)
GET    /api/dashboards/dashboard           (list/paginated)
PUT    /api/dashboards/dashboard/{id}      (update)
DELETE /api/dashboards/dashboard/{id}      (delete)
```

All endpoints require the header: `elastic-api-version: 2023-10-31`

The new API accepts native JSON objects instead of stringified JSON, improving
readability for version control and programmatic management:

**v2 (Legacy Saved Objects format)**:
```json
{
  "attributes": {
    "panelsJSON": "[{\"type\":\"lens\",...}]",
    "optionsJSON": "{\"useMargins\":true,...}",
    "controlGroupInput": {
      "panelsJSON": "{\"ctrl-id\":{\"type\":\"optionsListControl\",...}}"
    }
  }
}
```

**v3 (New Dashboard API format)**:
```json
{
  "attributes": {
    "panels": [{"type": "lens", ...}],
    "options": {"useMargins": true, ...},
    "controlGroupInput": {
      "controls": [{"id": "ctrl-id", "type": "optionsListControl", ...}]
    }
  }
}
```

The Content Management layer handles bidirectional transformation:
- **Read operations**: Parses stringified JSON from storage into native objects
- **Write operations**: Serializes native objects to stringified JSON for storage

This architecture maintains backward compatibility with existing saved objects
while exposing a cleaner API surface.

#### Model Versions System

After Kibana 8.10.0, the legacy `migrations` property is deprecated. The new
`modelVersions` system uses consecutive integers (1, 2, 3...) decoupled from
Kibana release versions.

Version field changes:

| Field | Status | Usage |
| ------- | -------- | ------- |
| `migrationVersion` (map) | Being phased out | Legacy version tracking |
| `typeMigrationVersion` | Current standard | Primary version field |
| `coreMigrationVersion` | Active | Tracks core Kibana version |

#### Legacy Visualization Deprecations

| Visualization Type | 9.x Status | Full Removal |
| ------------------- | ------------ | -------------- |
| **TSVB** | Creation disabled, existing work | 10.0 |
| **Aggregation-based** | Creation disabled, existing work | 10.0 |
| **Timelion (viz)** | Creation disabled, existing work | 10.0 |
| **Vega** | Fully supported | No removal planned |
| **Logs Stream panel** | **REMOVED** | 9.0 |
| **Legacy Input Controls** | Hidden by default | TBD |

**Critical for compilers**: Target Lens (`lns*` visualization types) as the
primary output format since legacy visualization creation is disabled in 9.0
and scheduled for full removal in 10.0.

## kb-yaml-to-lens Config Schema vs Kibana v3 API Comparison

This section compares the kb-yaml-to-lens YAML config schema to Kibana's new v3
Dashboard API schema. Both schemas prioritize developer experience with native
objects and semantic naming.

### Top-Level Field Mapping

| kb-yaml-to-lens Config | Kibana v3 API | Saved Object Storage | Notes |
| ----------------------- | -------------- | --------------------- | ------ |
| `name` | `title` | `attributes.title` | Direct semantic match |
| `id` | `id` | `id` | Direct match |
| `description` | `description` | `attributes.description` | Direct match |
| `settings` | `options` | `attributes.optionsJSON` | Structural match (nested vs flat) |
| `query` | `searchSource.query` | `kibanaSavedObjectMeta.searchSourceJSON.query` | Direct match |
| `filters` | `searchSource.filter` | `kibanaSavedObjectMeta.searchSourceJSON.filter` | Direct match |
| `controls` | `controlGroupInput.controls` | `attributes.controlGroupInput.panelsJSON` | Array structure aligned |
| `panels` | `panels` | `attributes.panelsJSON` | Native array in both |
| `sample_data` | — | — | kb-yaml-to-lens only |
| — | `timeRestore` | `attributes.timeRestore` | Not in config schema |
| — | `timeFrom`/`timeTo` | `attributes.timeFrom`/`timeTo` | Not in config schema |
| — | `refreshInterval` | `attributes.refreshInterval` | Not in config schema |
| — | `tags` | — | New v3 API feature |
| — | `spaces` | — | Multi-space support |

### Settings / Options Mapping

| kb-yaml-to-lens Config | Kibana v3 API | Notes |
| ----------------------- | -------------- | ------ |
| `settings.margins` | `options.useMargins` | Boolean, same semantics |
| `settings.sync.colors` | `options.syncColors` | Boolean, same semantics |
| `settings.sync.cursor` | `options.syncCursor` | Boolean, same semantics |
| `settings.sync.tooltips` | `options.syncTooltips` | Boolean, same semantics |
| `settings.titles` | `options.hidePanelTitles` | Inverted boolean (show vs hide) |
| `settings.layout_algorithm` | — | kb-yaml-to-lens only (auto-layout) |
| `settings.controls.label_position` | `controlGroupInput.labelPosition` | `inline`/`above` vs `oneLine`/`twoLine` |
| `settings.controls.chain_controls` | `controlGroupInput.chainingSystem` | Boolean vs enum (`HIERARCHICAL`/`NONE`) |
| `settings.controls.click_to_apply` | `controlGroupInput.autoApplySelections` | Inverted boolean |
| `settings.controls.apply_global_filters` | `controlGroupInput.ignoreParentSettings.ignoreFilters` | Inverted boolean |
| `settings.controls.apply_global_timerange` | `controlGroupInput.ignoreParentSettings.ignoreTimerange` | Inverted boolean |

### Control Types Mapping

| kb-yaml-to-lens Config | Kibana v3 API Type | Notes |
| ----------------------- | ------------------- | ------ |
| `type: options` | `optionsListControl` | Options list control |
| `type: range` | `rangeSliderControl` | Range slider control |
| `type: time` | `timeSlider` | Time slider control |
| `type: esql` | `esqlControl` | ES\|QL variable control |

**Control Structure Comparison**:

kb-yaml-to-lens config:
```yaml
controls:
  - type: options
    field: host.name
    data_view: logs-*
    width: medium
    preselected: ["server-1"]
```

Kibana v3 API format:
```json
{
  "controlGroupInput": {
    "controls": [{
      "id": "ctrl-uuid",
      "type": "optionsListControl",
      "order": 0,
      "width": "medium",
      "grow": false,
      "controlConfig": {
        "fieldName": "host.name",
        "dataViewId": "logs-*",
        "selectedOptions": ["server-1"]
      }
    }]
  }
}
```

### Panel Structure Mapping

| kb-yaml-to-lens Config | Kibana v3 API | Notes |
| ----------------------- | -------------- | ------ |
| Panel type discriminator | `type` field | Direct match |
| `position.x`, `position.y`, etc. | `gridData.x`, `gridData.y`, etc. | Direct match |
| Lens config fields | `panelConfig.attributes.state` | Nested in panel config |
| `title` | `panelConfig.title` | Direct match |
| `data_view` | Reference in `panelConfig.attributes.references` | Extracted to references |

### Alignment Assessment

**High Alignment Areas**:
- Native array/object structures (not stringified JSON in config layer)
- Semantic field naming patterns
- Panel positioning grid system (48-column)
- Control types and configurations
- By-value panel embedding approach

**Gaps to Address for Full v3 API Support**:
1. Time restoration settings (`timeRestore`, `timeFrom`, `timeTo`)
2. Auto-refresh interval (`refreshInterval`)
3. Tags support for dashboard organization
4. Multi-space deployment (`spaces`)
5. Control structure transformation (array with explicit `id` and `order` fields)

**Effort Assessment**: LOW-MEDIUM

Adding a new output target for the v3 Dashboard API would require:
1. New serializer that outputs native objects (instead of stringified JSON)
2. Transform controls from config format to v3 array format with explicit IDs
3. Add optional time/refresh fields to config schema
4. Minor field name mappings (e.g., `name` → `title`)

The core architecture already aligns well with the v3 API's design philosophy.

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
| ------- | ------ | ------------- | ---------- |
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
| --------- | ------- | --------- |
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
| -------- | ------------------- |
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
| ----------- | -------------- | ----- | ----- | ------------- |
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
| ------------------- | ------------- | ------------------ |
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
| ------------ | ----------- | ------- |
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
| --------- | -------- |
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

### Dashboard API Endpoints (Technical Preview, 9.x+)

The new dedicated Dashboard API provides cleaner CRUD operations with native
JSON objects (see [Issue #174497](https://github.com/elastic/kibana/issues/174497)):

| Method | Endpoint | Purpose |
| -------- | ---------- | --------- |
| `POST` | `/api/dashboards/dashboard` | Create dashboard |
| `POST` | `/api/dashboards/dashboard/{id}` | Create dashboard with specific ID |
| `GET` | `/api/dashboards/dashboard/{id}` | Retrieve dashboard |
| `GET` | `/api/dashboards/dashboard` | List dashboards (paginated) |
| `PUT` | `/api/dashboards/dashboard/{id}` | Update dashboard |
| `DELETE` | `/api/dashboards/dashboard/{id}` | Delete dashboard |

**Required headers**:
```text
elastic-api-version: 2023-10-31
kbn-xsrf: true
Content-Type: application/json
```

**Status**: Technical Preview - schema may change before GA.

### Saved Objects API Endpoints

The primary API for dashboard management (stable, works with all Kibana versions):

| Method | Endpoint | Purpose |
| -------- | ---------- | --------- |
| `POST` | `/api/saved_objects/_export` | Export dashboards (NDJSON) |
| `POST` | `/api/saved_objects/_import` | Import dashboards |
| `GET` | `/api/saved_objects/dashboard/{id}` | Retrieve single dashboard |
| `POST` | `/api/saved_objects/dashboard` | Create dashboard |
| `PUT` | `/api/saved_objects/dashboard/{id}` | Update dashboard |

**Space-aware endpoints** use the format: `/s/{space_id}/api/saved_objects/...`

### NDJSON Export Format

Kibana exports use Newline Delimited JSON, where each line is a complete saved
object:

```json
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

```text
kbn-xsrf: true
Content-Type: application/json
```

### Deprecated/Removed APIs

| Removed API | Replacement |
| ------------- | ------------- |
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
| ------ | ---------- |
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
   `attributes` is stringified JSON (for Saved Objects API)
2. **Use by-value panels** - Embed full Lens configurations inline for
   self-contained dashboards
3. **Target Lens exclusively** - Legacy visualization types are deprecated and
   will be removed in Kibana 10.0
4. **Follow reference naming conventions** - Proper naming is critical for
   linking panels to data views
5. **Generate matching UUIDs** - `panelIndex` and `gridData.i` must match
6. **Respect the 48-column grid** - Use standard layout patterns for consistent
   positioning
7. **Choose the right API**:
   - **Saved Objects API** - Stable, works with all Kibana versions, uses
     stringified JSON
   - **Dashboard API** (9.x+, Technical Preview) - Cleaner native JSON, but
     schema may change
8. **Support version evolution** - Use `typeMigrationVersion` for compatibility
   tracking
9. **Consider collapsible sections** - Modern dashboards benefit from
   organizational features (8.19+, 9.x)
10. **Leverage ES|QL controls** - Variable controls enable dynamic filtering
    (9.x+)
11. **Monitor v3 API evolution** - The new Dashboard API
    ([#174497](https://github.com/elastic/kibana/issues/174497)) uses native
    objects instead of stringified JSON, aligning well with kb-yaml-to-lens
    architecture

This architecture reference provides the foundation for building robust
YAML-to-Kibana compilation tools that generate compatible, future-proof
dashboard configurations.
