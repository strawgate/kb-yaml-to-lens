# Aerospike Monitoring Dashboards

Monitoring dashboards for Aerospike NoSQL database using OpenTelemetry metrics with ES|QL queries.

## Overview

These dashboards provide comprehensive monitoring for Aerospike clusters, including cluster-level health metrics, per-node performance, and namespace-level storage and query statistics. All dashboards use ES|QL with the `TS` (time series) command for optimized time series analysis.

## Dashboards

| Dashboard | File | Description |
|-----------|------|-------------|
| **Overview** | `overview.yaml` | Cluster-level metrics and node health monitoring |
| **Node Metrics** | `node-metrics.yaml` | Detailed per-node performance monitoring |
| **Namespace Metrics** | `namespace-metrics.yaml` | Namespace-level storage and query statistics |

All dashboards include navigation links for easy switching between views.

## Prerequisites

- **Aerospike**: Aerospike database cluster
- **OpenTelemetry Collector**: Collector with Aerospike receiver configured
- **Kibana**: Version 8.x or later with ES|QL support

## Data Requirements

Dashboards expect metrics from the OpenTelemetry Aerospike receiver:

- **Data stream dataset**: `aerospikereceiver.otel`
- **Data view**: `metrics-*`

### Key Metrics

| Metric | Description |
| ------ | ----------- |
| `aerospike.node.name` | Node identifier |
| `aerospike.node.memory.free` | Free memory on the node |
| `aerospike.node.memory.used` | Used memory on the node |
| `aerospike.node.connection.open` | Open connections on the node |
| `aerospike.node.connection.count` | Connection count on the node |
| `aerospike.namespace` | Namespace identifier |
| `aerospike.namespace.memory.usage` | Memory usage per namespace |
| `aerospike.namespace.memory.free` | Free memory per namespace |
| `aerospike.namespace.disk.available` | Available disk per namespace |
| `aerospike.namespace.query.count` | Query count per namespace |
| `aerospike.namespace.transaction.count` | Transaction count per namespace |

### Key Attributes

| Attribute | Description |
| --------- | ----------- |
| `aerospike.node.name` | Node name |
| `aerospike.namespace` | Namespace name |
| `attributes.type` | Connection or transaction type |
| `attributes.index` | Index type (primary/secondary) |

## ES|QL Features

These dashboards use ES|QL queries with the following features:

- **`TS` command**: Time series optimized queries for efficient time-based analysis
- **`TBUCKET()`**: Automatic time bucketing for time series visualizations
- **`RATE()`**: Native rate calculations for counter metrics
- **`AVG_OVER_TIME()`**: Time-weighted averages for gauge metrics
- **`FROM` queries**: Aggregation queries for KPI metrics and data tables

## Setup

### Docker - Aerospike

```bash
docker run -d \
  --name aerospike-test \
  -p 3000:3000 \
  aerospike/aerospike-server:latest
```

### OpenTelemetry Collector Configuration

```yaml
receivers:
  aerospike:
    endpoint: localhost:3000
    collection_interval: 60s
    metrics:
      aerospike.node.memory.free:
        enabled: true
      aerospike.node.memory.used:
        enabled: true
      aerospike.node.connection.open:
        enabled: true
      aerospike.node.connection.count:
        enabled: true
      aerospike.namespace.memory.usage:
        enabled: true
      aerospike.namespace.memory.free:
        enabled: true
      aerospike.namespace.disk.available:
        enabled: true
      aerospike.namespace.query.count:
        enabled: true
      aerospike.namespace.transaction.count:
        enabled: true
```

## Usage

1. Configure the Aerospike receiver in your OpenTelemetry Collector
2. Ensure metrics are being sent to Elasticsearch
3. Compile the dashboards:

   ```bash
   kb-dashboard compile --input-dir docs/content/examples/aerospike/
   ```

4. Upload to Kibana:

   ```bash
   kb-dashboard compile --input-dir docs/content/examples/aerospike/ --upload
   ```

## Filters

All dashboards include controls for filtering by:

- **Node**: Filter to specific Aerospike node(s)
- **Namespace**: Filter to specific namespace(s) (where applicable)

## Related Resources

- [OpenTelemetry Aerospike Receiver Documentation](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/aerospikereceiver)
- [Elastic Observability](https://www.elastic.co/observability)
- [ES|QL Documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/esql.html)
- [Dashboard Compiler Documentation](../../index.md)
