# Tag Cloud Chart Panel Configuration

The Tag Cloud chart panel visualizes term frequency as a word cloud, where the size of each tag is proportional to its metric value. This is useful for showing the most common or significant terms in your data.

## A Poem for the Cloud Watchers

_For those who see meaning in the drift of words:_

```text
Up above the dashboard sky,
Word clouds float and drift on by.
Tags in sizes large and small—
The bigger the word, the higher the fall.

From eighteen points to seventy-two,
Font sizes speak the gospel true.
Horizontal, vertical, angles wide,
Orientations multiply!

Error messages like cumulus forms,
User agents weathering storms,
Kubernetes labels floating free,
Pod names adrift across the sea.

"single", "right angled", "multiple" ways
To orient your word displays.
So here's to those who like to see
Their data in words, big and free!
```

---

## Minimal Configuration Example (Lens)

```yaml
dashboards:
- name: "Log Analysis"
  panels:
    - title: "Top Error Messages"
      grid: { x: 0, y: 0, w: 48, h: 6 }
      lens:
        type: tagcloud
        data_view: "logs-*"
        tags:
          type: values
          field: "error.message"
        metrics:
          aggregation: count
```

## Minimal Configuration Example (ES|QL)

```yaml
dashboards:
- name: "Log Analysis"
  panels:
    - title: "Top Error Messages"
      grid: { x: 0, y: 0, w: 48, h: 6 }
      esql:
        type: tagcloud
        query: "FROM logs-* | STATS error_count = count(*) BY error.message"
        tags:
          field: "error.message"
        metrics:
          field: "error_count"
```

## Full Configuration Options

### LensTagcloudChart

| YAML Key | Data Type | Description | Default | Required |
| ------------ | ------------------------ | ---------------------------------------------- | -------- | -------- |
| `type` | `Literal['tagcloud']` | Specifies the chart type. | tagcloud | Yes |
| `data_view` | `string` | The data view that determines the data source. | - | Yes |
| `tags` | `LensDimensionTypes` | The dimension for grouping (terms/tags). | - | Yes |
| `metrics` | `LensMetricTypes` | The metric for sizing each tag. | - | Yes |
| `appearance` | `TagcloudAppearance \| None` | Appearance settings (fonts, orientation). See [TagcloudAppearance Options](#tagcloudappearance-options) below. | None | No |
| `color` | `ColorMapping \| None` | Color palette configuration. See [Color Mapping Configuration](base.md#color-mapping-configuration). | None | No |

### ESQLTagcloudChart

| YAML Key | Data Type | Description | Default | Required |
| ------------ | ----------------------- | ------------------------------------------ | -------- | -------- |
| `type` | `Literal['tagcloud']` | Specifies the chart type. | tagcloud | Yes |
| `esql` | `string` | The ES\|QL query that determines the data. | - | Yes |
| `tags` | `ESQLDimensionTypes` | The dimension for grouping (terms/tags). | - | Yes |
| `metrics` | `ESQLMetricTypes` | The metric for sizing each tag. | - | Yes |
| `appearance` | `TagcloudAppearance \| None` | Appearance settings (fonts, orientation). See [TagcloudAppearance Options](#tagcloudappearance-options) below. | None | No |
| `color` | `ColorMapping \| None` | Color palette configuration. See [Color Mapping Configuration](base.md#color-mapping-configuration). | None | No |

### TagcloudAppearance Options

Controls the visual appearance of tags in the cloud.

| YAML Key | Data Type | Description | Default | Required |
| --------------- | ------------------------- | -------------------------------- | ------- | -------- |
| `min_font_size` | `int` (1-100) | Minimum font size for tags (in points). Smaller tags represent lower metric values. | 12 | No |
| `max_font_size` | `int` (1-200) | Maximum font size for tags (in points). Larger tags represent higher metric values. | 72 | No |
| `orientation` | `TagcloudOrientationEnum` | Text orientation configuration. Controls how tags are rotated in the cloud. | single | No |
| `show_label` | `boolean` | Toggle for label visibility. When false, hides the legend/labels. | true | No |

#### Orientation Options

The `orientation` field controls how tags are rotated in the cloud:

- **`single`**: All tags horizontal (0°) - cleanest, most readable
- **`right angled`**: Mix of horizontal (0°) and vertical (90°) orientations - classic word cloud style
- **`multiple`**: Multiple angles including diagonal - most artistic but potentially less readable

**Example:**

```yaml
appearance:
  min_font_size: 18        # Smallest tag size (18pt) - lower values have smaller visual impact
  max_font_size: 96        # Largest tag size (96pt) - higher values have greater visual impact
  orientation: "multiple"  # Multiple angles (most artistic but less readable than "single" or "right angled")
  show_label: false        # Hide legend/labels
```

## Advanced Configuration Example

```yaml
dashboards:
- name: "Advanced Tag Cloud"
  panels:
    - title: "Service Labels"
      grid: { x: 0, y: 0, w: 48, h: 8 }
      lens:
        type: tagcloud
        data_view: "logs-*"
        tags:
          type: values
          field: "service.name"
        metrics:
          aggregation: count
        appearance:
          min_font_size: 12
          max_font_size: 96
          orientation: "multiple"
          show_label: false
        color:
          palette: "kibana_palette"
```

## Related

- [Base Panel Configuration](base.md)
- [Lens Panel Configuration](lens.md) (see sections on Dimensions and Metrics)
- [ESQL Panel Configuration](esql.md) (see section on ESQL Columns)
- [Dashboard Configuration](../dashboard/dashboard.md)
