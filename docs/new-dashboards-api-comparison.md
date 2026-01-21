# New Kibana Dashboards API Comparison

This document compares the new Kibana Dashboards API schema (as of late 2025) against
our current kb-yaml-to-lens config schema to assess alignment and estimate the effort
required to compile directly to the new API format.

## Executive Summary

**Overall Assessment: MODERATE-HIGH Alignment with Significant Architectural Differences**

The new Kibana API represents a fundamental restructuring of how dashboards and
visualizations are defined. Key characteristics:

| Aspect | Current Saved Objects | New Dashboards API |
| -------- | ----------------------- | -------------------- |
| Top-level structure | `{id, type, attributes, references}` | `{id, data, meta}` |
| JSON stringification | Extensive (`panelsJSON`, `optionsJSON`) | None - native objects |
| Panel embedding | By-value with `embeddableConfig.attributes` | `type` + `config.attributes` |
| Visualization definition | Inline in `state.datasourceStates` | Separate `/api/lens/visualizations/:id` endpoint |
| Filter structure | DSL-based with `meta` wrapper | Semantic `condition`/`group` structure |
| Controls | `controlGroupInput.panelsJSON` | `pinned_panels[]` array |

**Estimated Effort to Support New API**: **MEDIUM-HIGH**

The good news: Our config schema's philosophy (semantic naming, native objects, minimal
boilerplate) aligns well with the new API's design goals. The challenge: The visualization
schema is completely new and requires significant mapping work.

---

## Dashboard-Level Comparison

### Top-Level Field Mapping

| Our Config | New Kibana API | Current Saved Object | Notes |
| ------------ | ---------------- | ---------------------- | ------- |
| `name` | `data.title` | `attributes.title` | Direct mapping |
| `id` | `id` (at root) | `id` (at root) | Direct mapping |
| `description` | `data.description` | `attributes.description` | Direct mapping |
| `settings` | `data.options` | `attributes.optionsJSON` | Structural change |
| `query` | `data.query` | `attributes.kibanaSavedObjectMeta.searchSourceJSON.query` | Simplified |
| `filters` | `data.filters` | `attributes.kibanaSavedObjectMeta.searchSourceJSON.filter` | **Major change** |
| `controls` | `data.pinned_panels` | `attributes.controlGroupInput` | **Major change** |
| `panels` | `data.panels` | `attributes.panelsJSON` | Structure simplified |
| - | `data.time_range` | `attributes.timeFrom`/`attributes.timeTo` | Not in our schema |
| - | `data.refresh_interval` | `attributes.refreshInterval` | Not in our schema |
| - | `data.tags` | N/A | New feature |
| `sample_data` | N/A | N/A | Our extension |

### Settings/Options Mapping

| Our Config | New Kibana API | Current Saved Object |
| ------------ | ---------------- | ---------------------- |
| `settings.margins` | `options.use_margins` | `optionsJSON.useMargins` |
| `settings.sync.colors` | `options.sync_colors` | `optionsJSON.syncColors` |
| `settings.sync.cursor` | `options.sync_cursor` | `optionsJSON.syncCursor` |
| `settings.sync.tooltips` | `options.sync_tooltips` | `optionsJSON.syncTooltips` |
| `settings.titles` | `options.hide_panel_titles` (inverted) | `optionsJSON.hidePanelTitles` |
| `settings.layout_algorithm` | N/A | N/A |
| `settings.controls.*` | N/A (moved to pinned_panels) | `controlGroupInput.*` |

**Key Observation**: Our semantic naming (`sync.cursor`) vs new API's flat snake_case
(`sync_cursor`) requires simple key transformation.

---

## Filter Schema Comparison

This is one of the **most significant changes**. The new API introduces a completely
semantic filter schema.

### Current kb-yaml-to-lens Filter Schema

```yaml
filters:
  - field: "host.keyword"
    equals: "www.elastic.co"
  - field: "machine.os.keyword"
    in: ["linux", "windows"]
  - field: "@timestamp"
    gte: "now-1d"
    lte: "now"
  - and:
    - field: "status"
      equals: "error"
    - or:
      - field: "level"
        equals: "critical"
      - field: "level"
        equals: "high"
```

### New Kibana API Filter Schema

```json
{
  "filters": [
    {
      "data_view_id": "logsDataView",
      "condition": {
        "field": "host.keyword",
        "operator": "is",
        "value": "www.elastic.co"
      }
    },
    {
      "data_view_id": "logsDataView",
      "group": {
        "type": "AND",
        "conditions": [
          {"field": "status", "operator": "is", "value": "error"},
          {
            "type": "OR",
            "conditions": [
              {"field": "level", "operator": "is", "value": "critical"},
              {"field": "level", "operator": "is", "value": "high"}
            ]
          }
        ]
      }
    },
    {
      "disabled": true,
      "data_view_id": "logsDataView",
      "dsl": {"query": {"match": {"agent": {"query": "Mozilla"}}}}
    }
  ]
}
```

### Filter Mapping Analysis

| Our Filter Type | New API Equivalent | Complexity |
| ----------------- | -------------------- | ------------ |
| `PhraseFilter` (`equals`) | `condition.operator: "is"` | Low |
| `PhrasesFilter` (`in`) | Multiple conditions in group? | Medium |
| `RangeFilter` (`gte`/`lte`/`gt`/`lt`) | Not directly shown | Unknown |
| `ExistsFilter` | Not shown | Unknown |
| `CustomFilter` (`dsl`) | `dsl` field (direct) | Low |
| `AndFilter` | `group.type: "AND"` | Low |
| `OrFilter` | `group.type: "OR"` | Low |
| `NegateFilter` | Not shown | Unknown |

**Key Difference**: The new API requires `data_view_id` on each filter, which we
currently don't require (we use a default from the dashboard context).

---

## Panel Schema Comparison

### Panel Structure

| Our Config | New Kibana API | Current Saved Object |
| ------------ | ---------------- | ---------------------- |
| `name` | `config.title` | `embeddableConfig.title` |
| `description` | `config.description` | `embeddableConfig.description` |
| `id` | `uid` | `panelIndex` |
| `size.w` | `grid.w` | `gridData.w` |
| `size.h` | `grid.h` | `gridData.h` |
| `position.x` | `grid.x` | `gridData.x` |
| `position.y` | `grid.y` | `gridData.y` |
| Panel type | `type` | `type` |
| Visualization | `config.attributes` | `embeddableConfig.attributes` |

### Panel Type Mapping

| Our Panel Type | New API Type | Notes |
| ---------------- | -------------- | ------- |
| `LensPanel` | `type: "lens"` + `config.attributes` | Major restructuring |
| `ESQLPanel` | `type: "lens"` with ES|QL dataset | Same as above |
| `MarkdownPanel` | `type: "markdown"` | `config.attributes.content` |
| `SearchPanel` | `type: "search"` (by reference?) | Need to investigate |
| `LinksPanel` | `type: "links"` (by reference?) | Need to investigate |
| `ImagePanel` | `type: "image"` | Unknown schema |

---

## Visualization Schema Comparison (Lens)

This is the **most significant change**. The new API introduces a completely redesigned
visualization schema that is semantic and declarative rather than internal-format-based.

### Current Output: Lens State Object

Our current compiler outputs the internal Lens state format:

```json
{
  "visualizationType": "lnsMetric",
  "state": {
    "datasourceStates": {
      "formBased": {
        "layers": {
          "layer1": {
            "columns": {
              "col1": {
                "operationType": "count",
                "dataType": "number",
                "isBucketed": false,
                "sourceField": "Records"
              }
            },
            "columnOrder": ["col1"]
          }
        }
      }
    },
    "visualization": {
      "layerId": "layer1",
      "accessor": "col1"
    }
  }
}
```

### New API: Semantic Visualization Schema

```json
{
  "type": "metric",
  "dataset": {
    "type": "dataView",
    "id": "logs-*"
  },
  "metric": {
    "operation": "count",
    "label": "Total Requests",
    "format": {"type": "number", "decimals": 0}
  }
}
```

### Visualization Type Mapping

| Our Type | New API Type | Key Differences |
| ---------- | -------------- | ----------------- |
| `metric` | `type: "metric"` | `primary` → `metric`, `secondary` → `secondary_metric` |
| `gauge` | `type: "gauge"` | Similar structure, different naming |
| `pie` | `type: "pie" / "treemap" / "waffle" / "mosaic"` | Unified partition schema |
| `bar` | XY schema with `type: "bar"` | Completely different structure |
| `line` | XY schema with `type: "line"` | Completely different structure |
| `area` | XY schema with `type: "area"` | Completely different structure |
| `heatmap` | `type: "heatmap"` | Similar conceptually |
| `datatable` | `type: "table"` | Different field names |
| `tagcloud` | `type: "tagcloud"` | Similar structure |

### Metric Chart Deep Comparison

**Our Config:**
```yaml
lens:
  type: metric
  data_view: "logs-*"
  primary:
    aggregation: count
    label: "Total Requests"
  secondary:
    aggregation: average
    field: "response_time"
  breakdown:
    type: values
    field: "service.name"
```

**New API:**
```json
{
  "type": "metric",
  "dataset": {"type": "dataView", "id": "logs-*"},
  "metric": {
    "operation": "count",
    "label": "Total Requests",
    "format": {"type": "number"}
  },
  "secondary_metric": {
    "operation": "avg",
    "field": "response_time"
  },
  "breakdown_by": {
    "operation": "terms",
    "field": "service.name"
  }
}
```

**Alignment Assessment**: HIGH - Our semantic `primary`/`secondary`/`breakdown` maps
naturally to the new API's `metric`/`secondary_metric`/`breakdown_by`.

### XY Chart Deep Comparison

**Our Config:**
```yaml
lens:
  type: bar
  mode: stacked
  data_view: "logs-*"
  dimension:
    type: date_histogram
    field: "@timestamp"
  metrics:
    - aggregation: count
  breakdown:
    type: values
    field: "service.name"
```

**New API:**
```json
{
  "type": "xy",
  "layers": [{
    "type": "bar_stacked",
    "dataset": {"type": "dataView", "id": "logs-*"},
    "x": {"operation": "date_histogram", "field": "@timestamp"},
    "y": {"operation": "count"},
    "breakdown_by": {"operation": "terms", "field": "service.name"}
  }]
}
```

**Alignment Assessment**: MEDIUM - Conceptually similar but structural differences:
- Our `mode: stacked` becomes part of `type: "bar_stacked"`
- Our `dimension` → `x`
- Our `metrics` list → `y` (single or array?)
- New API uses a `layers` array even for simple charts

### ES|QL Dataset Support

**Our Config:**
```yaml
esql:
  type: metric
  query: "FROM logs-* | STATS count = COUNT(*)"
  primary:
    field: "count"
```

**New API:**
```json
{
  "type": "metric",
  "dataset": {
    "type": "esql",
    "query": "FROM logs-* | STATS count = COUNT(*)"
  },
  "metric": {
    "operation": "value",
    "column": "count"
  }
}
```

**Alignment Assessment**: HIGH - The new API's `dataset.type: "esql"` with `operation: "value"`
for referencing ES|QL columns is very similar to our approach.

---

## Controls/Pinned Panels Comparison

### Current kb-yaml-to-lens Controls

```yaml
controls:
  - type: options
    field: "host.keyword"
    data_view: "logs-*"
    preselected: ["www.elastic.co"]
    match_technique: prefix
  - type: range
    field: "bytes"
    data_view: "logs-*"
```

### New API Pinned Panels

```json
{
  "pinned_panels": [
    {
      "type": "optionsListControl",
      "size": "small",
      "grow": true,
      "config": {
        "data_view_id": "logsDataView",
        "field_name": "host.keyword",
        "selected_options": ["www.elastic.co"],
        "search_technique": "prefix",
        "sort": {"by": "_count", "direction": "desc"}
      }
    }
  ]
}
```

### Control Type Mapping

| Our Type | New API Type | Mapping Complexity |
| ---------- | -------------- | -------------------- |
| `options` | `optionsListControl` | Low |
| `range` | `rangeSliderControl` (assumed) | Low |
| `time` | `timeSliderControl` (assumed) | Low |
| `esql` | Unknown | High (needs research) |

**Key Differences:**
- New API uses `pinned_panels` at dashboard level (not nested in `controlGroupInput`)
- Control-specific config is in `config` object
- Size/grow options at panel level
- `data_view` → `data_view_id`, `field` → `field_name`

---

## Effort Assessment

### Phase 1: Foundation (Estimated: 2-3 weeks)

1. **New output target abstraction**
   - Create `OutputFormat` enum: `SAVED_OBJECTS` | `DASHBOARDS_API`
   - Abstract view layer to support both formats

2. **Dashboard-level compilation**
   - Map `name` → `data.title`
   - Map `settings` → `data.options`
   - Handle `data.time_range`, `data.refresh_interval`

3. **Simple panel compilation**
   - Grid positioning (minimal changes)
   - Markdown panels (simple)
   - Panel wrapper structure

### Phase 2: Filter System (Estimated: 1-2 weeks)

1. **Semantic filter transformation**
   - Map phrase → `condition.operator: "is"`
   - Map logical operators to `group.type`
   - Add `data_view_id` requirement (breaking change consideration)

2. **DSL fallback**
   - Preserve custom DSL filters
   - Handle unmapped filter types

### Phase 3: Visualization Schemas (Estimated: 4-6 weeks)

This is the bulk of the work - completely rewriting how we generate visualization configs.

1. **Metric charts** (1 week)
   - Map `primary` → `metric`
   - Map `secondary` → `secondary_metric`
   - Map `breakdown` → `breakdown_by`
   - Handle format specifications

2. **Partition charts** (1 week)
   - Unify pie/treemap/waffle/mosaic under partition schema
   - Map dimensions to `breakdown_by` array
   - Map metrics appropriately

3. **XY charts** (2 weeks)
   - Handle bar/line/area with layer structure
   - Map stacking modes to type variants
   - Support reference lines
   - Handle multi-layer charts

4. **Other charts** (1-2 weeks)
   - Gauge
   - Heatmap
   - Table
   - Tagcloud

### Phase 4: Controls (Estimated: 1 week)

1. **Map control types**
2. **Handle ES|QL controls** (may need new API research)

### Phase 5: Testing & Documentation (Estimated: 2 weeks)

1. **E2E tests with new API**
2. **Update documentation**
3. **Migration guide**

### Total Estimated Effort: 10-14 weeks

---

## Recommendations

### Short-term (Now)

1. **Continue with saved objects format** - It works with current Kibana versions
2. **Track API stability** - The new API is still evolving
3. **Design for abstraction** - Consider refactoring to make adding new output formats easier

### Medium-term (When API stabilizes)

1. **Add new output format option** - `--output-format=dashboards-api`
2. **Start with metric charts** - Highest alignment, good proof of concept
3. **Iterate on XY charts** - Most complex, plan carefully

### Long-term

1. **Consider deprecating saved objects output** - When Kibana 9+ adoption is high
2. **Leverage visualization API** - Store visualizations separately for reuse
3. **Add new capabilities** - Tags, refresh intervals, time restoration

---

## Compatibility Matrix

| Feature | Saved Objects | New Dashboards API |
| --------- | --------------- | -------------------- |
| Kibana 8.x | ✅ Full support | ❌ Not available |
| Kibana 9.x | ✅ Full support | ⚠️ Technical Preview |
| Kibana 10.x | ✅ Expected | ⚠️ Unknown |
| Direct import | ✅ NDJSON | ⚠️ API only |
| GitOps | ✅ File-based | ⚠️ API-based |
| Visualization reuse | ❌ By-value only | ✅ Separate viz API |

---

## Appendix: Schema Examples

### Complete Dashboard Comparison

<details>
<summary>Our YAML Config</summary>

```yaml
name: "Application Metrics"
description: "Key performance indicators for our application"
settings:
  margins: true
  sync:
    cursor: true
    tooltips: false
    colors: false
query:
  kuery: "service.name:frontend"
filters:
  - field: "environment"
    equals: "production"
controls:
  - type: options
    field: "host.keyword"
    data_view: "logs-*"
panels:
  - lens:
      type: metric
      data_view: "logs-*"
      primary:
        aggregation: count
    size:
      w: half
      h: 8
  - lens:
      type: bar
      data_view: "logs-*"
      dimension:
        type: date_histogram
        field: "@timestamp"
      metrics:
        - aggregation: count
    size:
      w: whole
      h: 15
```

</details>

<details>
<summary>New Kibana API Equivalent</summary>

```json
{
  "data": {
    "title": "Application Metrics",
    "description": "Key performance indicators for our application",
    "options": {
      "use_margins": true,
      "sync_cursor": true,
      "sync_tooltips": false,
      "sync_colors": false,
      "hide_panel_titles": false
    },
    "query": {
      "language": "kuery",
      "query": "service.name:frontend"
    },
    "filters": [
      {
        "data_view_id": "logs-*",
        "condition": {
          "field": "environment",
          "operator": "is",
          "value": "production"
        }
      }
    ],
    "pinned_panels": [
      {
        "type": "optionsListControl",
        "config": {
          "data_view_id": "logs-*",
          "field_name": "host.keyword"
        }
      }
    ],
    "panels": [
      {
        "type": "lens",
        "grid": {"x": 0, "y": 0, "w": 24, "h": 8},
        "config": {
          "attributes": {
            "type": "metric",
            "dataset": {"type": "dataView", "id": "logs-*"},
            "metric": {"operation": "count"}
          }
        }
      },
      {
        "type": "lens",
        "grid": {"x": 0, "y": 8, "w": 48, "h": 15},
        "config": {
          "attributes": {
            "type": "xy",
            "layers": [{
              "type": "bar",
              "dataset": {"type": "dataView", "id": "logs-*"},
              "x": {"operation": "date_histogram", "field": "@timestamp"},
              "y": {"operation": "count"}
            }]
          }
        }
      }
    ]
  }
}
```

</details>

---

## References

- [Kibana Issue #174497: Dashboard-as-Code API](https://github.com/elastic/kibana/issues/174497)
- [Kibana PR #193067: Public CRUD API MVP](https://github.com/elastic/kibana/pull/193067)
- User-provided schema documentation (late 2025)
