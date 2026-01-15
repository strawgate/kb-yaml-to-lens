# Kibana New Dashboards API Comparison

This document compares Kibana's new Dashboards API (introduced in 9.x via
[PR #193067](https://github.com/elastic/kibana/pull/193067)) against our current
YAML config schema, analyzing alignment points and gaps.

## Executive Summary

**Overall Alignment: HIGH**

Our YAML config schema was already designed with similar principles to the new
Kibana API:

- Native arrays/objects instead of stringified JSON
- Semantic field naming (`name` → `title`, `settings` → `options`)
- Optional defaults pattern reducing boilerplate
- Flat, intuitive structure for end users

The new Kibana API validates our architectural approach. Supporting it as an
output format would require **low-to-medium effort** since our config layer
already operates with destringified structures internally.

**Key Finding:** The new API eliminates the painful stringified JSON fields
(`panelsJSON`, `optionsJSON`, `searchSourceJSON`) that our compiler currently
handles in the view layer. This structural change is exactly what our config
layer was designed to abstract away.

## API Overview

### Current Architecture (Saved Objects)

```
[Our YAML Config] → [Config Models] → [View Models] → [Stringified JSON/NDJSON]
                                            ↓
                            panelsJSON: "[{\"type\":\"lens\",...}]"
                            optionsJSON: "{\"useMargins\":true,...}"
```

### New Dashboards API (v3)

```
[Our YAML Config] → [Config Models] → [New API Transform] → [Native JSON]
                                            ↓
                            panels: [{type: "lens", ...}]
                            options: {use_margins: true, ...}
```

## Field Mapping Matrix

### Top-Level Dashboard Fields

| Our Config | New API | Current Saved Object | Mapping Type |
|------------|---------|---------------------|--------------|
| `name` | `title` | `attributes.title` | Semantic Match |
| `id` | `id` (request param) | `id` | Direct Match |
| `description` | `description` | `attributes.description` | Direct Match |
| `settings` | `options` | `attributes.optionsJSON` | Semantic Match |
| `query` | `query` | `kibanaSavedObjectMeta.searchSourceJSON.query` | Direct Match |
| `filters` | `filters` | `kibanaSavedObjectMeta.searchSourceJSON.filter` | Direct Match |
| `controls` | `control_group` | `attributes.controlGroupInput` | Structural Change |
| `panels` | `panels` | `attributes.panelsJSON` | Direct Match |
| `sample_data` | N/A | N/A | No Equivalent |
| N/A | `tags` | `attributes.tags` | No Equivalent (new) |
| N/A | `time_range` | `attributes.timeFrom/timeTo` | No Equivalent (new) |
| N/A | `refresh_interval` | `attributes.refreshInterval` | No Equivalent (new) |
| N/A | `access_control` | N/A | No Equivalent (new) |
| N/A | `pinned_panels` | N/A | No Equivalent (new) |

### Dashboard Settings → Options

| Our Config (`settings.*`) | New API (`options.*`) | Notes |
|---------------------------|----------------------|-------|
| `margins` | `use_margins` | Semantic match (snake_case) |
| `sync.cursor` | `sync_cursor` | Flattened, snake_case |
| `sync.tooltips` | `sync_tooltips` | Flattened, snake_case |
| `sync.colors` | `sync_colors` | Flattened, snake_case |
| `titles` | `hide_panel_titles` | Inverted boolean |
| `controls.position` | N/A | Moved to control_group |
| `controls.style` | N/A | Moved to control_group |
| `controls.chaining` | N/A | Moved to control_group |
| `controls.show_apply` | N/A | Moved to control_group |
| `layout_algorithm` | N/A | Compiler-only feature |
| N/A | `auto_apply_filters` | New field |

### Panel Structure

| Our Config (`panels[].*`) | New API (`panels[].*`) | Notes |
|--------------------------|------------------------|-------|
| `type` | `type` | Direct match |
| `title` | `config.title` | Nested in config |
| `position.x` | `grid.x` | Renamed container |
| `position.y` | `grid.y` | Renamed container |
| `position.w` | `grid.w` | Renamed container |
| `position.h` | `grid.h` | Renamed container |
| (auto-generated) | `uid` | Panel unique ID |
| `data_view` | `config.attributes.references` | Structural change |
| `primary`, `breakdown`, etc. | `config.attributes.state` | Lens-specific |
| N/A | `version` | Deprecated in new API |

### Control Structure

| Our Config (`controls[].*`) | New API (`control_group.controls[].*`) | Notes |
|-----------------------------|---------------------------------------|-------|
| `type` | `type` | Direct match |
| `field` | `control_config.field_name` | Renamed, nested |
| `data_view` | `control_config.data_view_id` | Renamed, nested |
| `title` | `control_config.title` | Nested |
| `search_technique` | `control_config.search_technique` | Nested |
| `width` | `width` | Direct match |
| `grow` | `grow` | Direct match |
| (auto-generated) | `order` | Position in array |

## Structural Differences

### 1. Stringified JSON Elimination

**Current (Saved Objects):**
```json
{
  "attributes": {
    "panelsJSON": "[{\"type\":\"lens\",\"gridData\":{\"x\":0,\"y\":0}}]",
    "optionsJSON": "{\"useMargins\":true}",
    "kibanaSavedObjectMeta": {
      "searchSourceJSON": "{\"query\":{\"language\":\"kuery\"}}"
    }
  }
}
```

**New API:**
```json
{
  "data": {
    "panels": [{"type": "lens", "grid": {"x": 0, "y": 0}}],
    "options": {"use_margins": true},
    "query": {"language": "kuery"},
    "filters": []
  }
}
```

**Impact:** Our view layer (`dashboard/view.py`, `panels/view.py`,
`controls/view.py`) contains `@field_serializer` decorators specifically for
stringification. A new output format would bypass these serializers.

### 2. Naming Convention Changes

The new API uses `snake_case` consistently:

| Current Saved Object | New API |
|---------------------|---------|
| `useMargins` | `use_margins` |
| `syncColors` | `sync_colors` |
| `hidePanelTitles` | `hide_panel_titles` |
| `gridData` | `grid` |
| `panelIndex` | `uid` |
| `embeddableConfig` | `config` |
| `dataViewId` | `data_view_id` |
| `fieldName` | `field_name` |

**Impact:** Our config layer already uses snake_case internally, but our view
layer uses camelCase for Kibana compatibility.

### 3. Reference Handling

**Current:** References extracted to top-level array with naming convention:
```json
{
  "references": [
    {"name": "panel-uuid:indexpattern-datasource-layer-layer1", "id": "logs-*"}
  ]
}
```

**New API:** References embedded within panel config (TBD - appears to maintain
similar structure but destringified).

### 4. Control Group Restructuring

**Current (Saved Object):**
```json
{
  "controlGroupInput": {
    "chainingSystem": "HIERARCHICAL",
    "controlStyle": "oneLine",
    "panelsJSON": "{\"uuid\":{\"type\":\"optionsListControl\",...}}"
  }
}
```

**New API:**
```json
{
  "control_group": {
    "chaining_strategy": "HIERARCHICAL",
    "label_position": "one_line",
    "controls": [{"type": "options_list", "control_config": {...}}]
  }
}
```

**Key Changes:**
- `panelsJSON` → `controls` (array, not stringified dict)
- `controlStyle` → `label_position`
- `explicitInput` → `control_config`
- Controls use array order instead of `order` field

### 5. Sections (New in 8.19+)

The new API introduces first-class section support:

```json
{
  "panels": [
    {"type": "lens", "grid": {...}, "config": {...}},
    {
      "title": "Section Title",
      "collapsed": false,
      "grid": {"y": 15},
      "panels": [...]
    }
  ]
}
```

**Impact:** We don't currently support collapsible sections in our config
schema.

## Alignment Points

### 1. Native Structure Approach

Our config layer was designed to provide a clean, semantic API that abstracts
away Kibana's stringified JSON complexity. The new API validates this approach
by offering the same abstraction at the HTTP layer.

**Our Config:**
```yaml
panels:
  - type: lens
    title: Request Count
    position: {x: 0, y: 0, w: 24, h: 15}
```

**New API (conceptually equivalent):**
```json
{"panels": [{"type": "lens", "config": {"title": "Request Count"}, "grid": {...}}]}
```

### 2. Optional Defaults Pattern

Both our config and the new API use sensible defaults to reduce boilerplate:

| Feature | Our Default | New API Default |
|---------|-------------|-----------------|
| Panel width | 24 | 24 |
| Panel height | 15 | 15 |
| Use margins | true | true |
| Sync cursor | true | true |
| Control chaining | HIERARCHICAL | HIERARCHICAL |

### 3. Flat Settings Structure

Our `settings` object provides flat access to dashboard options:

```yaml
settings:
  margins: true
  sync:
    cursor: true
    colors: false
```

The new API's `options` object is similarly flat (after destringification).

### 4. Panel Type Abstraction

Both systems abstract panel-specific configuration behind a common structure
with type-specific config.

## Gaps Identified

### Features in New API Not in Our Config

| Feature | Priority | Notes |
|---------|----------|-------|
| `tags` | Medium | Tag IDs for organization |
| `time_range` | Low | We rely on dashboard defaults |
| `refresh_interval` | Low | Runtime configuration |
| `access_control` | Medium | New access control features |
| `pinned_panels` | Low | Panel pinning state |
| Sections | Medium | Collapsible panel groups |

### Features in Our Config Not in New API

| Feature | Status | Notes |
|---------|--------|-------|
| `sample_data` | Compiler-only | Bundled test data generation |
| `layout_algorithm` | Compiler-only | Auto-positioning algorithm |
| High-level panel abstractions | Compiler-only | `LensPanel`, `primary`, `breakdown` |

## Implementation Recommendations

### Phase 1: Research Complete

This analysis provides the foundation for understanding the new API. Key
findings documented above.

### Phase 2: Output Format Support (Future)

To support the new API as an output format:

1. **Create new transform layer** (`api_v3_transform.py`)
   - Skip stringification serializers
   - Apply snake_case naming
   - Restructure control group

2. **Update panel compilation**
   - Change `gridData` → `grid`
   - Change `panelIndex` → `uid`
   - Change `embeddableConfig` → `config`

3. **Add new config fields** (optional)
   - `tags: list[str]`
   - `time_range: TimeRange`
   - `refresh_interval: RefreshInterval`
   - Section support for panels

**Estimated Effort:** Low-to-medium

- Core transform: 2-3 days
- Testing/validation: 1-2 days
- New features: As needed

### Phase 3: API Stabilization (Wait)

The new API is currently in Technical Preview status. Before full
implementation:

1. Monitor [Kibana releases](https://www.elastic.co/docs/release-notes/kibana)
   for GA announcement
2. Watch [Issue #174497](https://github.com/elastic/kibana/issues/174497) for
   updates
3. Track schema evolution via
   [Issue #230621](https://github.com/elastic/kibana/issues/230621)

## Conclusion

The new Kibana Dashboards API closely aligns with our existing config schema
design philosophy. Our abstraction layer already provides a similar clean
interface for users, with the compilation step handling the complexity of
Kibana's internal format.

**Key Takeaways:**

1. **Our architecture is validated** - The new API proves our approach was
   correct
2. **Low migration effort** - Internal structure already matches new API
   concepts
3. **Wait for GA** - Don't implement until API leaves Technical Preview
4. **Continue current output** - Stringified format remains compatible with
   both old and new Kibana versions

## Sources

- [Kibana Dashboards API Meta Issue #174497](https://github.com/elastic/kibana/issues/174497)
- [Dashboard API Implementation PR #193067](https://github.com/elastic/kibana/pull/193067)
- [Control Schema Rename Issue #194757](https://github.com/elastic/kibana/issues/194757)
- [Filters/Query Promotion Issue #230621](https://github.com/elastic/kibana/issues/230621)
- [Kibana API Documentation](https://www.elastic.co/docs/api/doc/kibana/)
- [Update Dashboard API (v9)](https://www.elastic.co/docs/api/doc/kibana/v9/operation/operation-put-dashboards-dashboard-id)
