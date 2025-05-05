# Search Panel

The `search` panel is used to display the results of a saved Kibana search.

```yaml
- panel:
    type: search
    # Common panel fields (id, title, description, grid, hide_title) also apply
    saved_search_id: string # (Required) The ID of the saved Kibana search object.
```

## Fields

*   `type` (required, string): Must be `search`.
*   `saved_search_id` (required, string): The ID of the saved Kibana search object to display in the panel.

## Example

```yaml
dashboard:
  title: Dashboard with Search Results
  panels:
    - panel:
        type: search
        grid: { x: 0, y: 0, w: 24, h: 10 }
        title: Recent Errors
        saved_search_id: my-saved-error-search-id
```

## Related Documentation

*   [Base Panel Object](../base.md)