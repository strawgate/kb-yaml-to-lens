# MySQL OpenTelemetry Dashboards

MySQL database monitoring dashboards using OpenTelemetry MySQL receiver metrics.

## Overview

These dashboards provide comprehensive monitoring for MySQL database instances, including connections, buffer pool efficiency, query performance, and InnoDB metrics.

## Dashboards

| Dashboard | File | Description |
|-----------|------|-------------|
| **Overview (Lens)** | `mysql-overview-lens.yaml` | Comprehensive MySQL metrics using Lens visualizations |
| **Overview (ES\|QL)** | `mysql-overview-esql.yaml` | MySQL metrics using ES\|QL queries |

Both dashboards include navigation links for easy switching between views.

## Prerequisites

- **MySQL**: MySQL 5.7+ or 8.x database server
- **OpenTelemetry Collector**: Collector Contrib with MySQL receiver configured
- **Kibana**: Version 8.x or later

## Data Requirements

Dashboards expect metrics from the OpenTelemetry MySQL receiver:

- **Data stream dataset**: `mysqlreceiver.otel`
- **Data view**: `metrics-*`

### Key Metrics

| Metric | Description |
|--------|-------------|
| `mysql.threads` | Thread counts (connected, running, etc.) |
| `mysql.buffer_pool.*` | InnoDB buffer pool metrics |
| `mysql.commands` | Command execution counts |
| `mysql.queries` | Query statistics |

### Key Attributes

- `resource.attributes.host.name` - MySQL host name
- `resource.attributes.service.instance.id` - MySQL instance identifier

## Configuration Example

```yaml
receivers:
  mysql:
    endpoint: localhost:3306
    username: ${env:MYSQL_USERNAME}
    password: ${env:MYSQL_PASSWORD}
    collection_interval: 10s

exporters:
  elasticsearch:
    endpoints: ["https://your-elasticsearch-instance:9200"]

service:
  pipelines:
    metrics:
      receivers: [mysql]
      exporters: [elasticsearch]
```

## Usage

1. Configure the MySQL receiver in your OpenTelemetry Collector
2. Ensure metrics are being sent to Elasticsearch
3. Compile the dashboards:

   ```bash
   kb-dashboard compile --input-dir docs/content/examples/mysql_otel/
   ```

4. Upload to Kibana:

   ```bash
   kb-dashboard compile --input-dir docs/content/examples/mysql_otel/ --upload
   ```

## Dashboard Controls

The dashboards include interactive controls for filtering:

- **MySQL Host**: Filter by MySQL server host
- **MySQL Instance**: Filter by MySQL instance ID

## Related Resources

- [OpenTelemetry MySQL Receiver](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/mysqlreceiver)
