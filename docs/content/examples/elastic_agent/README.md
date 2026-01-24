# Elastic Agent Monitoring Dashboards

Comprehensive monitoring dashboards for Elastic Agent and its input types.

## Overview

These dashboards provide visibility into Elastic Agent health, performance, and input metrics. The bundle includes a central overview dashboard with navigation to detailed input-specific dashboards.

**Note:** Based on the [Elastic integrations repository](https://github.com/elastic/integrations/tree/main/packages/elastic_agent) dashboards. Licensed under [Elastic License 2.0](../../licenses/ELASTIC-LICENSE-2.0.txt).

## Dashboards

### General Dashboards

| Dashboard | File | Description |
|-----------|------|-------------|
| **Overview** | `01-overview.yaml` | High-level entry point with agent counts and integration volume |
| **Agent Metrics** | `02-agent-metrics.yaml` | Detailed agent health, memory, CPU, and event metrics |
| **Concerning Agents** | `03-concerning-agents.yaml` | Agents with high resource usage or errors |
| **Integrations** | `04-integrations.yaml` | Integration-level metrics and status |
| **Input Metrics** | `05-input-metrics.yaml` | Navigation hub for all input-specific dashboards |

### Cloud Storage Input Dashboards

| Dashboard | File | Description |
|-----------|------|-------------|
| **S3 Input** | `06-s3-input-metrics.yaml` | AWS S3 input metrics including SQS messages and object processing |
| **CloudWatch Input** | `07-cloudwatch-input-metrics.yaml` | AWS CloudWatch Logs input metrics |
| **Azure Blob Storage Input** | `08-azure-blob-storage-input-metrics.yaml` | Azure Blob Storage input metrics |
| **Azure Event Hub Input** | `09-azure-eventhub-input-metrics.yaml` | Azure Event Hub input metrics |
| **GCP Storage Input** | `10-gcp-storage-input-metrics.yaml` | Google Cloud Storage input metrics |
| **GCP Pub/Sub Input** | `11-gcp-pubsub-input-metrics.yaml` | Google Cloud Pub/Sub input metrics |

### Network Protocol Input Dashboards

| Dashboard | File | Description |
|-----------|------|-------------|
| **TCP Input** | `12-tcp-input-metrics.yaml` | TCP listener input metrics |
| **UDP Input** | `13-udp-input-metrics.yaml` | UDP listener input metrics |
| **HTTP Endpoint Input** | `14-http-endpoint-input-metrics.yaml` | HTTP endpoint receiver metrics |
| **Unix Socket Input** | `15-unix-input-metrics.yaml` | Unix socket input metrics |
| **Lumberjack Input** | `16-lumberjack-input-metrics.yaml` | Lumberjack protocol input metrics |

### File and Log Input Dashboards

| Dashboard | File | Description |
|-----------|------|-------------|
| **Filestream Input** | `17-filestream-input-metrics.yaml` | File monitoring input metrics |
| **Winlog Input** | `18-winlog-input-metrics.yaml` | Windows Event Log input metrics |
| **ETW Input** | `19-etw-input-metrics.yaml` | Event Tracing for Windows input metrics |
| **Unified Logs Input** | `20-unified-logs-input-metrics.yaml` | macOS Unified Logs input metrics |

### API and Data Processing Input Dashboards

| Dashboard | File | Description |
|-----------|------|-------------|
| **CEL Input** | `21-cel-input-metrics.yaml` | Common Expression Language input metrics |
| **HTTPJSON Input** | `22-httpjson-input-metrics.yaml` | HTTP JSON API polling input metrics |
| **Streaming Input** | `23-streaming-input-metrics.yaml` | Streaming data input metrics |
| **Entity Analytics Input** | `24-entity-analytics-input-metrics.yaml` | Entity analytics input metrics |

## Prerequisites

- **Elastic Agent**: Version 8.x or later with monitoring enabled
- **Kibana**: Version 8.x or later

## Data Requirements

- **Data view**: `metrics-*`
- **Data stream datasets**: `elastic_agent.elastic_agent`, `elastic_agent.filebeat_input`, `elastic_agent.metricbeat_input`

## Usage

Compile all dashboards:

```bash
kb-dashboard compile --input-dir docs/content/examples/elastic_agent
```

Upload directly to Kibana:

```bash
kb-dashboard compile --input-dir docs/content/examples/elastic_agent --upload
```

## Navigation

All dashboards include a navigation panel linking to related dashboards. Start with the **Overview** dashboard to explore your Elastic Agent fleet, then drill down into specific input metrics as needed.
