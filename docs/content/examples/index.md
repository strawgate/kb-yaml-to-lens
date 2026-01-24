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

**Note:** Based on the [Elastic integrations repository](https://github.com/elastic/integrations/tree/main/packages/system_otel) dashboards. Licensed under [Elastic License 2.0](../licenses/ELASTIC-LICENSE-2.0.txt). Some advanced panels (AI-powered features, legacy visualizations) are excluded as they're not yet supported by the compiler.

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

### AWS CloudTrail OpenTelemetry Dashboard

AWS CloudTrail activity monitoring dashboard using ES|QL for data processing.

**Use this when:** Monitoring AWS API calls and user actions via CloudTrail with OpenTelemetry.

**Note:** Based on the [Elastic integrations repository](https://github.com/elastic/integrations/tree/main/packages/aws_cloudtrail_otel) dashboard. This example demonstrates advanced ES|QL features including calculated fields, nested dimensions, and string manipulation.

#### CloudTrail Logs Overview

Comprehensive CloudTrail activity visualization with success/failure tracking, service breakdowns, and user analysis.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (aws_cloudtrail_otel/cloudtrail-logs-overview.yaml)"

    ```yaml
    --8<-- "examples/aws_cloudtrail_otel/cloudtrail-logs-overview.yaml"
    ```
<!-- markdownlint-enable MD046 -->

### Docker OpenTelemetry Dashboards

Docker container monitoring dashboards for OpenTelemetry metrics.

**Use this when:** Monitoring Docker containers with OpenTelemetry Docker Stats Receiver.

**Note:** Based on the [Elastic integrations repository](https://github.com/elastic/integrations/tree/main/packages/docker_otel) dashboards. Licensed under [Elastic License 2.0](../licenses/ELASTIC-LICENSE-2.0.txt).

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

### Elasticsearch OpenTelemetry Dashboards

Comprehensive Elasticsearch cluster monitoring dashboards using OpenTelemetry's Elasticsearch receiver. Includes a complete OpenTelemetry Collector configuration and detailed setup guide.

**Use this when:** Monitoring Elasticsearch clusters with OpenTelemetry Elasticsearch Receiver.

**Includes:** 7 dashboards covering cluster health, node metrics, JVM monitoring, index statistics, and circuit breakers. See [elasticsearch_otel/README.md](elasticsearch_otel/README.md) for complete setup instructions and OpenTelemetry Collector configuration.

#### Cluster Overview

High-level cluster health, node counts, shard distribution, and pending tasks.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (elasticsearch_otel/01-cluster-overview.yaml)"

    ```yaml
    --8<-- "examples/elasticsearch_otel/01-cluster-overview.yaml"
    ```
<!-- markdownlint-enable MD046 -->

#### Node Overview

Node-level summary with CPU, memory, disk, and operations.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (elasticsearch_otel/02-node-overview.yaml)"

    ```yaml
    --8<-- "examples/elasticsearch_otel/02-node-overview.yaml"
    ```
<!-- markdownlint-enable MD046 -->

#### Node Metrics

Detailed node performance metrics including cache and thread pools.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (elasticsearch_otel/03-node-metrics.yaml)"

    ```yaml
    --8<-- "examples/elasticsearch_otel/03-node-metrics.yaml"
    ```
<!-- markdownlint-enable MD046 -->

#### Index Metrics

Index-level statistics, shard sizes, segments, and operations.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (elasticsearch_otel/04-index-metrics.yaml)"

    ```yaml
    --8<-- "examples/elasticsearch_otel/04-index-metrics.yaml"
    ```
<!-- markdownlint-enable MD046 -->

#### JVM Health

JVM memory (heap/non-heap), garbage collection, threads, and memory pools.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (elasticsearch_otel/05-jvm-health.yaml)"

    ```yaml
    --8<-- "examples/elasticsearch_otel/05-jvm-health.yaml"
    ```
<!-- markdownlint-enable MD046 -->

#### Circuit Breakers

Circuit breaker memory usage, limits, and trip events.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (elasticsearch_otel/06-circuit-breakers.yaml)"

    ```yaml
    --8<-- "examples/elasticsearch_otel/06-circuit-breakers.yaml"
    ```
<!-- markdownlint-enable MD046 -->

#### Cluster Metadata

Cluster configuration and metadata exploration using ES|QL.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (elasticsearch_otel/07-cluster-metadata.yaml)"

    ```yaml
    --8<-- "examples/elasticsearch_otel/07-cluster-metadata.yaml"
### Kubernetes Cluster OpenTelemetry Dashboards

Comprehensive Kubernetes cluster monitoring dashboards using the OpenTelemetry k8sclusterreceiver.

**Use this when:** Monitoring Kubernetes clusters with OpenTelemetry Collector's k8sclusterreceiver.

**Note:** See the [README](k8s_cluster_otel/README.md) for RBAC configuration, OpenTelemetry Collector setup, and deployment instructions.

#### Cluster Overview

Entry point for cluster health triage - pods, workloads, and deployment health.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (k8s_cluster_otel/01-cluster-overview.yaml)"

    ```yaml
    --8<-- "examples/k8s_cluster_otel/01-cluster-overview.yaml"
    ```
<!-- markdownlint-enable MD046 -->

#### Workload Health

Deployment, StatefulSet, DaemonSet, and container health monitoring.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (k8s_cluster_otel/02-workload-health.yaml)"

    ```yaml
    --8<-- "examples/k8s_cluster_otel/02-workload-health.yaml"
    ```
<!-- markdownlint-enable MD046 -->

#### Resource Allocation

CPU, memory, and storage requests vs limits for capacity planning.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (k8s_cluster_otel/03-resource-allocation.yaml)"

    ```yaml
    --8<-- "examples/k8s_cluster_otel/03-resource-allocation.yaml"
    ```
<!-- markdownlint-enable MD046 -->

#### Batch Jobs

Job and CronJob execution status and completion tracking.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (k8s_cluster_otel/04-batch-jobs.yaml)"

    ```yaml
    --8<-- "examples/k8s_cluster_otel/04-batch-jobs.yaml"
    ```
<!-- markdownlint-enable MD046 -->

#### Autoscaling

Horizontal Pod Autoscaler scaling behavior and capacity tracking.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (k8s_cluster_otel/05-autoscaling.yaml)"

    ```yaml
    --8<-- "examples/k8s_cluster_otel/05-autoscaling.yaml"
### Apache HTTP Server OpenTelemetry Dashboard

Apache HTTP Server monitoring dashboard using OpenTelemetry metrics.

**Use this when:** Monitoring Apache web servers with OpenTelemetry Apache Receiver.

**Note:** Based on the [Elastic integrations repository](https://github.com/elastic/integrations/tree/main/packages/apache_http_server_otel) dashboard. Licensed under [Elastic License 2.0](../licenses/ELASTIC-LICENSE-2.0.txt).

#### Apache Logs Overview

Apache HTTP Server log analysis with request breakdowns, status codes, and traffic patterns.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (apache_http_server_otel/apache-logs-overview.yaml)"

    ```yaml
    --8<-- "examples/apache_http_server_otel/apache-logs-overview.yaml"
    ```
<!-- markdownlint-enable MD046 -->

### AWS VPC Flow Logs OpenTelemetry Dashboards

AWS VPC Flow Logs monitoring dashboards for OpenTelemetry data with interconnected navigation.

**Use this when:** Monitoring AWS VPC network traffic with OpenTelemetry AWS VPC Flow Logs receiver.

**Note:** Based on the [Elastic integrations repository](https://github.com/elastic/integrations/tree/main/packages/aws_vpcflow_otel) dashboards. Demonstrates ES|QL queries with area charts, bar charts, datatables, and dashboard links. See the [README](aws_vpcflow_otel/README.md) for data requirements and panel details.

Includes 3 interconnected dashboards with navigation links:

- **VPC Flow Logs Overview** (`aws_vpcflow_otel-overview`) - High-level KPIs, quick insights, and time-series trends
- **Traffic Analysis** (`aws_vpcflow_otel-traffic`) - Traffic distribution, source analysis, security deep dive, and top sources/destinations
- **Interface Analysis** (`aws_vpcflow_otel-interface`) - Per-interface analysis, bandwidth by interface, and per-account metrics

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (aws_vpcflow_otel/dashboards.yaml)"

    ```yaml
    --8<-- "examples/aws_vpcflow_otel/dashboards.yaml"
    ```
<!-- markdownlint-enable MD046 -->

### Redis OpenTelemetry Dashboards

Redis database monitoring dashboards for OpenTelemetry metrics.

**Use this when:** Monitoring Redis instances with OpenTelemetry Redis Receiver.

#### Overview

Multi-instance monitoring with key metrics across all Redis instances.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (redis_otel/overview.yaml)"

    ```yaml
    --8<-- "examples/redis_otel/overview.yaml"
    ```
<!-- markdownlint-enable MD046 -->

#### Instance Details

Detailed single-instance analysis including memory, connections, keyspace, and replication metrics.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (redis_otel/instance-details.yaml)"

    ```yaml
    --8<-- "examples/redis_otel/instance-details.yaml"
    ```
<!-- markdownlint-enable MD046 -->

#### Database Metrics

Per-database keyspace metrics including keys, TTL, and expiration statistics.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (redis_otel/database-metrics.yaml)"

    ```yaml
    --8<-- "examples/redis_otel/database-metrics.yaml"
    ```
<!-- markdownlint-enable MD046 -->

### CrowdStrike Security Dashboards

Security monitoring dashboards for CrowdStrike EDR data streams. Includes both dataset-centric dashboards (organized by data source) and workflow-centric modern dashboards (organized by security workflow).

**Use this when:** Monitoring CrowdStrike Falcon EDR alerts, incidents, vulnerabilities, and host data.

**Note:** Based on the [Elastic integrations repository](https://github.com/elastic/integrations/tree/main/packages/crowdstrike) dashboards. Licensed under [Elastic License 2.0](../licenses/ELASTIC-LICENSE-2.0.txt).

#### Overview Dashboard

High-level entry point with navigation to all CrowdStrike dashboards.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (crowdstrike/overview.yaml)"

    ```yaml
    --8<-- "examples/crowdstrike/overview.yaml"
    ```
<!-- markdownlint-enable MD046 -->

#### Alert Dashboard

Comprehensive alert monitoring with 16 panels covering status, severity, IOCs, and network context.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (crowdstrike/alert.yaml)"

    ```yaml
    --8<-- "examples/crowdstrike/alert.yaml"
    ```
<!-- markdownlint-enable MD046 -->

#### Falcon Overview

Falcon incidents with MITRE ATT&CK technique and tactic mapping.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (crowdstrike/falcon-overview.yaml)"

    ```yaml
    --8<-- "examples/crowdstrike/falcon-overview.yaml"
    ```
<!-- markdownlint-enable MD046 -->

#### FDR Overview

Falcon Data Replicator events and alerts monitoring.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (crowdstrike/fdr-overview.yaml)"

    ```yaml
    --8<-- "examples/crowdstrike/fdr-overview.yaml"
    ```
<!-- markdownlint-enable MD046 -->

#### Host Dashboard

Host device monitoring with OS platform distribution and activity tracking.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (crowdstrike/host.yaml)"

    ```yaml
    --8<-- "examples/crowdstrike/host.yaml"
    ```
<!-- markdownlint-enable MD046 -->

#### Vulnerability Dashboard

Vulnerability tracking with severity, status, and confidence breakdowns.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (crowdstrike/vulnerability.yaml)"

    ```yaml
    --8<-- "examples/crowdstrike/vulnerability.yaml"
    ```
<!-- markdownlint-enable MD046 -->

### CrowdStrike Modern Dashboards

Workflow-centric security operations dashboards designed for modern SOC workflows. These dashboards follow the [Dashboard Style Guide](../dashboard-style-guide.md) best practices with progressive disclosure pattern, consistent navigation, and control filters.

**Use this when:** Building workflow-centric security dashboards for daily SOC operations, threat investigation, vulnerability management, or compliance reporting.

#### SOC Dashboard

Real-time security event monitoring, alert triage, and incident response coordination.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (crowdstrike-modern/soc.yaml)"

    ```yaml
    --8<-- "examples/crowdstrike-modern/soc.yaml"
    ```
<!-- markdownlint-enable MD046 -->

#### Threat Investigation

Deep-dive threat analysis with MITRE ATT&CK mapping and IOC tracking.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (crowdstrike-modern/threat-investigation.yaml)"

    ```yaml
    --8<-- "examples/crowdstrike-modern/threat-investigation.yaml"
    ```
<!-- markdownlint-enable MD046 -->

#### Asset & Vulnerability Management

Asset inventory and vulnerability tracking for risk assessment and patch prioritization.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (crowdstrike-modern/asset-vulnerability.yaml)"

    ```yaml
    --8<-- "examples/crowdstrike-modern/asset-vulnerability.yaml"
    ```
<!-- markdownlint-enable MD046 -->

#### Compliance & Audit

Compliance monitoring and audit trail analysis for regulatory reporting.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (crowdstrike-modern/compliance-audit.yaml)"

    ```yaml
    --8<-- "examples/crowdstrike-modern/compliance-audit.yaml"
    ```
<!-- markdownlint-enable MD046 -->

### System Integration Dashboards

Comprehensive monitoring dashboards for the Elastic System integration.

**Use this when:** Monitoring Linux/Unix systems, Windows systems, and Windows security events.

**Note:** Based on the [Elastic integrations repository](https://github.com/elastic/integrations/tree/main/packages/system) dashboards. Licensed under [Elastic License 2.0](../licenses/ELASTIC-LICENSE-2.0.txt).

#### Classic Dashboards

These dashboards are direct conversions from the Elastic System integration.

**Metrics Dashboards:**

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (system/01-metrics-overview.yaml)"

    ```yaml
    --8<-- "examples/system/01-metrics-overview.yaml"
    ```
<!-- markdownlint-enable MD046 -->

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (system/02-host-details.yaml)"

    ```yaml
    --8<-- "examples/system/02-host-details.yaml"
    ```
<!-- markdownlint-enable MD046 -->

**Log Dashboards:**

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (system/03-syslog.yaml)"

    ```yaml
    --8<-- "examples/system/03-syslog.yaml"
    ```
<!-- markdownlint-enable MD046 -->

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (system/04-sudo-commands.yaml)"

    ```yaml
    --8<-- "examples/system/04-sudo-commands.yaml"
    ```
<!-- markdownlint-enable MD046 -->

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (system/05-ssh-logins.yaml)"

    ```yaml
    --8<-- "examples/system/05-ssh-logins.yaml"
    ```
<!-- markdownlint-enable MD046 -->

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (system/06-users-groups.yaml)"

    ```yaml
    --8<-- "examples/system/06-users-groups.yaml"
    ```
<!-- markdownlint-enable MD046 -->

**Windows Security Dashboards:**

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (system/07-windows-overview.yaml)"

    ```yaml
    --8<-- "examples/system/07-windows-overview.yaml"
    ```
<!-- markdownlint-enable MD046 -->

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (system/08-windows-logons.yaml)"

    ```yaml
    --8<-- "examples/system/08-windows-logons.yaml"
    ```
<!-- markdownlint-enable MD046 -->

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (system/09-windows-failed-blocked.yaml)"

    ```yaml
    --8<-- "examples/system/09-windows-failed-blocked.yaml"
    ```
<!-- markdownlint-enable MD046 -->

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (system/10-windows-user-management.yaml)"

    ```yaml
    --8<-- "examples/system/10-windows-user-management.yaml"
    ```
<!-- markdownlint-enable MD046 -->

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (system/11-windows-group-management.yaml)"

    ```yaml
    --8<-- "examples/system/11-windows-group-management.yaml"
    ```
<!-- markdownlint-enable MD046 -->

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (system/12-windows-directory-monitoring.yaml)"

    ```yaml
    --8<-- "examples/system/12-windows-directory-monitoring.yaml"
    ```
<!-- markdownlint-enable MD046 -->

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (system/13-windows-system-process.yaml)"

    ```yaml
    --8<-- "examples/system/13-windows-system-process.yaml"
    ```
<!-- markdownlint-enable MD046 -->

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (system/14-windows-policy-object.yaml)"

    ```yaml
    --8<-- "examples/system/14-windows-policy-object.yaml"
    ```
<!-- markdownlint-enable MD046 -->

#### Modern Dashboards

These dashboards follow the [Dashboard Style Guide](../dashboard-style-guide.md) best practices with:

- 4-layer hierarchy (Context → Summary → Analysis → Detail)
- Navigation links at top
- Limited metric cards (0-4)
- Appropriate chart types
- Tables at bottom with 10-row pagination
- Controls for filtering

**Metrics Dashboards:**

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (system_modern/01-metrics-overview.yaml)"

    ```yaml
    --8<-- "examples/system_modern/01-metrics-overview.yaml"
    ```
<!-- markdownlint-enable MD046 -->

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (system_modern/02-host-details.yaml)"

    ```yaml
    --8<-- "examples/system_modern/02-host-details.yaml"
    ```
<!-- markdownlint-enable MD046 -->

**Log Dashboards:**

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (system_modern/03-syslog.yaml)"

    ```yaml
    --8<-- "examples/system_modern/03-syslog.yaml"
    ```
<!-- markdownlint-enable MD046 -->

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (system_modern/04-sudo-commands.yaml)"

    ```yaml
    --8<-- "examples/system_modern/04-sudo-commands.yaml"
    ```
<!-- markdownlint-enable MD046 -->

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (system_modern/05-ssh-logins.yaml)"

    ```yaml
    --8<-- "examples/system_modern/05-ssh-logins.yaml"
    ```
<!-- markdownlint-enable MD046 -->

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (system_modern/06-users-groups.yaml)"

    ```yaml
    --8<-- "examples/system_modern/06-users-groups.yaml"
    ```
<!-- markdownlint-enable MD046 -->

**Windows Security Dashboards:**

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (system_modern/07-windows-overview.yaml)"

    ```yaml
    --8<-- "examples/system_modern/07-windows-overview.yaml"
    ```
<!-- markdownlint-enable MD046 -->

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (system_modern/08-windows-logons.yaml)"

    ```yaml
    --8<-- "examples/system_modern/08-windows-logons.yaml"
    ```
<!-- markdownlint-enable MD046 -->

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (system_modern/09-windows-failed-blocked.yaml)"

    ```yaml
    --8<-- "examples/system_modern/09-windows-failed-blocked.yaml"
    ```
<!-- markdownlint-enable MD046 -->

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (system_modern/10-windows-user-management.yaml)"

    ```yaml
    --8<-- "examples/system_modern/10-windows-user-management.yaml"
    ```
<!-- markdownlint-enable MD046 -->

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (system_modern/11-windows-group-management.yaml)"

    ```yaml
    --8<-- "examples/system_modern/11-windows-group-management.yaml"
    ```
<!-- markdownlint-enable MD046 -->

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (system_modern/12-windows-directory-monitoring.yaml)"

    ```yaml
    --8<-- "examples/system_modern/12-windows-directory-monitoring.yaml"
    ```
<!-- markdownlint-enable MD046 -->

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (system_modern/13-windows-system-process.yaml)"

    ```yaml
    --8<-- "examples/system_modern/13-windows-system-process.yaml"
    ```
<!-- markdownlint-enable MD046 -->

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (system_modern/14-windows-policy-object.yaml)"

    ```yaml
    --8<-- "examples/system_modern/14-windows-policy-object.yaml"
    ```
<!-- markdownlint-enable MD046 -->

### Apache HTTP Server OpenTelemetry Dashboard

Apache HTTP Server monitoring dashboard for OpenTelemetry metrics.

**Use this when:** Monitoring Apache HTTP Server with OpenTelemetry Apache Receiver.

#### Overview

Server status, scoreboard, and performance metrics.

<!-- markdownlint-disable MD046 -->
??? example "Dashboard Definition (apache_otel/01-overview.yaml)"

    ```yaml
    --8<-- "examples/apache_otel/01-overview.yaml"
    ```
<!-- markdownlint-enable MD046 -->

## Viewing Example Source Code

All example files are located in the `docs/content/examples/` directory of the repository. You can:

1. **View inline:** Expand any "Dashboard Definition" section above to see the complete YAML code
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
