# Apache HTTP Server OpenTelemetry Dashboards

This directory contains dashboards for monitoring Apache HTTP Server using OpenTelemetry metrics collected by the Apache receiver.

## Overview

These dashboards provide comprehensive monitoring for Apache HTTP Server 2.4.13+ installations, displaying metrics collected via the `server-status?auto` endpoint by the OpenTelemetry Collector's Apache receiver.

## Upstream Documentation

- [OpenTelemetry Apache Receiver](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/apachereceiver)
- [Apache receiver metadata](https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/main/receiver/apachereceiver/metadata.yaml)

## Configuration Example

To collect Apache metrics with OpenTelemetry, configure the Apache receiver in your OpenTelemetry Collector:

```yaml
receivers:
  apache:
    endpoint: "http://localhost/server-status?auto"
    collection_interval: 10s

processors:
  resource:
    attributes:
      - key: server.address
        from_attribute: apache.server.name
        action: upsert
      - key: server.port
        from_attribute: apache.server.port
        action: upsert

exporters:
  elasticsearch:
    endpoints: ["https://your-elasticsearch-instance:9200"]
    # Additional Elasticsearch configuration...

service:
  pipelines:
    metrics:
      receivers: [apache]
      processors: [resource]
      exporters: [elasticsearch]
```

## Dashboards

### 01-apache-overview.yaml

Main overview dashboard displaying Apache HTTP Server performance and health metrics using ES|QL queries with the `TS` (time series) command for optimized time series analysis.

**Sections:**

- **Overview Metrics**: Request rate, traffic, connections, uptime, and current CPU load
- **Time Series**: Request and traffic rates over time
- **Performance**: CPU time and request processing time
- **Health**: CPU load averages (1/5/15 min), connection metrics, uptime trends
- **Capacity**: Async connections by state, worker distribution, scoreboard status
- **Workers**: Worker states over time
- **Summary**: Server performance data table

## Metrics Covered

The dashboards visualize the following Apache HTTP Server metrics:

| Metric | Description | Type | Unit |
|--------|-------------|------|------|
| `apache.requests` | Total requests serviced | Sum | requests |
| `apache.traffic` | Total HTTP server traffic | Sum | bytes |
| `apache.current_connections` | Active connections | Sum | connections |
| `apache.connections.async` | Async connections by state (writing, keepalive, closing) | Gauge | connections |
| `apache.uptime` | Server uptime | Sum | seconds |
| `apache.cpu.load` | Current CPU load percentage | Gauge | percent |
| `apache.cpu.time` | CPU time by level and mode | Sum | {jiff} |
| `apache.request.time` | Total request processing time | Sum | ms |
| `apache.load.1` | Server load (1 minute average) | Gauge | percent |
| `apache.load.5` | Server load (5 minute average) | Gauge | percent |
| `apache.load.15` | Server load (15 minute average) | Gauge | percent |
| `apache.workers` | Workers by state | Sum | workers |
| `apache.scoreboard` | Scoreboard by state | Sum | workers |

## Attributes

Key attributes used for breakdowns and filtering:

- `server.address` - Apache server hostname/address
- `server.port` - Apache server port
- `attributes.connection_state` - Async connection state (writing, keepalive, closing)
- `attributes.workers_state` - Worker state
- `attributes.scoreboard_state` - Scoreboard state
- `attributes.cpu_level` - CPU level (system, user, children)
- `attributes.cpu_mode` - CPU mode

## Prerequisites

- Apache HTTP Server 2.4.13 or later
- Apache `mod_status` module enabled with `ExtendedStatus On`
- OpenTelemetry Collector with Apache receiver configured
- Metrics ingested into Elasticsearch with data view pattern `metrics-*`
- Data stream dataset: `apachereceiver.otel`

## Usage

1. Configure the Apache receiver in your OpenTelemetry Collector
2. Ensure metrics are being sent to Elasticsearch
3. Compile the dashboard:

   ```bash
   kb-dashboard compile --input-file docs/content/examples/apache_otel/01-apache-overview.yaml
   ```

4. Upload to Kibana:

   ```bash
   kb-dashboard compile --input-file docs/content/examples/apache_otel/01-apache-overview.yaml --upload
   ```

## Dashboard Controls

The dashboard includes interactive controls for filtering:

- **Server Address**: Filter by Apache server address
- **Server Port**: Filter by Apache server port

These controls allow you to focus on specific servers in multi-server environments.
