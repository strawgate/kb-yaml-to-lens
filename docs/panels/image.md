# Image Panel Configuration

The `image` panel type is used to display an image directly on your dashboard. This can be useful for branding, diagrams, or other visual elements.

## A Poem for the Visual Storytellers

_For those who know a picture is worth a thousand metrics:_

```text
Contain, cover, fill, or none—
Four ways to get the framing done.
Company logos, architecture maps,
System diagrams filling gaps.

When words and numbers just won't do,
A picture paints the broader view.
An SVG or PNG file
Can save a thousand words of toil.

From branding bold at dashboard's crown,
To network maps when things break down,
Your from_url pulls it through—
Background colors, alt text too.

So here's to images on the page,
Worth more than data can engage.
A visual anchor, tried and true,
That shows what numbers never knew.
```

---

## Minimal Configuration Example

To add an Image panel, you need to specify its `grid` position and the `image` configuration with `from_url` for the image source.

```yaml
dashboards:
  - name: "Branded Dashboard"
    panels:
      - title: "Company Logo"
        grid:
          x: 0
          y: 0
          w: 16
          h: 3
        image:
          from_url: "https://example.com/path/to/your/logo.png"
```

## Complex Configuration Example

This example demonstrates an Image panel with specific `fit` behavior, alternative text for accessibility, and a background color.

```yaml
dashboards:
  - name: "Dashboard with Informative Image"
    panels:
      - title: "System Architecture Diagram"
        description: "Overview of the system components and their interactions." # Alt text
        grid:
          x: 0
          y: 0
          w: 48 # Full width
          h: 6
        image:
          from_url: "https://example.com/path/to/architecture.svg"
          fit: "contain"  # Ensure the whole image is visible within the panel
          background_color: "#f0f0f0" # Light grey background
```

## Full Configuration Options

Image panels inherit from the [Base Panel Configuration](./base.md) and have the following specific fields:

| YAML Key | Data Type | Description | Kibana Default | Required |
| ------------------ | ------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ------------------------------- | -------- |
| `id` | `string` | A unique identifier for the panel. Inherited from BasePanel. | Generated ID | No |
| `title` | `string` | The title displayed on the panel header. Inherited from BasePanel. | `""` (empty string) | No |
| `hide_title` | `boolean` | If `true`, the panel title will be hidden. Inherited from BasePanel. | `false` | No |
| `description` | `string` | Alternative text for the image, used for accessibility. This overrides the BasePanel `description` if you want specific alt text for the image itself. | `""` (empty string, if `None`) | No |
| `grid` | `Grid` object | Defines the panel's position and size. Inherited from BasePanel. See [Grid Object Configuration](./base.md#grid-object-configuration). | N/A | Yes |
| `image` | `Image` object | Configuration for the image panel. | N/A | Yes |

**Image Object Configuration:**

| YAML Key | Data Type | Description | Kibana Default | Required |
| ------------------ | ------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ------------------------------- | -------- |
| `from_url` | `string` | The URL of the image to be displayed in the panel. | N/A | Yes |
| `fit` | `Literal['contain', 'cover', 'fill', 'none']` | The sizing of the image within the panel boundaries. | `contain` | No |
| `background_color` | `string` | Background color for the image panel (e.g., hex code like `#FFFFFF` or color name like `transparent`). | `""` (empty string, likely transparent in Kibana) | No |

**Details for `fit` options:**

* `contain`: (Default) Scales the image to fit within the panel while maintaining its aspect ratio. The entire image will be visible.
* `cover`: Scales the image to fill the panel while maintaining its aspect ratio. Some parts of the image may be cropped to achieve this.
* `fill`: Stretches or compresses the image to fill the panel completely, potentially altering its original aspect ratio.
* `none`: Displays the image at its original size. If the image is larger than the panel, it will be cropped. If smaller, it will sit within the panel, respecting its original dimensions.

## Programmatic Usage (Python)

You can create Image panels programmatically using Python:

```python
from dashboard_compiler.panels.config import Grid
from dashboard_compiler.panels.images.config import ImagePanel, ImagePanelConfig

panel = ImagePanel(
    grid=Grid(x=0, y=0, w=24, h=20),
    image=ImagePanelConfig(
        from_url='https://example.com/logo.png',
    ),
)
```

## Related Documentation

* [Base Panel Configuration](./base.md)
* [Dashboard Configuration](../dashboard/dashboard.md)
