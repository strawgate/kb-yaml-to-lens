# MySQL OpenTelemetry Dashboards

MySQL database monitoring dashboards using OpenTelemetry MySQL receiver metrics.

## Overview

These dashboards provide comprehensive monitoring for MySQL database instances, including connections, buffer pool efficiency, query performance, and InnoDB metrics.

## Dashboards

| Dashboard | File | Description |
|-----------|------|-------------|
| **Overview** | `mysql-overview-esql.yaml` | Comprehensive MySQL metrics using ES\|QL queries |
| **Extended** | `mysql-extended-esql.yaml` | Extended MySQL metrics for optional/disabled metrics |

Both dashboards include navigation links for easy switching between views.

## Prerequisites

- **MySQL**: MySQL 5.7+ or 8.x database server
- **OpenTelemetry Collector**: Collector Contrib with MySQL receiver configured
- **Kibana**: Version 9.2 or later (dashboards use ES|QL TS command)

## Data Requirements

- **Data stream dataset**: `mysqlreceiver.otel`
- **Data view**: `metrics-*`

## OpenTelemetry Collector Configuration

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

## Metrics Reference

| Metric | Description |
|--------|-------------|
| `mysql.threads` | Thread counts (connected, running, etc.) |
| `mysql.buffer_pool.*` | InnoDB buffer pool metrics |
| `mysql.commands` | Command execution counts |
| `mysql.queries` | Query statistics |

### Attributes

| Attribute | Description |
| --------- | ----------- |
| `resource.attributes.host.name` | MySQL host name |
| `resource.attributes.service.instance.id` | MySQL instance identifier |

## Related Resources

- [OpenTelemetry MySQL Receiver](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/mysqlreceiver)
