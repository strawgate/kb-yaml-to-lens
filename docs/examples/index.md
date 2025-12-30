# Complete Examples

This section provides real-world YAML dashboard examples demonstrating various features and capabilities of the Dashboard Compiler.

## Available Examples

### [Controls Example](https://github.com/strawgate/kb-yaml-to-lens/blob/main/docs/examples/controls-example.yaml)

Demonstrates the use of dashboard controls including:

- Options list controls for filtering
- Range slider controls
- Time slider controls
- Control chaining and dependencies
- Custom label positions

**Use this when:** You need interactive filtering capabilities on your dashboard.

### [Dimensions Example](https://github.com/strawgate/kb-yaml-to-lens/blob/main/docs/examples/dimensions-example.yaml)

Shows how to configure dimensions in Lens visualizations:

- Multiple dimension types
- Custom formatting options
- Breakdown configurations
- Top values and other bucketing strategies

**Use this when:** You're building complex charts with multiple breakdowns and groupings.

### [Filters Example](https://github.com/strawgate/kb-yaml-to-lens/blob/main/docs/examples/filters-example.yaml)

Comprehensive filter demonstrations including:

- Field existence filters
- Phrase and phrase list filters
- Range filters (numeric and date)
- Custom DSL filters
- Combined filters with AND/OR/NOT operators
- Panel-level and dashboard-level filters

**Use this when:** You need to pre-filter data or provide context-specific views.

### [Multi-Panel Showcase](https://github.com/strawgate/kb-yaml-to-lens/blob/main/docs/examples/multi-panel-showcase.yaml)

A complete dashboard featuring multiple panel types:

- Markdown panels for documentation
- Metric charts for KPIs
- Pie charts for distributions
- XY charts for trends
- Image panels
- Links panels for navigation
- Grid layout examples

**Use this when:** You want to see how different panel types work together in a single dashboard.

### [Navigation Example](https://github.com/strawgate/kb-yaml-to-lens/blob/main/docs/examples/navigation-example.yaml)

Demonstrates dashboard navigation features:

- Links panels with external and internal navigation
- Dashboard linking patterns
- URL parameter passing
- Navigation best practices

**Use this when:** You're building a suite of interconnected dashboards.

### [Aerospike Monitoring Examples](https://github.com/strawgate/kb-yaml-to-lens/tree/main/docs/examples/aerospike/)

Real-world monitoring dashboards for Aerospike database:

- **Overview Dashboard** - Cluster-level metrics and node health
- **Node Metrics** - Detailed per-node performance monitoring
- **Namespace Metrics** - Namespace-level storage and query statistics

**Use this when:** Monitoring Aerospike NoSQL database deployments.

## Viewing Example Source Code

All example files are located in the `docs/examples/` directory of the repository. You can:

1. **Browse on GitHub:** Click any example link above to view the YAML source
2. **Clone locally:** Download the repository to experiment with examples
3. **Compile examples:** Run `kb-dashboard compile --input-dir docs/examples --output-dir output` to generate NDJSON files

## Using Examples as Templates

To use an example as a starting point for your own dashboard:

1. Copy the example YAML file to your `inputs/` directory
2. Modify the dashboard name, description, and ID
3. Adjust panels, filters, and controls to match your data views
4. Compile and upload to Kibana

## Related Documentation

- [Dashboard Configuration](../dashboard/dashboard.md) - Dashboard-level settings
- [Panel Types](../panels/base.md) - Available panel types and configurations
