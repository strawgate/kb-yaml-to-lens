# Docker OpenTelemetry Dashboards

Docker container monitoring dashboards using OpenTelemetry Docker Stats Receiver metrics.

## Overview

These dashboards provide comprehensive monitoring for Docker containers including CPU, memory, disk I/O, and network metrics.

**Note:** Based on the [Elastic integrations repository](https://github.com/elastic/integrations/tree/main/packages/docker_otel) dashboards. Licensed under [Elastic License 2.0](../../licenses/ELASTIC-LICENSE-2.0.txt).

## Dashboards

| Dashboard | File | Description |
|-----------|------|-------------|
| **Containers Overview** | `01-containers-overview.yaml` | Multi-container monitoring with CPU, memory, disk I/O, and network metrics |
| **Container Stats** | `02-container-stats.yaml` | Detailed single-container performance analysis and resource utilization |

All dashboards include navigation links for easy switching between views.

## Prerequisites

- **Docker**: Docker Engine with containers running
- **OpenTelemetry Collector**: Collector Contrib with Docker Stats receiver configured
- **Kibana**: Version 8.x or later

## Data Requirements

- **Data stream dataset**: `dockerstatsreceiver.otel`
- **Data view**: `metrics-*`

### Key Attributes

| Attribute | Description |
| --------- | ----------- |
| `container.image.name` | Container image name |
| `container.name` | Container name |
| `container.hostname` | Container hostname |
| `container.id` | Container ID |

## Usage

1. Configure the Docker Stats receiver in your OpenTelemetry Collector
2. Ensure metrics are being sent to Elasticsearch
3. Compile and upload the dashboards:

   ```bash
   kb-dashboard compile --input-dir docs/content/examples/docker_otel/ --upload
   ```
