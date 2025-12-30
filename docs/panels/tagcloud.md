# Tag Cloud Chart Panel Configuration

The Tag Cloud chart panel visualizes term frequency as a word cloud, where the size of each tag is proportional to its metric value. This is useful for showing the most common or significant terms in your data.

## A Poem for the Cloud Watchers

_For those who see meaning in the drift of words:_

```text
Up above the dashboard sky,
Word clouds float and drift on by.
Tags in sizes large and small—
The bigger the word, the more you've got of all.

From eighteen points to seventy-two,
Font sizes speak the gospel true.
Horizontal, vertical, angles wide,
Orientations far and wide!

Error messages like cumulus forms,
User agents weathering storms,
Kubernetes labels floating free,
Pod names adrift across the sea.

"single", "right angled", "multiple" ways
To orient your word displays.
So here's to those who like to see
Their data as vocabulary!
```

---

## Minimal Configuration Example (Lens)

```yaml
dashboards:
-
  name: "Log Analysis"
  panels:
    - type: charts
      title: "Top Error Messages"
      grid: { x: 0, y: 0, w: 48, h: 6 }
      chart:
        type: tagcloud
        data_view: "logs-*"
        tags:
          field: "error.message"
        metric:
          aggregation: count
```

## Minimal Configuration Example (ES|QL)

```yaml
dashboards:
-
  name: "Log Analysis"
  panels:
    - type: charts
      title: "Top Error Messages"
      grid: { x: 0, y: 0, w: 48, h: 6 }
      esql: "FROM logs-* | STATS count(*) BY error.message"
      chart:
        type: tagcloud
        tags:
          field: "error.message"
        metric:
          field: "count(*)"
```

## Full Configuration Options

### LensTagcloudChart

| YAML Key | Data Type | Description | Default | Required |
| ------------ | ------------------------ | ---------------------------------------------- | -------- | -------- |
| `type` | `Literal['tagcloud']` | Specifies the chart type. | tagcloud | Yes |
| `data_view` | `string` | The data view that determines the data source. | - | Yes |
| `tags` | `LensDimensionTypes` | The dimension for grouping (terms/tags). | - | Yes |
| `metric` | `LensMetricTypes` | The metric for sizing each tag. | - | Yes |
| `appearance` | `TagcloudAppearance` | Appearance settings (fonts, orientation). | None | No |
| `color` | `ColorMapping` | Color palette configuration. | None | No |

### ESQLTagcloudChart

| YAML Key | Data Type | Description | Default | Required |
| ------------ | ----------------------- | ------------------------------------------ | -------- | -------- |
| `type` | `Literal['tagcloud']` | Specifies the chart type. | tagcloud | Yes |
| `esql` | `string` | The ES\|QL query that determines the data. | - | Yes |
| `tags` | `ESQLDimensionTypes` | The dimension for grouping (terms/tags). | - | Yes |
| `metric` | `ESQLMetricTypes` | The metric for sizing each tag. | - | Yes |
| `appearance` | `TagcloudAppearance` | Appearance settings (fonts, orientation). | None | No |
| `color` | `ColorMapping` | Color palette configuration. | None | No |

### TagcloudAppearance

| YAML Key | Data Type | Description | Default | Required |
| --------------- | ------------------------- | -------------------------------- | ------- | -------- |
| `min_font_size` | `int` (1-100) | Minimum font size for tags. | 12 | No |
| `max_font_size` | `int` (1-200) | Maximum font size for tags. | 72 | No |
| `orientation` | `TagcloudOrientationEnum` | Text orientation configuration. | single | No |
| `show_label` | `boolean` | Toggle for label visibility. | true | No |

### TagcloudOrientationEnum

- `single`: Single horizontal orientation
- `right angled`: Mix of horizontal and vertical orientations
- `multiple`: Multiple angles

### ColorMapping

| YAML Key | Data Type | Description | Default | Required |
| --------- | --------- | ---------------------------------------- | ------- | -------- |
| `palette` | `string` | The palette to use for tag cloud colors. | default | No |

Common palette values include: `default`, `kibana_palette`, `eui_amsterdam_color_blind`, etc.

## Advanced Configuration Example

```yaml
dashboards:
-
  name: "Advanced Tag Cloud"
  panels:
    - type: charts
      title: "Kubernetes Pod Labels"
      grid: { x: 0, y: 0, w: 48, h: 8 }
      chart:
        type: tagcloud
        data_view: "k8s-*"
        tags:
          field: "kubernetes.labels.app"
        metric:
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
