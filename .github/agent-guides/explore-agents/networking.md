# Explore Agent Networking

You run inside a Docker container. Understanding the network topology is
critical — getting this wrong means your CLI commands silently time out.

## URL rules

| Context | Kibana URL | Elasticsearch URL | Why |
|---------|-----------|-------------------|-----|
| Playwright (`browser_navigate`, `browser_run_code`) | `http://localhost:443` | `http://localhost:9200` | The browser runs on the **host**, where Kibana is mapped to port 443. |
| Shell commands (`uv run`, `curl`, `python`) | `http://host.docker.internal:443` | N/A (use Kibana API) | Shell commands run inside the **container**. The AWF firewall only allows ports 80 (MCP gateway) and 443 (Kibana) through its Squid proxy. `host.docker.internal` routes to the host. |

## What is NOT available

- **The Docker daemon is NOT available.** Do not run `docker ps`,
  `docker exec`, `docker logs`, `docker compose`, or any Docker
  commands — they will all fail with "Cannot connect to the Docker daemon".
  You cannot inspect, restart, or manage the Kibana/Elasticsearch containers.

- **`localhost` does not reach Kibana from shell commands.** If you run
  `curl http://localhost:443` it will fail with "Connection refused".
  Always use `http://host.docker.internal:443` for shell commands.

- **Elasticsearch is NOT directly reachable from shell commands.** Only
  Kibana (port 443) is exposed through the firewall. Use the Kibana API
  or Playwright for any Elasticsearch interaction.

## Pre-provisioned services

Elasticsearch and Kibana are pre-provisioned for this workflow run.
Do NOT run bootstrap scripts (`just explore-bootstrap`,
`scripts/bootstrap-explore-kibana.sh`, Docker compose, or equivalent).

## CLI examples

Compile and upload a dashboard:
```bash
uv run kb-dashboard compile --input-file <file> --output-dir /tmp/compiled/ \
  --upload --kibana-url http://host.docker.internal:443
```

Export a dashboard:
```bash
uv run kb-dashboard fetch <dashboard-id> --output /tmp/exported.ndjson \
  --kibana-url http://host.docker.internal:443
```
