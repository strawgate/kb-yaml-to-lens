# Custom Color Assignments

While the compiler includes several built-in color palettes for basic color customization, you can also manually assign specific colors to individual data values. This is useful for semantic coloring (e.g., green for success, red for errors) or brand-specific requirements.

## When to Use Color Assignments

Manual color assignments are particularly valuable when:

- **Semantic Meaning**: Colors convey meaning (green = success, red = error, yellow = warning)
- **Brand Requirements**: Specific data values must match brand guidelines
- **Consistency**: Colors need to be consistent across multiple dashboards
- **Accessibility**: You need to ensure specific high-contrast color combinations

For simple color customization without semantic meaning, consider using one of the [built-in color palettes](../panels/base.md#color-mapping-configuration) instead.

## Basic Example: HTTP Status Code Coloring

This example demonstrates semantic color assignments for HTTP status codes:

```yaml
dashboards:
-
  name: Status Monitoring
  panels:
    - title: HTTP Response Codes
      grid: { x: 0, y: 0, w: 24, h: 15 }
      lens:
        type: pie
        data_view: "logs-*"
        dimensions:
          - field: "http.response.status_code"
            type: values
        metrics:
          - aggregation: count
        color:
          palette: 'eui_amsterdam_color_blind'
          assignments:
            - values: ['200', '201']
              color: '#00BF6F'  # Green for success
            - values: ['404']
              color: '#FFA500'  # Orange for not found
            - values: ['500', '502', '503']
              color: '#BD271E'  # Red for errors
```

In this example:

- A base palette (`eui_amsterdam_color_blind`) provides colors for unassigned values
- Specific status codes receive semantic colors (green for 2xx, orange for 404, red for 5xx)
- Multiple values can share the same color using the `values` array

## Configuration Reference

### ColorMapping Object

The `color` field on chart panels accepts a `ColorMapping` object:

| YAML Key | Data Type | Description | Default | Required |
| -------- | --------- | ----------- | ------- | -------- |
| `palette` | `string` | The color palette ID to use for unassigned colors. | `'eui_amsterdam_color_blind'` | No |
| `assignments` | `list[ColorAssignment]` | Manual color assignments to specific data values. | `[]` | No |

### ColorAssignment Object

Each item in the `assignments` list specifies a color for one or more data values:

| YAML Key | Data Type | Description | Required |
| -------- | --------- | ----------- | -------- |
| `value` | `string` | Single data value to assign this color to. | No* |
| `values` | `list[str]` | List of data values to assign this color to. | No* |
| `color` | `string` | Hex color code (e.g., '#FF0000'). | Yes |

\* At least one of `value` or `values` must be provided.

## Advanced Patterns

### Pattern 1: Grouping Related Values

Group related values under a single color to reduce visual complexity:

```yaml
color:
  palette: 'eui_amsterdam_color_blind'
  assignments:
    # Success states
    - values: ['completed', 'success', 'ok']
      color: '#00BF6F'
    # Warning states
    - values: ['pending', 'in_progress', 'waiting']
      color: '#FFA500'
    # Error states
    - values: ['failed', 'error', 'timeout']
      color: '#BD271E'
```

### Pattern 2: Single Value Assignment

For individual values, you can use either `value` (singular) or `values` (list):

```yaml
color:
  assignments:
    # Using 'value' for single values
    - value: 'critical'
      color: '#BD271E'
    # Using 'values' with a single-item list (equivalent)
    - values: ['warning']
      color: '#FFA500'
```

### Pattern 3: Combining with Palette Selection

Choose a palette that provides good defaults for unassigned values:

```yaml
color:
  palette: 'gray'  # Unassigned values use grayscale
  assignments:
    # Only highlight important values with color
    - value: 'critical_error'
      color: '#BD271E'
    - value: 'performance_issue'
      color: '#FFA500'
```

## Comprehensive Example

For a complete example showcasing various color assignment techniques across different chart types, see the [color-palette-examples.yaml](https://github.com/strawgate/kb-yaml-to-lens/blob/main/docs/examples/color-palette-examples.yaml) file in the repository.

## Best Practices

1. **Use Semantic Colors Consistently**: Establish a color scheme and use it consistently across all dashboards (e.g., always use red for errors).

2. **Consider Color Blindness**: While you can use any hex color, consider color-blind accessibility. Use the `eui_amsterdam_color_blind` palette as a base and only override specific values when necessary.

3. **Document Your Color Scheme**: Add comments to your YAML explaining the meaning of color assignments:

   ```yaml
   color:
     assignments:
       # Critical alerts require immediate attention
       - value: 'critical'
         color: '#BD271E'
   ```

4. **Test in Different Themes**: Kibana supports light and dark themes. Test your color choices in both to ensure they remain visible and meaningful.

5. **Limit Manual Assignments**: Only assign colors to values that need semantic meaning. Let the palette handle the rest to maintain visual harmony.

## Related Documentation

- [Color Mapping Configuration](../panels/base.md#color-mapping-configuration) - Base panel color configuration reference
- [Color Palette Examples](https://github.com/strawgate/kb-yaml-to-lens/blob/main/docs/examples/color-palette-examples.yaml) - Comprehensive color examples
- [Pie Charts](../panels/pie.md) - Pie chart color configuration
- [XY Charts](../panels/xy.md) - XY chart color configuration
