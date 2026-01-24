# CrowdStrike Security Dashboards

Security monitoring dashboards for CrowdStrike EDR data streams. These dataset-centric dashboards are organized by data source for comprehensive security visibility.

## Overview

These dashboards provide visibility into CrowdStrike Falcon EDR alerts, incidents, vulnerabilities, and host data. Each dashboard focuses on a specific data stream or security domain.

**Note:** Based on the [Elastic integrations repository](https://github.com/elastic/integrations/tree/main/packages/crowdstrike) dashboards. Licensed under [Elastic License 2.0](../../licenses/ELASTIC-LICENSE-2.0.txt).

## Dashboards

| Dashboard | File | Description |
|-----------|------|-------------|
| **Overview** | `overview.yaml` | High-level entry point with navigation to all CrowdStrike dashboards |
| **Alert** | `alert.yaml` | Comprehensive alert monitoring with status, severity, IOCs, and network context |
| **Falcon Overview** | `falcon-overview.yaml` | Falcon incidents with MITRE ATT&CK technique and tactic mapping |
| **FDR Overview** | `fdr-overview.yaml` | Falcon Data Replicator events and alerts monitoring |
| **Host** | `host.yaml` | Host device monitoring with OS platform distribution and activity tracking |
| **Vulnerability** | `vulnerability.yaml` | Vulnerability tracking with severity, status, and confidence breakdowns |

## Prerequisites

- **CrowdStrike Falcon**: EDR solution with data streaming enabled
- **Elastic Agent**: With CrowdStrike integration configured
- **Kibana**: Version 8.x or later

## Data Requirements

Dashboards expect data from the CrowdStrike integration:

- **Data view**: `logs-*`
- **Data stream datasets**:
  - `crowdstrike.fdr` - Falcon Data Replicator
  - `crowdstrike.falcon` - Falcon incidents
  - `crowdstrike.alert` - CrowdStrike alerts
  - `crowdstrike.host` - Host information
  - `crowdstrike.vulnerability` - Vulnerability data

## Usage

1. Configure the CrowdStrike integration in Elastic Agent
2. Ensure data is being ingested to Elasticsearch
3. Compile the dashboards:

   ```bash
   kb-dashboard compile --input-dir docs/content/examples/crowdstrike/
   ```

4. Upload to Kibana:

   ```bash
   kb-dashboard compile --input-dir docs/content/examples/crowdstrike/ --upload
   ```

## Related

See also: [CrowdStrike Modern Dashboards](../crowdstrike-modern/README.md) for workflow-centric SOC dashboards.
