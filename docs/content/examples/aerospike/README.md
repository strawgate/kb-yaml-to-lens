# Aerospike Monitoring Dashboards

Monitoring dashboards for Aerospike NoSQL database using OpenTelemetry metrics with ES|QL queries.

## Overview

These dashboards provide comprehensive monitoring for Aerospike clusters, including cluster-level health metrics, per-node performance, and namespace-level storage and query statistics.

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
- **Kibana**: Version 9.2.0 or later (required for TS/TBUCKET/RATE/AVG_OVER_TIME)

## Data Requirements

Dashboards expect metrics from the OpenTelemetry Aerospike receiver:

- **Data stream dataset**: `aerospikereceiver.otel`
- **Data view**: `metrics-*`

### Core Metrics (enabled by default)

| Metric | Type | Unit | Description |
| ------ | ---- | ---- | ----------- |
| `aerospike.node.name` | Resource | - | Node identifier |
| `aerospike.node.memory.free` | Gauge | % (0-100) | Percentage of free memory on the node |
| `aerospike.node.connection.open` | Sum | connections | Current open connections (by type) |
| `aerospike.namespace` | Resource | - | Namespace identifier |
| `aerospike.namespace.memory.usage` | Sum | bytes | Memory usage per namespace (by component) |
| `aerospike.namespace.memory.free` | Gauge | % (0-100) | Percentage of free memory per namespace |
| `aerospike.namespace.disk.available` | Gauge | % (0-100) | Percentage of available disk per namespace |

### Counter Metrics (use RATE() for time-series)

| Metric | Unit | Description |
| ------ | ---- | ----------- |
| `aerospike.namespace.query.count` | queries | Query count (by type, index, result) |
| `aerospike.namespace.transaction.count` | transactions | Transaction count (by type, result) |

### Extended Metrics (optional)

| Metric | Unit | Description |
| ------ | ---- | ----------- |
| `aerospike.node.connection.count` | connections | Connection count (by type, operation) |
| `aerospike.node.query.tracked` | queries | Queries exceeding tracking threshold |
| `aerospike.namespace.scan.count` | scans | Scan count (by type, result) |

### Key Attributes

| Attribute | Description |
| --------- | ----------- |
| `aerospike.node.name` | Node name |
| `aerospike.namespace` | Namespace name |
| `attributes.type` | Connection or transaction type |
| `attributes.index` | Index type (primary/secondary) |


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
      aerospike.node.connection.open:
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
