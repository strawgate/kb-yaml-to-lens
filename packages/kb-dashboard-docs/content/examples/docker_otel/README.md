# Docker OpenTelemetry Dashboards

Docker container monitoring dashboards using OpenTelemetry Docker Stats Receiver metrics.

## Overview

These dashboards provide comprehensive monitoring for Docker containers including CPU, memory, disk I/O, and network metrics.

**Note:** Based on the [Elastic integrations repository](https://github.com/elastic/integrations/tree/main/packages/docker_otel) dashboards. Licensed under [Elastic License 2.0](../../licenses/ELASTIC-LICENSE-2.0.txt).

## Dashboards

| Dashboard | File | Description |
|-----------|------|-------------|
| **Containers Overview** | `01-containers-overview.yaml` | Multi-container monitoring with CPU, memory, disk I/O, and network metrics |
| **Container Stats** | `02-container-stats.yaml` | Detailed single-container performance analysis and resource utilization |

All dashboards include navigation links for easy switching between views.

## Dashboard Definitions

<!-- markdownlint-disable MD046 -->
??? example "Containers Overview (01-containers-overview.yaml)"

    ```yaml
    --8<-- "examples/docker_otel/01-containers-overview.yaml"
    ```

??? example "Container Stats (02-container-stats.yaml)"

    ```yaml
    --8<-- "examples/docker_otel/02-container-stats.yaml"
    ```
<!-- markdownlint-enable MD046 -->

## Prerequisites

- **Docker**: Docker Engine with containers running
- **OpenTelemetry Collector**: Collector Contrib with Docker Stats receiver configured
- **Kibana**: Version 8.x or later

## Data Requirements

- **Data stream dataset**: `dockerstatsreceiver.otel`
- **Data view**: `metrics-*`

## OpenTelemetry Collector Configuration

```yaml
receivers:
  docker_stats:
    endpoint: unix:///var/run/docker.sock
    collection_interval: 10s

exporters:
  elasticsearch:
    endpoints: ["https://your-elasticsearch-instance:9200"]

service:
  pipelines:
    metrics:
      receivers: [docker_stats]
      exporters: [elasticsearch]
```

## Metrics Reference

### Default Metrics

| Metric | Type | Unit | Description | Attributes |
|--------|------|------|-------------|------------|
| `container.blockio.io_service_bytes_recursive` | Sum | `By` | Bytes transferred to/from disk | `device_major`, `device_minor`, `operation` |
| `container.cpu.usage.kernelmode` | Sum | `ns` | CPU time in kernel mode | — |
| `container.cpu.usage.total` | Sum | `ns` | Total CPU time consumed | — |
| `container.cpu.usage.usermode` | Sum | `ns` | CPU time in user mode | — |
| `container.cpu.utilization` | Gauge | `1` | Percent of CPU used by container | — |
| `container.memory.file` | Sum | `By` | Filesystem cache memory (cgroups v2) | — |
| `container.memory.percent` | Gauge | `1` | Percentage of memory used | — |
| `container.memory.total_cache` | Sum | `By` | Memory with block devices | — |
| `container.memory.usage.limit` | Sum | `By` | Memory limit set for container | — |
| `container.memory.usage.total` | Sum | `By` | Memory usage excluding cache | — |
| `container.network.io.usage.rx_bytes` | Sum | `By` | Bytes received | `interface` |
| `container.network.io.usage.rx_dropped` | Sum | `{packets}` | Incoming packets dropped | `interface` |
| `container.network.io.usage.tx_bytes` | Sum | `By` | Bytes transmitted | `interface` |
| `container.network.io.usage.tx_dropped` | Sum | `{packets}` | Outgoing packets dropped | `interface` |

### Optional Metrics (60+ additional available)

| Category | Example Metrics |
|----------|----------------|
| **Block I/O** | `io_merged`, `io_queued`, `io_service_time`, `io_serviced`, `io_time`, `io_wait_time` |
| **CPU** | `limit`, `logical.count`, `shares`, `throttling_data.*`, `usage.percpu`, `usage.system` |
| **Memory** | `active_anon`, `active_file`, `cache`, `dirty`, `inactive_anon`, `inactive_file`, `pgfault`, `pgmajfault`, `rss`, `writeback` |
| **Network** | `rx_errors`, `rx_packets`, `tx_errors`, `tx_packets` |
| **Container** | `restarts`, `uptime`, `pids.count`, `pids.limit` |

### Metric Attributes

| Attribute | Values | Description |
| --------- | ------ | ----------- |
| `device_major` | Device number | Major device number |
| `device_minor` | Device number | Minor device number |
| `operation` | `read`, `write`, `sync`, `async`, `discard`, `total` | Block I/O operation |
| `interface` | Interface name | Network interface |

### Resource Attributes

| Attribute | Description | Default |
| --------- | ----------- | ------- |
| `container.id` | Container ID | Enabled |
| `container.name` | Container name | Enabled |
| `container.hostname` | Container hostname | Enabled |
| `container.image.name` | Container image name | Enabled |
| `container.image.id` | Container image ID | Enabled |
| `container.runtime` | Container runtime | Enabled |
| `container.command_line` | Container command line | Disabled |

## Metrics Not Used in Dashboards

The following default metrics are available but not currently visualized in the dashboards:

| Metric | Type | Unit | Description | Attributes |
|--------|------|------|-------------|------------|
| `container.cpu.usage.kernelmode` | Sum | `ns` | CPU time in kernel mode | — |
| `container.cpu.usage.usermode` | Sum | `ns` | CPU time in user mode | — |
| `container.memory.file` | Sum | `By` | Filesystem cache memory (cgroups v2) | — |
| `container.memory.total_cache` | Sum | `By` | Memory with block devices | — |
| `container.network.io.usage.rx_dropped` | Sum | `{packets}` | Incoming packets dropped | `interface` |
| `container.network.io.usage.tx_dropped` | Sum | `{packets}` | Outgoing packets dropped | `interface` |

All optional metrics (60+) listed in the "Optional Metrics" section above are also not used in the current dashboards. See the [OpenTelemetry Docker Stats Receiver documentation](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/dockerstatsreceiver) for details on enabling these metrics.

## Related Resources

- [OpenTelemetry Docker Stats Receiver](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/dockerstatsreceiver)
