# Apache HTTP Server OpenTelemetry Dashboards

Dashboards for monitoring Apache HTTP Server using OpenTelemetry metrics collected by the Apache receiver.

## Overview

These dashboards provide comprehensive monitoring for Apache HTTP Server 2.4.13+ installations, displaying metrics collected via the `server-status?auto` endpoint by the OpenTelemetry Collector's Apache receiver.

## Dashboards

| Dashboard | File | Description |
|-----------|------|-------------|
| **Overview** | `01-apache-overview.yaml` | Apache HTTP Server performance and health metrics |

## Dashboard Definitions

<!-- markdownlint-disable MD046 -->
??? example "Overview (01-apache-overview.yaml)"

    ```yaml
    --8<-- "examples/apache_otel/01-apache-overview.yaml"
    ```
<!-- markdownlint-enable MD046 -->

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

All metrics are enabled by default.

| Metric | Type | Unit | Description | Attributes |
|--------|------|------|-------------|------------|
| `apache.requests` | Sum | `{requests}` | Number of requests serviced | — |
| `apache.traffic` | Sum | `By` | Total HTTP server traffic | — |
| `apache.current_connections` | Sum | `{connections}` | Number of active connections currently attached | — |
| `apache.connections.async` | Gauge | `{connections}` | Number of connections in different asynchronous states | `connection_state` |
| `apache.uptime` | Sum | `s` | Time the server has been running | — |
| `apache.cpu.load` | Gauge | `%` | Current processor load | — |
| `apache.cpu.time` | Sum | `{jiff}` | Jiffs used by processes of given category | `level`, `mode` |
| `apache.request.time` | Sum | `ms` | Total time spent on handling requests | — |
| `apache.load.1` | Gauge | `%` | Average server load over last 1 minute | — |
| `apache.load.5` | Gauge | `%` | Average server load over last 5 minutes | — |
| `apache.load.15` | Gauge | `%` | Average server load over last 15 minutes | — |
| `apache.workers` | Sum | `{workers}` | Number of workers currently attached | `state` |
| `apache.scoreboard` | Sum | `{workers}` | Count of workers decoded from Apache's scoreboard | `state` |

### Metric Attributes

| Attribute | Values | Description |
| --------- | ------ | ----------- |
| `connection_state` | `writing`, `keepalive`, `closing` | Async connection state |
| `level` | `self`, `children` | CPU level |
| `mode` | `system`, `user` | CPU mode |
| `state` (workers) | `busy`, `idle` | Worker state |
| `state` (scoreboard) | `open`, `waiting`, `starting`, `reading`, `sending`, `keepalive`, `dnslookup`, `closing`, `logging`, `finishing`, `idle_cleanup`, `unknown` | Scoreboard state |

### Resource Attributes

| Attribute | Description |
| --------- | ----------- |
| `apache.server.name` | Apache HTTP server name |
| `apache.server.port` | Apache HTTP server port |

## Related Resources

- [OpenTelemetry Apache Receiver](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/apachereceiver)
