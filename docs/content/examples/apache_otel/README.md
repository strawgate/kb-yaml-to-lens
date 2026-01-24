# Apache HTTP Server OpenTelemetry Dashboards

Dashboards for monitoring Apache HTTP Server using OpenTelemetry metrics collected by the Apache receiver.

## Overview

These dashboards provide comprehensive monitoring for Apache HTTP Server 2.4.13+ installations, displaying metrics collected via the `server-status?auto` endpoint by the OpenTelemetry Collector's Apache receiver.

## Dashboards

| Dashboard | File | Description |
|-----------|------|-------------|
| **Overview** | `01-apache-overview.yaml` | Apache HTTP Server performance and health metrics |

## Prerequisites

- **Apache HTTP Server**: Version 2.4.13 or later with `mod_status` enabled
- **OpenTelemetry Collector**: Collector with Apache receiver configured
- **Kibana**: Version 9.2 or later (dashboards use ES|QL TS command)

## Data Requirements

- **Data stream dataset**: `apachereceiver.otel`
- **Data view**: `metrics-*`

## OpenTelemetry Collector Configuration

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

## Metrics Reference

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

### Attributes

| Attribute | Description |
| --------- | ----------- |
| `server.address` | Apache server hostname/address |
| `server.port` | Apache server port |
| `attributes.connection_state` | Async connection state (writing, keepalive, closing) |
| `attributes.workers_state` | Worker state |
| `attributes.scoreboard_state` | Scoreboard state |
| `attributes.cpu_level` | CPU level (system, user, children) |
| `attributes.cpu_mode` | CPU mode |

## Related Resources

- [OpenTelemetry Apache Receiver](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/apachereceiver)
