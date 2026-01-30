# System OpenTelemetry Dashboards

Host monitoring dashboards for OpenTelemetry Host Metrics Receiver.

## Overview

These dashboards provide monitoring for infrastructure with OpenTelemetry, covering CPU, memory, disk, network, and host metadata.

**Note:** Based on the [Elastic integrations repository](https://github.com/elastic/integrations/tree/main/packages/system_otel) dashboards. Licensed under [Elastic License 2.0](../../licenses/ELASTIC-LICENSE-2.0.txt).

## Dashboards

| Dashboard | File | Description |
|-----------|------|-------------|
| **Hosts Overview** | `01-hosts-overview.yaml` | Overview of all hosts with key performance metrics |
| **Host Details - Overview** | `02-host-details-overview.yaml` | Detailed single host overview with CPU, memory, and disk metrics |
| **Host Details - Metrics** | `03-host-details-metrics.yaml` | In-depth metrics charts for CPU, memory, disk, and load |
| **Host Details - Metadata** | `04-host-details-metadata.yaml` | Host resource attributes and metadata |
| **Host Details - Logs** | `05-host-details-logs.yaml` | Host log messages |

All dashboards include navigation links for easy switching between views.

## Dashboard Definitions

<!-- markdownlint-disable MD046 -->
??? example "Hosts Overview (01-hosts-overview.yaml)"

    ```yaml
    --8<-- "examples/system_otel/01-hosts-overview.yaml"
    ```

??? example "Host Details - Overview (02-host-details-overview.yaml)"

    ```yaml
    --8<-- "examples/system_otel/02-host-details-overview.yaml"
    ```

??? example "Host Details - Metrics (03-host-details-metrics.yaml)"

    ```yaml
    --8<-- "examples/system_otel/03-host-details-metrics.yaml"
    ```

??? example "Host Details - Metadata (04-host-details-metadata.yaml)"

    ```yaml
    --8<-- "examples/system_otel/04-host-details-metadata.yaml"
    ```

??? example "Host Details - Logs (05-host-details-logs.yaml)"

    ```yaml
    --8<-- "examples/system_otel/05-host-details-logs.yaml"
    ```
<!-- markdownlint-enable MD046 -->

## Prerequisites

- **OpenTelemetry Collector**: Collector with Host Metrics receiver configured
- **Kibana**: Version 8.x or later

## Data Requirements

- **Data stream dataset**: `hostmetricsreceiver.otel`
- **Data view**: `metrics-*`

## OpenTelemetry Collector Configuration

```yaml
receivers:
  hostmetrics:
    collection_interval: 10s
    scrapers:
      cpu:
      memory:
      disk:
      filesystem:
      network:
      load:

exporters:
  elasticsearch:
    endpoints: ["https://your-elasticsearch-instance:9200"]

service:
  pipelines:
    metrics:
      receivers: [hostmetrics]
      exporters: [elasticsearch]
```

## Metrics Reference

### CPU Metrics

| Metric | Type | Unit | Description | Attributes |
|--------|------|------|-------------|------------|
| `system.cpu.time` | Sum | `s` | Seconds each logical CPU spent on each mode | `cpu`, `state` |
| `system.cpu.utilization` | Gauge | `1` | CPU usage difference per logical CPU (0-1) | `cpu`, `state` |
| `system.cpu.load_average.1m` | Gauge | `{thread}` | Average CPU load over 1 minute | — |
| `system.cpu.load_average.5m` | Gauge | `{thread}` | Average CPU load over 5 minutes | — |
| `system.cpu.load_average.15m` | Gauge | `{thread}` | Average CPU load over 15 minutes | — |
| `system.cpu.logical.count` | Sum | `{cpu}` | Number of available logical CPUs (optional) | — |
| `system.cpu.physical.count` | Sum | `{cpu}` | Number of available physical CPUs (optional) | — |
| `system.cpu.frequency` | Gauge | `Hz` | Current CPU frequency (optional) | `cpu` |

### Memory Metrics

| Metric | Type | Unit | Description | Attributes |
|--------|------|------|-------------|------------|
| `system.memory.usage` | Sum | `By` | Bytes of memory in use | `state` |
| `system.memory.utilization` | Gauge | `1` | Percentage of memory in use (optional) | `state` |
| `system.memory.limit` | Sum | `By` | Total bytes of memory (optional) | — |
| `system.linux.memory.available` | Sum | `By` | Available memory estimate (Linux, optional) | — |

### Disk Metrics

| Metric | Type | Unit | Description | Attributes |
|--------|------|------|-------------|------------|
| `system.disk.io` | Sum | `By` | Disk bytes transferred | `device`, `direction` |
| `system.disk.operations` | Sum | `{operations}` | Disk operations count | `device`, `direction` |
| `system.disk.io_time` | Sum | `s` | Time disk spent activated | `device` |
| `system.disk.operation_time` | Sum | `s` | Time spent in disk operations | `device`, `direction` |
| `system.disk.pending_operations` | Sum | `{operations}` | Queue size of pending I/O operations | `device` |
| `system.disk.merged` | Sum | `{operations}` | Merged disk operations | `device`, `direction` |
| `system.disk.weighted_io_time` | Sum | `s` | Weighted I/O time | `device` |

### Filesystem Metrics

| Metric | Type | Unit | Description | Attributes |
|--------|------|------|-------------|------------|
| `system.filesystem.usage` | Sum | `By` | Filesystem bytes used | `device`, `mode`, `mountpoint`, `type`, `state` |
| `system.filesystem.utilization` | Gauge | `1` | Fraction of filesystem used (optional) | `device`, `mode`, `mountpoint`, `type` |
| `system.filesystem.inodes.usage` | Sum | `{inodes}` | Filesystem inodes used | `device`, `mode`, `mountpoint`, `type`, `state` |

### Network Metrics

| Metric | Type | Unit | Description | Attributes |
|--------|------|------|-------------|------------|
| `system.network.io` | Sum | `By` | Bytes transmitted and received | `device`, `direction` |
| `system.network.packets` | Sum | `{packets}` | Packets transferred | `device`, `direction` |
| `system.network.dropped` | Sum | `{packets}` | Packets dropped | `device`, `direction` |
| `system.network.errors` | Sum | `{errors}` | Errors encountered | `device`, `direction` |
| `system.network.connections` | Sum | `{connections}` | Number of connections | `protocol`, `state` |
| `system.network.conntrack.count` | Sum | `{entries}` | Conntrack table entries (optional) | — |
| `system.network.conntrack.max` | Sum | `{entries}` | Conntrack table limit (optional) | — |

### Metric Attributes

| Attribute | Values | Description |
| --------- | ------ | ----------- |
| `cpu` | `0`, `1`, `2`, ... | Logical CPU number |
| `state` (cpu) | `idle`, `interrupt`, `nice`, `softirq`, `steal`, `system`, `user`, `wait` | CPU state |
| `state` (memory) | `buffered`, `cached`, `free`, `inactive`, `slab_reclaimable`, `slab_unreclaimable`, `used` | Memory state |
| `state` (filesystem) | `free`, `reserved`, `used` | Filesystem state |
| `device` | Device name | Disk, filesystem, or network device |
| `direction` | `read`/`write` (disk), `receive`/`transmit` (network) | I/O direction |
| `mountpoint` | Mount path | Filesystem mount point |
| `type` | `ext4`, `xfs`, `ntfs`, etc. | Filesystem type |
| `mode` | `rw`, `ro` | Filesystem mode |
| `protocol` | `tcp`, `udp` | Network protocol |
| `state` (connections) | TCP connection states | Connection state |

### Resource Attributes

| Attribute | Description |
| --------- | ----------- |
| `host.name` | Host identifier |
| `os.type` | Operating system type |

## Metrics Not Used in Dashboards

The following metrics are available from the Host Metrics receiver but are not currently visualized in the dashboards:

### Default Metrics Not Used

| Metric | Type | Unit | Description | Attributes |
|--------|------|------|-------------|------------|
| `system.cpu.time` | Sum | `s` | Seconds each logical CPU spent on each mode | `cpu`, `state` |
| `system.memory.usage` | Sum | `By` | Bytes of memory in use | `state` |
| `system.disk.operation_time` | Sum | `s` | Time spent in disk operations | `device`, `direction` |
| `system.disk.pending_operations` | Sum | `{operations}` | Queue size of pending I/O operations | `device` |
| `system.disk.merged` | Sum | `{operations}` | Merged disk operations | `device`, `direction` |
| `system.disk.weighted_io_time` | Sum | `s` | Weighted I/O time | `device` |
| `system.filesystem.usage` | Sum | `By` | Filesystem bytes used | `device`, `mode`, `mountpoint`, `type`, `state` |
| `system.filesystem.inodes.usage` | Sum | `{inodes}` | Filesystem inodes used | `device`, `mode`, `mountpoint`, `type`, `state` |
| `system.network.connections` | Sum | `{connections}` | Number of connections | `protocol`, `state` |

### Optional Metrics Not Used

| Metric | Type | Unit | Description | Attributes |
|--------|------|------|-------------|------------|
| `system.cpu.physical.count` | Sum | `{cpu}` | Number of available physical CPUs | — |
| `system.cpu.frequency` | Gauge | `Hz` | Current CPU frequency | `cpu` |
| `system.memory.limit` | Sum | `By` | Total bytes of memory | — |
| `system.linux.memory.available` | Sum | `By` | Available memory estimate (Linux) | — |
| `system.network.conntrack.count` | Sum | `{entries}` | Conntrack table entries | — |
| `system.network.conntrack.max` | Sum | `{entries}` | Conntrack table limit | — |

## Related Resources

- [OpenTelemetry Host Metrics Receiver](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/hostmetricsreceiver)
