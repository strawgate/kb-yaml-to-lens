# System OpenTelemetry Dashboards

Comprehensive host monitoring dashboards for OpenTelemetry Host Metrics Receiver.

## Overview

These dashboards provide monitoring for infrastructure with OpenTelemetry, covering CPU, memory, disk, network, and host metadata.

**Note:** Based on the [Elastic integrations repository](https://github.com/elastic/integrations/tree/main/packages/system_otel) dashboards. Licensed under [Elastic License 2.0](../../licenses/ELASTIC-LICENSE-2.0.txt).

## Dashboards

| Dashboard | File | Description |
|-----------|------|-------------|
| **Hosts Overview** | `01-hosts-overview.yaml` | Overview of all hosts with key performance metrics |
| **Host Details - Overview** | `02-host-details-overview.yaml` | Detailed single host overview with CPU, memory, and disk metrics |
| **Host Details - Metrics** | `03-host-details-metrics.yaml` | In-depth metrics charts for CPU, memory, disk, and load |
| **Host Details - Metadata** | `04-host-details-metadata.yaml` | Host resource attributes and metadata (ES\|QL datatables) |
| **Host Details - Logs** | `05-host-details-logs.yaml` | Host log messages (ES\|QL datatable) |

All dashboards include navigation links for easy switching between views.

## Prerequisites

- **OpenTelemetry Collector**: Collector with Host Metrics receiver configured
- **Kibana**: Version 8.x or later

## Data Requirements

Dashboards expect metrics from the OpenTelemetry Host Metrics receiver:

- **Data stream dataset**: `hostmetricsreceiver.otel`
- **Data view**: `metrics-*`

### Key Attributes

- `resource.attributes.host.name` - Host identifier
- `resource.attributes.os.type` - Operating system type

### Key Metrics

| Metric | Description |
|--------|-------------|
| `system.cpu.utilization` | CPU utilization percentage |
| `system.memory.usage` | Memory usage |
| `system.disk.*` | Disk I/O metrics |
| `system.network.*` | Network traffic metrics |
| `system.filesystem.*` | Filesystem usage metrics |

## Configuration Example

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

## Usage

1. Configure the Host Metrics receiver in your OpenTelemetry Collector
2. Ensure metrics are being sent to Elasticsearch
3. Compile the dashboards:

   ```bash
   kb-dashboard compile --input-dir docs/content/examples/system_otel/
   ```

4. Upload to Kibana:

   ```bash
   kb-dashboard compile --input-dir docs/content/examples/system_otel/ --upload
   ```

## Related Resources

- [OpenTelemetry Host Metrics Receiver](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/hostmetricsreceiver)
