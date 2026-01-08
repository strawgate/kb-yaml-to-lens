# Complete Examples

This section provides real-world YAML dashboard examples demonstrating various features and capabilities of the Dashboard Compiler.

## How to Use These Examples

1. **View:** Expand the "Dashboard Definition" section for any example below to see the complete code inline. (Click the section header to expand.)
2. **Copy:** Use the copy button in the expanded code block.
3. **Save:** Save the content to a `.yaml` file in your `inputs/` directory (e.g., `inputs/my_example.yaml`).
4. **Compile:** Run the compiler:

   ```bash
   kb-dashboard compile
   ```

5. **Upload (Optional):** To upload directly to Kibana:

   ```bash
   kb-dashboard compile --upload
   ```

## Available Examples

### Controls Example

Demonstrates the use of dashboard controls including:

- Options list controls for filtering
- Range slider controls
- Time slider controls
- Control chaining and dependencies
- Custom label positions

**Use this when:** You need interactive filtering capabilities on your dashboard.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (controls-example.yaml)"

    ```yaml
    --8<-- "examples/controls-example.yaml"
    ```
<!-- markdownlint-enable MD046 -->

### Dimensions Example

Shows how to configure dimensions in Lens visualizations:

- Multiple dimension types
- Custom formatting options
- Breakdown configurations
- Top values and other bucketing strategies

**Use this when:** You're building complex charts with multiple breakdowns and groupings.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (dimensions-example.yaml)"

    ```yaml
    --8<-- "examples/dimensions-example.yaml"
    ```
<!-- markdownlint-enable MD046 -->

### Color Palette Example

Demonstrates color customization for charts including:

- Custom color palettes (color-blind safe, Elastic brand, grayscale, legacy)
- **Advanced:** Manual color assignments to specific values
- **Advanced:** Multi-value color grouping
- Per-chart color configuration
- **Advanced:** Color assignments for pie, line, bar, and area charts

**Use this when:** You need to customize chart colors for branding, accessibility, or visual clarity.

**Note:** Manual color assignments are an advanced topic. See the [Custom Color Assignments](../advanced/color-assignments.md) guide for an introduction.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (color-palette-examples.yaml)"

    ```yaml
    --8<-- "examples/color-palette-examples.yaml"
    ```
<!-- markdownlint-enable MD046 -->

### Filters Example

Comprehensive filter demonstrations including:

- Field existence filters
- Phrase and phrase list filters
- Range filters (numeric and date)
- Custom DSL filters
- Combined filters with AND/OR/NOT operators
- Panel-level and dashboard-level filters

**Use this when:** You need to pre-filter data or provide context-specific views.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (filters-example.yaml)"

    ```yaml
    --8<-- "examples/filters-example.yaml"
    ```
<!-- markdownlint-enable MD046 -->

### Multi-Panel Showcase

A complete dashboard featuring multiple panel types:

- Markdown panels for documentation
- Metric charts for KPIs
- Pie charts for distributions
- XY charts for trends
- Image panels
- Links panels for navigation
- Grid layout examples

**Use this when:** You want to see how different panel types work together in a single dashboard.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (multi-panel-showcase.yaml)"

    ```yaml
    --8<-- "examples/multi-panel-showcase.yaml"
    ```
<!-- markdownlint-enable MD046 -->

### Navigation Example

Demonstrates dashboard navigation features:

- Links panels with external and internal navigation
- Dashboard linking patterns
- URL parameter passing
- Navigation best practices

**Use this when:** You're building a suite of interconnected dashboards.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (navigation-example.yaml)"

    ```yaml
    --8<-- "examples/navigation-example.yaml"
    ```
<!-- markdownlint-enable MD046 -->

### Aerospike Monitoring Examples

Real-world monitoring dashboards for Aerospike database.

**Use this when:** Monitoring Aerospike NoSQL database deployments.

#### Overview Dashboard

Cluster-level metrics and node health monitoring.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (aerospike/overview.yaml)"

    ```yaml
    --8<-- "examples/aerospike/overview.yaml"
    ```
<!-- markdownlint-enable MD046 -->

#### Node Metrics

Detailed per-node performance monitoring.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (aerospike/node-metrics.yaml)"

    ```yaml
    --8<-- "examples/aerospike/node-metrics.yaml"
    ```
<!-- markdownlint-enable MD046 -->

#### Namespace Metrics

Namespace-level storage and query statistics.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (aerospike/namespace-metrics.yaml)"

    ```yaml
    --8<-- "examples/aerospike/namespace-metrics.yaml"
    ```
<!-- markdownlint-enable MD046 -->

### OpenTelemetry System Dashboards

Comprehensive host monitoring dashboards for OpenTelemetry system metrics.

**Use this when:** Monitoring infrastructure with OpenTelemetry Host Metrics Receiver.

**Note:** Based on the [Elastic integrations repository](https://github.com/elastic/integrations/tree/main/packages/system_otel) dashboards. Some advanced panels (AI-powered features, legacy visualizations) are excluded as they're not yet supported by the compiler.

#### Hosts Overview

Overview of all hosts with key performance metrics.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (system_otel/01-hosts-overview.yaml)"

    ```yaml
    --8<-- "examples/system_otel/01-hosts-overview.yaml"
    ```
<!-- markdownlint-enable MD046 -->

#### Host Details - Overview

Detailed single host overview with CPU, memory, and disk metrics.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (system_otel/02-host-details-overview.yaml)"

    ```yaml
    --8<-- "examples/system_otel/02-host-details-overview.yaml"
    ```
<!-- markdownlint-enable MD046 -->

#### Host Details - Metrics

In-depth metrics charts for CPU, memory, disk, and load.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (system_otel/03-host-details-metrics.yaml)"

    ```yaml
    --8<-- "examples/system_otel/03-host-details-metrics.yaml"
    ```
<!-- markdownlint-enable MD046 -->

#### Host Details - Metadata

Host resource attributes and metadata (ES|QL datatables).

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (system_otel/04-host-details-metadata.yaml)"

    ```yaml
    --8<-- "examples/system_otel/04-host-details-metadata.yaml"
    ```
<!-- markdownlint-enable MD046 -->

#### Host Details - Logs

Host log messages (ES|QL datatable).

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (system_otel/05-host-details-logs.yaml)"

    ```yaml
    --8<-- "examples/system_otel/05-host-details-logs.yaml"
    ```
<!-- markdownlint-enable MD046 -->

### Docker OpenTelemetry Dashboards

Docker container monitoring dashboards for OpenTelemetry metrics.

**Use this when:** Monitoring Docker containers with OpenTelemetry Docker Stats Receiver.

**Note:** Based on the [Elastic integrations repository](https://github.com/elastic/integrations/tree/main/packages/docker_otel) dashboards.

#### Containers Overview

Multi-container monitoring with CPU, memory, disk I/O, and network metrics.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (docker_otel/01-containers-overview.yaml)"

    ```yaml
    --8<-- "examples/docker_otel/01-containers-overview.yaml"
    ```
<!-- markdownlint-enable MD046 -->

#### Container Stats

Detailed single-container performance analysis and resource utilization.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (docker_otel/02-container-stats.yaml)"

    ```yaml
    --8<-- "examples/docker_otel/02-container-stats.yaml"
    ```
<!-- markdownlint-enable MD046 -->

## Viewing Example Source Code

All example files are located in the `docs/examples/` directory of the repository. You can:

1. **View inline:** Expand any "Dashboard Definition" section above to see the complete YAML code
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
