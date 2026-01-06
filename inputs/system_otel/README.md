# OpenTelemetry System Dashboards

This directory contains YAML dashboards for the OpenTelemetry System integration, based on the dashboards from the [Elastic integrations repository](https://github.com/elastic/integrations/tree/main/packages/system_otel).

## Dashboards

1. **01-hosts-overview.yaml** - Overview of all hosts with key metrics
2. **02-host-details-overview.yaml** - Detailed overview of a single host
3. **03-host-details-metrics.yaml** - Detailed metrics charts for a host

**Note:** Two dashboards from the original Elastic integrations set are not included:

- **Host Details - Metadata** - Uses `visualization` panels not yet supported by the compiler
- **Host Details - Logs** - Uses AI-powered panels (`aiopsLogRateAnalysisEmbeddable`, `aiopsPatternAnalysisEmbeddable`) not yet supported by the compiler

## Notes

These YAML dashboards are simplified versions of the original Kibana dashboards. Some advanced features from the original dashboards are not yet supported:

- **AI-powered features**: Log rate analysis and pattern detection panels (excluded from these dashboards)
- **Visualization panels**: Legacy visualization panels (excluded from these dashboards)
- **Dashboard drill-downs**: Clickable table rows that navigate to other dashboards

The dashboards use the `metrics-*` data view.

## Data Requirements

These dashboards expect data from the OpenTelemetry hostmetricsreceiver with the following fields:

### Metrics

- `metrics.system.cpu.utilization`
- `metrics.system.cpu.load_average.1m/5m/15m`
- `metrics.system.cpu.logical.count`
- `metrics.system.memory.utilization`
- `metrics.system.memory.usage`
- `metrics.system.filesystem.utilization`
- `metrics.system.network.io`
- `metrics.system.disk.operations`
- `attributes.state` (CPU and memory states)
- `attributes.device` (network and disk devices)
- `attributes.mountpoint` (filesystem mount points)

### Resource Attributes

- `resource.attributes.host.name`
- `resource.attributes.host.ip`
- `resource.attributes.host.arch`
- `resource.attributes.host.mac`
- `resource.attributes.host.cpu.*` (CPU metadata)
- `resource.attributes.os.type`
- `resource.attributes.os.description`
- `cloud.*` (Cloud metadata fields)
