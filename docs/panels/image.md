# Image Panel Configuration

The `image` panel type is used to display an image directly on your dashboard. This can be useful for branding, diagrams, or other visual elements.

## A Poem for the Visual Storytellers

_For those who know a picture is worth a thousand metrics:_

```text
When words and numbers just won't do,
A picture paints the broader view.
An SVG or PNG so fine
Can speak a thousand words in line.

Contain, cover, fill, or none—
Four ways to get the framing done.
Company logos, architecture maps,
System diagrams filling gaps.

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

## Image Panel

::: dashboard_compiler.panels.images.config.ImagePanel
    options:
      show_root_heading: false
      heading_level: 2

## Image Panel Configuration

::: dashboard_compiler.panels.images.config.ImagePanelConfig
    options:
      show_root_heading: false
      heading_level: 3

### Fit Options

The `fit` field controls how the image is sized within the panel:

- **`contain`**: (Default) Scales the image to fit within the panel while maintaining its aspect ratio. The entire image will be visible.
- **`cover`**: Scales the image to fill the panel while maintaining its aspect ratio. Some parts of the image may be cropped to achieve this.
- **`fill`**: Stretches or compresses the image to fill the panel completely, potentially altering its original aspect ratio.
- **`none`**: Displays the image at its original size. If the image is larger than the panel, it will be cropped. If smaller, it will sit within the panel, respecting its original dimensions.

## Related Documentation

- [Base Panel Configuration](./base.md)
- [Dashboard Configuration](../dashboard/dashboard.md)
