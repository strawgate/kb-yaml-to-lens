# Markdown Panel

The `markdown` panel is used to display content formatted using markdown. It corresponds to the "Text" visualization in Kibana.

```yaml
- panel:
    type: markdown
    # Common panel fields (id, title, description, grid, hide_title) also apply
    content: string       # (Required) The markdown content to display.
    font_size: integer    # (Optional) The font size for the content in pixels. Defaults to 12.
    links_in_new_tab: boolean # (Optional) If true, links will open in a new tab. Defaults to true.
```

## Fields

*   `type` (required, string): Must be `markdown`.
*   `content` (required, string): The markdown content to be rendered within the panel. You can use YAML multi-line string syntax (e.g., `|`) for readability with longer content.
*   `font_size` (optional, integer): The font size for the Markdown content, in pixels. Defaults to 12 if not set.
*   `links_in_new_tab` (optional, boolean): If true, links in the Markdown content will open in a new tab. Defaults to true if not set.

## Example

```yaml
dashboard:
  title: Dashboard with Markdown
  panels:
    - panel:
        type: markdown
        grid: { x: 0, y: 0, w: 24, h: 10 }
        title: Important Information
        content: |
          # Project Status

          - **Status:** In Progress
          - **Deadline:** End of Q3
        font_size: 14
        links_in_new_tab: false