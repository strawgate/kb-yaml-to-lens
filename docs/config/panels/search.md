# Search Panel

The `search` panel is used to embed a saved Kibana search into a dashboard.

```yaml
- panel:
    type: search
    # Common panel fields (id, title, description, grid, hide_title) also apply
    saved_search_id: string # (Required) The ID of the Kibana saved search object.
```

## Fields

*   `type` (required, string): Must be `search`.
*   `saved_search_id` (required, string): The unique identifier of the saved search object in Kibana that you want to embed.

## Example

```yaml
dashboard:
  title: Dashboard with Search
  panels:
    - panel:
        type: search
        grid: { x: 0, y: 0, w: 48, h: 20 }
        saved_search_id: my-saved-search-id