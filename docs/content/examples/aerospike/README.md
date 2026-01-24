# Aerospike Monitoring Dashboards

Monitoring dashboards for Aerospike NoSQL database using OpenTelemetry metrics.

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
- **Kibana**: Version 8.x or later

## Data Requirements

Dashboards expect metrics from the OpenTelemetry Aerospike receiver:

- **Data stream dataset**: `aerospikereceiver.otel`
- **Data view**: `metrics-*`

### Key Metrics

- `aerospike.node.name` - Node identifier
- Node-level performance metrics
- Namespace storage and query statistics

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
