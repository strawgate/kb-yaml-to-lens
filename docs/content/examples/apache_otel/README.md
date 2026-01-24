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
- **Kibana**: Version 8.x or later

## Data Requirements

- **Data stream dataset**: `apachereceiver.otel`
- **Data view**: `metrics-*`

## Usage

1. Configure the Apache receiver in your OpenTelemetry Collector
2. Ensure metrics are being sent to Elasticsearch
3. Compile and upload the dashboard:

   ```bash
   kb-dashboard compile --input-dir docs/content/examples/apache_otel/ --upload
   ```

## Related Resources

- [OpenTelemetry Apache Receiver](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/apachereceiver)
