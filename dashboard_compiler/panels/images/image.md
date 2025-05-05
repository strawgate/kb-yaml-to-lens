# Image Panel

The `image` panel is used to display images on the dashboard.

```yaml
- panel:
    type: image
    # Common panel fields (id, title, description, grid, hide_title) also apply
    from_url: string      # (Required) The URL of the image to be displayed.
    fit: string           # (Optional) The sizing of the image (contain, cover, fill, none). Defaults to "contain".
    description: string   # (Optional) Alternative text for the image. Defaults to "".
    background_color: string # (Optional) Background color for the image panel. Defaults to "".
```

## Fields

*   `type` (required, string): Must be `image`.
*   `from_url` (required, string): The URL of the image to be displayed in the panel.
*   `fit` (optional, string): The sizing of the image within the panel. Valid values are `contain`, `cover`, `fill`, or `none`. Defaults to `contain`.
*   `description` (optional, string): Alternative text for the image, used for accessibility. Defaults to an empty string if not set.
*   `background_color` (optional, string): Background color for the image panel. Defaults to an empty string if not set.

## Example

```yaml
dashboard:
  title: Dashboard with Image
  panels:
    - panel:
        type: image
        grid: { x: 0, y: 0, w: 12, h: 10 }
        title: Company Logo
        from_url: https://example.com/logo.png
        fit: contain
        description: The company logo
        background_color: "#FFFFFF"