# CrowdStrike Modern Dashboards

Workflow-centric security operations dashboards designed for modern SOC workflows. These dashboards follow the [Dashboard Style Guide](../../dashboard-style-guide.md) best practices with progressive disclosure pattern, consistent navigation, and control filters.

## Overview

Unlike the dataset-centric [CrowdStrike dashboards](../crowdstrike/README.md), these modern dashboards are organized by security workflow rather than data source, making them ideal for daily SOC operations.

**Design principles:**

- 4-layer hierarchy (Context → Summary → Analysis → Detail)
- Navigation links at top
- Limited metric cards (0-4)
- Appropriate chart types
- Tables at bottom with 10-row pagination
- Controls for filtering

## Dashboards

| Dashboard | File | Description |
|-----------|------|-------------|
| **SOC Dashboard** | `soc.yaml` | Real-time security event monitoring, alert triage, and incident response coordination |
| **Threat Investigation** | `threat-investigation.yaml` | Deep-dive threat analysis with MITRE ATT&CK mapping and IOC tracking |
| **Asset & Vulnerability** | `asset-vulnerability.yaml` | Asset inventory and vulnerability tracking for risk assessment and patch prioritization |
| **Compliance & Audit** | `compliance-audit.yaml` | Compliance monitoring and audit trail analysis for regulatory reporting |

All dashboards include consistent navigation for seamless workflow transitions.

## Prerequisites

- **CrowdStrike Falcon**: EDR solution with data streaming enabled
- **Elastic Agent**: With CrowdStrike integration configured
- **Kibana**: Version 8.x or later

## Data Requirements

Dashboards expect data from the CrowdStrike integration:

- **Data view**: `logs-*`
- **Data stream datasets**:
  - `crowdstrike.alert`
  - `crowdstrike.falcon`
  - `crowdstrike.fdr`

## Usage

1. Configure the CrowdStrike integration in Elastic Agent
2. Ensure data is being ingested to Elasticsearch
3. Compile the dashboards:

   ```bash
   kb-dashboard compile --input-dir docs/content/examples/crowdstrike-modern/
   ```

4. Upload to Kibana:

   ```bash
   kb-dashboard compile --input-dir docs/content/examples/crowdstrike-modern/ --upload
   ```

## Related

See also: [CrowdStrike Dashboards](../crowdstrike/README.md) for dataset-centric dashboards organized by data source.
