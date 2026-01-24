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

- **Data stream dataset**: `aerospikereceiver.otel`
- **Data view**: `metrics-*`

## Usage

1. Configure the Aerospike receiver in your OpenTelemetry Collector
2. Ensure metrics are being sent to Elasticsearch
3. Compile and upload the dashboards:

   ```bash
   kb-dashboard compile --input-dir docs/content/examples/aerospike/ --upload
   ```

## Related Resources

- [OpenTelemetry Aerospike Receiver Documentation](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/aerospikereceiver)
- [Dashboard Compiler Documentation](../../index.md)
