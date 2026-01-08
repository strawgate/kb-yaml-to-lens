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

## Lens Tagcloud Charts

::: dashboard_compiler.panels.charts.tagcloud.config.LensTagcloudChart
    options:
      show_root_heading: false
      heading_level: 3

## ESQL Tagcloud Charts

::: dashboard_compiler.panels.charts.tagcloud.config.ESQLTagcloudChart
    options:
      show_root_heading: false
      heading_level: 3

## Tagcloud Appearance

::: dashboard_compiler.panels.charts.tagcloud.config.TagcloudAppearance
    options:
      show_root_heading: false
      heading_level: 3

### Orientation Options

The `orientation` field controls how tags are rotated in the cloud:

- **`single`**: All tags horizontal (0°) - cleanest, most readable
- **`right angled`**: Mix of horizontal (0°) and vertical (90°) orientations - classic word cloud style
- **`multiple`**: Multiple angles including diagonal - most artistic but potentially less readable

## Related

- [Base Panel Configuration](base.md)
- [Lens Panel Configuration](lens.md) (see sections on Dimensions and Metrics)
- [ESQL Panel Configuration](esql.md) (see section on ESQL Columns)
- [Dashboard Configuration](../dashboard/dashboard.md)
