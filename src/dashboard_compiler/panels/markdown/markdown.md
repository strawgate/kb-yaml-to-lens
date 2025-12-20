# Markdown Panel Configuration

The `markdown` panel type is used to display rich text content, formatted using Markdown syntax, directly on your dashboard. This is equivalent to the "Text" visualization in Kibana.

## Minimal Configuration Example

To add a simple Markdown panel, you need to specify its `type`, `grid` position, and the `content`.

```yaml
# Within a dashboard's 'panels' list:
# - type: markdown
#   title: "Welcome Note"
#   grid:
#     x: 0
#     y: 0
#     w: 12 # Full width
#     h: 3  # Height of 3 grid units
#   content: "## Welcome to the Dashboard!\nThis panel provides an overview."

# For a complete dashboard structure:
dashboard:
  name: "Dashboard with Markdown"
  panels:
    - type: markdown
      title: "Welcome Note"
      grid:
        x: 0
        y: 0
        w: 12
        h: 3
      content: |
        ## Welcome to the Dashboard!
        This panel provides an overview of the key metrics and reports available.

        - Item 1
        - Item 2
```

## Complex Configuration Example

This example demonstrates a Markdown panel with a custom font size and a setting for how links are opened.

```yaml
dashboard:
  name: "Informational Dashboard"
  panels:
    - type: markdown
      title: "Important Instructions & Links"
      description: "Follow these steps for system setup."
      grid:
        x: 0
        y: 0
        w: 8
        h: 5
      content: |
        # Setup Guide

        Please follow the [official documentation](https://example.com/docs) for detailed setup instructions.

        Key steps include:
        1.  **Download** the installer.
        2.  **Configure** the `config.yaml` file.
        3.  **Run** the start script.

        For issues, refer to the [Troubleshooting Page](https://example.com/troubleshooting).
      font_size: 14
      links_in_new_tab: false # Links will open in the same tab
```

## Full Configuration Options

Markdown panels inherit from the [Base Panel Configuration](../base.md) and have the following specific fields:

| YAML Key           | Data Type        | Description                                                                                                | Kibana Default                               | Required |
| ------------------ | ---------------- | ---------------------------------------------------------------------------------------------------------- | -------------------------------------------- | -------- |
| `type`             | `Literal['markdown']` | Specifies the panel type.                                                                                | `markdown`                                   | Yes      |
| `id`               | `string`         | A unique identifier for the panel. Inherited from BasePanel.                                               | Generated ID                                 | No       |
| `title`            | `string`         | The title displayed on the panel header. Inherited from BasePanel.                                         | `""` (empty string)                          | No       |
| `hide_title`       | `boolean`        | If `true`, the panel title will be hidden. Inherited from BasePanel.                                       | `false`                                      | No       |
| `description`      | `string`         | A brief description of the panel. Inherited from BasePanel.                                                | `""` (empty string, if `None`)               | No       |
| `grid`             | `Grid` object    | Defines the panel's position and size. Inherited from BasePanel. See [Grid Object Configuration](../base.md#grid-object-configuration). | N/A                                          | Yes      |
| `content`          | `string`         | The Markdown content to be displayed in the panel. You can use YAML multi-line string syntax (e.g., `|` or `>`) for readability. | N/A                                          | Yes      |
| `font_size`        | `integer`        | The font size for the Markdown content, in pixels.                                                         | `12`                                         | No       |
| `links_in_new_tab` | `boolean`        | If `true`, links in the Markdown content will open in a new tab.                                           | `true`                                       | No       |

## Related Documentation

*   [Base Panel Configuration](../base.md)
*   [Dashboard Configuration](../dashboard/dashboard.md)