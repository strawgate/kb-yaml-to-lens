# IIS OpenTelemetry Dashboard

Microsoft IIS monitoring dashboard using OpenTelemetry IIS receiver metrics.

## Overview

This dashboard provides comprehensive monitoring for Microsoft IIS web servers, displaying all metrics collected by the OpenTelemetry Collector's IIS receiver.

## Dashboards

| Dashboard | File | Description |
|-----------|------|-------------|
| **Overview** | `01-iis-overview.yaml` | IIS monitoring with server uptime, connections, request queues, application pools, network I/O, and thread performance |

## Dashboard Definitions

<!-- markdownlint-disable MD046 -->
??? example "Overview (01-iis-overview.yaml)"

    ```yaml
    --8<-- "examples/iis_otel/01-iis-overview.yaml"
    ```
<!-- markdownlint-enable MD046 -->

## Prerequisites

- **IIS**: Microsoft IIS web server on Windows
- **OpenTelemetry Collector**: Collector Contrib with IIS receiver configured
- **Kibana**: Version 9.2 or later (dashboards use ES|QL TS command)

## Data Requirements

- **Data stream dataset**: `iisreceiver.otel`
- **Data view**: `metrics-*`

## OpenTelemetry Collector Configuration

```yaml
receivers:
  iis:
    collection_interval: 10s

exporters:
  elasticsearch:
    endpoints: ["https://your-elasticsearch-instance:9200"]

service:
  pipelines:
    metrics:
      receivers: [iis]
      exporters: [elasticsearch]
```

## Metrics Reference

All metrics are enabled by default.

| Metric | Type | Unit | Description | Attributes |
|--------|------|------|-------------|------------|
| `metrics.iis.application_pool.state` | Gauge | `1` | Application pool state (1-7: Uninitialized to Delete Pending) | — |
| `metrics.iis.application_pool.uptime` | Gauge | `s` | Application pool uptime since last restart | — |
| `metrics.iis.connection.active` | Sum | `{connection}` | Number of active connections | — |
| `metrics.iis.connection.anonymous` | Sum | `{connection}` | Connections established anonymously | — |
| `metrics.iis.connection.attempt.count` | Sum | `{attempt}` | Total connection attempts | — |
| `metrics.iis.network.blocked` | Sum | `By` | Bytes blocked due to bandwidth throttling | — |
| `metrics.iis.network.file.count` | Sum | `{file}` | Number of transmitted files | `attributes.direction` |
| `metrics.iis.network.io` | Sum | `By` | Total bytes sent and received | `attributes.direction` |
| `metrics.iis.request.count` | Sum | `{request}` | Total requests by HTTP method | `attributes.request` |
| `metrics.iis.request.queue.age.max` | Gauge | `s` | Age of oldest request in the queue | — |
| `metrics.iis.request.queue.count` | Sum | `{request}` | Current number of requests in the queue | — |
| `metrics.iis.request.rejected` | Sum | `{request}` | Total number of rejected requests | — |
| `metrics.iis.thread.active` | Sum | `{thread}` | Current number of active threads | — |
| `metrics.iis.uptime` | Gauge | `s` | Server uptime in seconds | — |

### Metric Attributes

| Attribute | Values | Description |
| --------- | ------ | ----------- |
| `attributes.direction` | `sent`, `received` | Data movement direction |
| `attributes.request` | `delete`, `get`, `head`, `options`, `post`, `put`, `trace` | HTTP request method |

### Resource Attributes

| Attribute | Description |
| --------- | ----------- |
| `resource.attributes.iis.application_pool` | Application pool name |
| `resource.attributes.iis.site` | Website name |

### Application Pool State Values

| Value | State |
| ----- | ----- |
| 1 | Uninitialized |
| 2 | Initialized |
| 3 | Running |
| 4 | Disabling |
| 5 | Disabled |
| 6 | Shutdown Pending |
| 7 | Delete Pending |

## Metrics Coverage

**All 14 IIS receiver metrics are used in this dashboard.** There are no unused default metrics.

## Related Resources

- [OpenTelemetry IIS Receiver](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/iisreceiver)
