# Third-Party Licenses

This directory contains license files for third-party content included in this repository.

## Elastic License 2.0

**File:** [ELASTIC-LICENSE-2.0.txt](./ELASTIC-LICENSE-2.0.txt)

**Applies to:** Example dashboards derived from the [Elastic integrations repository](https://github.com/elastic/integrations).

The following example files are derivative works based on Elastic's official integration dashboards and are licensed under the Elastic License 2.0:

### System OpenTelemetry Examples (`docs/examples/system_otel/`)

- `01-hosts-overview.yaml` - Derived from [system_otel](https://github.com/elastic/integrations/tree/main/packages/system_otel)
- `02-host-details-overview.yaml` - Derived from [system_otel](https://github.com/elastic/integrations/tree/main/packages/system_otel)
- `03-host-details-metrics.yaml` - Derived from [system_otel](https://github.com/elastic/integrations/tree/main/packages/system_otel)
- `04-host-details-metadata.yaml` - Derived from [system_otel](https://github.com/elastic/integrations/tree/main/packages/system_otel)
- `05-host-details-logs.yaml` - Derived from [system_otel](https://github.com/elastic/integrations/tree/main/packages/system_otel)

### Docker OpenTelemetry Examples (`docs/examples/docker_otel/`)

- `01-containers-overview.yaml` - Derived from [docker_otel](https://github.com/elastic/integrations/tree/main/packages/docker_otel)
- `02-container-stats.yaml` - Derived from [docker_otel](https://github.com/elastic/integrations/tree/main/packages/docker_otel)

These files have been converted from Kibana JSON format to YAML format for use as documentation examples. Each file contains a license header indicating its derivative nature.

## Other Examples

All other example files in this repository (e.g., `docs/examples/aerospike/`, `docs/examples/controls-example.yaml`, etc.) are original works licensed under the project's MIT license.

## Documentation Copy

For documentation build purposes, a copy of `ELASTIC-LICENSE-2.0.txt` is maintained at `docs/licenses/ELASTIC-LICENSE-2.0.txt`. This allows the license to be referenced in the MkDocs documentation site.

If you update the license file, ensure both copies are updated.
