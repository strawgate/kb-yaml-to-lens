# Docker OpenTelemetry Dashboards

This directory contains YAML dashboards for the Docker OpenTelemetry integration, based on the dashboards from the [Elastic integrations repository](https://github.com/elastic/integrations/tree/main/packages/docker_otel).

## Dashboards

1. **01-containers-overview.yaml** - Overview of all containers with key metrics and resource utilization
2. **02-container-stats.yaml** - Detailed performance statistics for individual containers

## Features

These dashboards provide comprehensive monitoring for Docker containers using OpenTelemetry metrics:

### Containers Overview Dashboard

- Active and total container counts
- Container timeline showing count over time
- Container distribution by runtime, image, and name
- Resource utilization charts:
  - CPU usage across containers
  - Memory usage across containers
  - Disk I/O read and write operations
  - Network I/O received and transmitted bytes

### Container Stats Dashboard

- Detailed metrics for selected containers
- Container information table with CPU and memory metrics
- Performance charts:
  - CPU utilization percentage
  - Memory utilization percentage
  - Memory usage in bytes
  - Disk I/O read and write operations by device
  - Network I/O received and transmitted bytes

### Dashboard Controls

Both dashboards include hierarchical filter controls for:

- Container Image
- Container Name
- Hostname
- Container ID

## Data Requirements

These dashboards expect data from the OpenTelemetry Docker Stats Receiver with the following fields:

### Metrics

- `container.cpu.utilization` - CPU utilization percentage
- `container.memory.usage.total` - Total memory usage in bytes
- `container.memory.percent` - Memory utilization percentage
- `container.memory.usage.limit` - Memory limit in bytes (may not be available for containers without explicit memory limits)
- `container.blockio.io_service_bytes_recursive` - Disk I/O bytes (filtered by `attributes.operation`: "read" or "write")
- `container.network.io.usage.rx_bytes` - Network bytes received
- `container.network.io.usage.tx_bytes` - Network bytes transmitted

### Resource Attributes

- `container.id` - Container identifier
- `container.name` - Container name
- `container.image.name` - Container image name
- `container.runtime` - Container runtime (e.g., docker, containerd)
- `container.hostname` - Container hostname
- `attributes.device_major` - Major device number for disk I/O metrics
- `attributes.interface` - Network interface name for network I/O metrics

### Data View

The dashboards use the `metrics-*` data view and filter for `data_stream.dataset: dockerstatsreceiver.otel`.

## Source

These dashboards are based on the official Elastic integrations repository:

- [Docker OTel Package](https://github.com/elastic/integrations/tree/main/packages/docker_otel)
- Original JSON dashboards converted to YAML format using the kb-yaml-to-lens compiler
