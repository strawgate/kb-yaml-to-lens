# Complete Examples

This section provides real-world YAML dashboard examples demonstrating various features and capabilities of the Dashboard Compiler.

## How to Use These Examples

1. **Browse:** Click on any example bundle below to view its README with complete documentation
2. **Copy:** Each bundle contains YAML files you can copy to your `inputs/` directory
3. **Compile:** Run the compiler:

   ```bash
   kb-dashboard compile
   ```

4. **Upload (Optional):** To upload directly to Kibana:

   ```bash
   kb-dashboard compile --upload
   ```

## Standalone Examples

These single-file examples demonstrate specific features:

### Controls Example

Demonstrates dashboard controls including options list, range slider, time slider, control chaining, and custom label positions.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (controls-example.yaml)"

    ```yaml
    --8<-- "examples/controls-example.yaml"
    ```
<!-- markdownlint-enable MD046 -->

### Dimensions Example

Shows how to configure dimensions in Lens visualizations including multiple dimension types, custom formatting, and breakdown configurations.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (dimensions-example.yaml)"

    ```yaml
    --8<-- "examples/dimensions-example.yaml"
    ```
<!-- markdownlint-enable MD046 -->

### Color Palette Example

Demonstrates color customization for charts including custom palettes, manual color assignments, and per-chart configuration.

**Note:** Manual color assignments are an advanced topic. See the [Custom Color Assignments](../advanced/color-assignments.md) guide.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (color-palette-examples.yaml)"

    ```yaml
    --8<-- "examples/color-palette-examples.yaml"
    ```
<!-- markdownlint-enable MD046 -->

### Filters Example

Comprehensive filter demonstrations including field existence, phrase filters, range filters, custom DSL, and combined filters.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (filters-example.yaml)"

    ```yaml
    --8<-- "examples/filters-example.yaml"
    ```
<!-- markdownlint-enable MD046 -->

### Multi-Panel Showcase

A complete dashboard featuring multiple panel types: markdown, metrics, pie charts, XY charts, images, links, and grid layouts.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (multi-panel-showcase.yaml)"

    ```yaml
    --8<-- "examples/multi-panel-showcase.yaml"
    ```
<!-- markdownlint-enable MD046 -->

### Navigation Example

Demonstrates dashboard navigation features including links panels, dashboard linking patterns, and URL parameter passing.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (navigation-example.yaml)"

    ```yaml
    --8<-- "examples/navigation-example.yaml"
    ```
<!-- markdownlint-enable MD046 -->

### Heatmap Examples

Examples of heatmap visualizations.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (heatmap-examples.yaml)"

    ```yaml
    --8<-- "examples/heatmap-examples.yaml"
    ```
<!-- markdownlint-enable MD046 -->

### Metric Formatting Examples

Examples of metric formatting options.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (metric-formatting-examples.yaml)"

    ```yaml
    --8<-- "examples/metric-formatting-examples.yaml"
    ```
<!-- markdownlint-enable MD046 -->

## Integration Bundles

Complete dashboard bundles for monitoring various technologies. Each bundle includes multiple dashboards with navigation links and comprehensive documentation.

### OpenTelemetry Integrations

| Bundle | Description |
| ------ | ----------- |
| [Aerospike](aerospike/README.md) | Aerospike NoSQL database monitoring (3 dashboards) |
| [Apache HTTP Server](apache_otel/README.md) | Apache web server metrics and logs (1 dashboard) |
| [AWS CloudTrail](aws_cloudtrail_otel/README.md) | AWS API activity monitoring with ES\|QL (1 dashboard) |
| [AWS VPC Flow Logs](aws_vpcflow_otel/README.md) | VPC network traffic analysis (3 dashboards) |
| [Docker](docker_otel/README.md) | Container monitoring with Docker Stats receiver (2 dashboards) |
| [Elasticsearch](elasticsearch_otel/README.md) | Elasticsearch cluster monitoring (7 dashboards) |
| [Kubernetes Cluster](k8s_cluster_otel/README.md) | K8s cluster health and workload monitoring (5 dashboards) |
| [Memcached](memcached_otel/README.md) | Memcached cache monitoring (1 dashboard) |
| [MySQL](mysql_otel/README.md) | MySQL database metrics (2 dashboards) |
| [PostgreSQL](postgresql_otel/README.md) | PostgreSQL database monitoring (2 dashboards) |
| [Redis](redis_otel/README.md) | Redis instance and database monitoring (3 dashboards) |
| [System (OTel)](system_otel/README.md) | Host metrics with Host Metrics receiver (5 dashboards) |

### Elastic Agent Integrations

| Bundle | Description |
| ------ | ----------- |
| [CrowdStrike](crowdstrike/README.md) | CrowdStrike EDR security dashboards (6 dashboards) |
| [CrowdStrike Modern](crowdstrike-modern/README.md) | Workflow-centric SOC dashboards (4 dashboards) |
| [System (Classic)](system/README.md) | Elastic System integration dashboards (14 dashboards) |
| [System (Modern)](system_modern/README.md) | Modern System dashboards with style guide patterns (14 dashboards) |

## Viewing Example Source Code

All example files are located in the `docs/content/examples/` directory of the repository. You can:

1. **View README:** Click the bundle link to see complete setup instructions and dashboard descriptions
2. **Clone locally:** Download the repository to experiment with examples
3. **Compile examples:** Run `kb-dashboard compile --input-dir docs/content/examples --output-dir output` to generate NDJSON files

## Using Examples as Templates

To use an example as a starting point for your own dashboard:

1. Copy the example YAML file to your `inputs/` directory
2. Modify the dashboard name, description, and ID
3. Adjust panels, filters, and controls to match your data views
4. Compile and upload to Kibana

## Related Documentation

- [Dashboard Configuration](../dashboard/dashboard.md) - Dashboard-level settings
- [Panel Types](../panels/base.md) - Available panel types and configurations
