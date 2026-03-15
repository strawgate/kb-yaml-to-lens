#!/usr/bin/env bash
# Bootstrap local Elasticsearch + Kibana and seed deterministic sample data.
#
# Usage:
#   bash scripts/bootstrap-explore-kibana.sh [kibana_version]
#
# Examples:
#   bash scripts/bootstrap-explore-kibana.sh
#   bash scripts/bootstrap-explore-kibana.sh 9.3.0

set -euo pipefail

KIBANA_VERSION="${1:-9.3.0}"
NETWORK_NAME="explore-net"
ES_CONTAINER="es-explore"
KIBANA_CONTAINER="kibana-explore"

echo "Bootstrapping Elasticsearch + Kibana (version: ${KIBANA_VERSION})"

docker rm -f "${ES_CONTAINER}" "${KIBANA_CONTAINER}" >/dev/null 2>&1 || true
docker network rm "${NETWORK_NAME}" >/dev/null 2>&1 || true
docker network create "${NETWORK_NAME}" >/dev/null

docker run -d --name "${ES_CONTAINER}" \
  --network "${NETWORK_NAME}" \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  -e "ES_JAVA_OPTS=-Xms1g -Xmx1g" \
  -e "network.host=0.0.0.0" \
  "docker.elastic.co/elasticsearch/elasticsearch:${KIBANA_VERSION}" >/dev/null

# Map Kibana to host port 443 so the AWF sandbox agent can reach it.
# The AWF firewall only DNAT-redirects ports 80 and 443 through its Squid proxy;
# all other ports are dropped by the filter chain's default deny rule.
# Port 80 is already used by the MCP gateway, so we use 443.
docker run -d --name "${KIBANA_CONTAINER}" \
  --network "${NETWORK_NAME}" \
  -p 443:5601 \
  -e "ELASTICSEARCH_HOSTS=http://${ES_CONTAINER}:9200" \
  -e "XPACK_SECURITY_ENABLED=false" \
  -e "SERVER_HOST=0.0.0.0" \
  "docker.elastic.co/kibana/kibana:${KIBANA_VERSION}" >/dev/null

echo "Waiting for Elasticsearch on http://localhost:9200 ..."
for i in $(seq 1 90); do
  if curl -fsS "http://localhost:9200" >/dev/null; then
    break
  fi
  sleep 2
done

echo "Waiting for Kibana on http://localhost:443 ..."
KIBANA_READY=0
for _ in $(seq 1 180); do
  if curl -fsS "http://localhost:443/api/status" >/dev/null; then
    KIBANA_READY=1
    break
  fi
  sleep 2
done

if [ "${KIBANA_READY}" -ne 1 ]; then
  echo "Kibana did not become ready within timeout." >&2
  exit 1
fi

# Generate timestamps relative to "now" so data always falls within Kibana's
# default "Last 15 minutes" range — no time picker changes needed.
# Placed after the Kibana wait so timestamps don't age during boot.
NOW_EPOCH="$(date +%s)"
# Portable epoch-to-ISO: macOS uses `date -r`, GNU/Linux uses `date -d @`
epoch_to_iso() {
  date -u -r "$1" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null \
    || date -u -d "@$1" +%Y-%m-%dT%H:%M:%SZ
}
TS0="$(epoch_to_iso $((NOW_EPOCH - 600)))"   # 10 min ago
TS1="$(epoch_to_iso $((NOW_EPOCH - 540)))"   # 9 min ago
TS2="$(epoch_to_iso $((NOW_EPOCH - 480)))"   # 8 min ago
TS3="$(epoch_to_iso $((NOW_EPOCH - 420)))"   # 7 min ago
TS4="$(epoch_to_iso $((NOW_EPOCH - 360)))"   # 6 min ago
TS5="$(epoch_to_iso $((NOW_EPOCH - 300)))"   # 5 min ago

cat > /tmp/explore-seed.ndjson <<EOF
{"create":{"_index":"logs-default-generic"}}
{"@timestamp":"${TS0}","service":{"name":"api"},"host":{"name":"host-a"},"event":{"dataset":"app.logs"},"log":{"level":"info"},"env":"prod","status":"ok","value":12.5}
{"create":{"_index":"logs-default-generic"}}
{"@timestamp":"${TS1}","service":{"name":"api"},"host":{"name":"host-b"},"event":{"dataset":"app.logs"},"log":{"level":"error"},"env":"prod","status":"error","value":41.1}
{"create":{"_index":"logs-default-generic"}}
{"@timestamp":"${TS2}","service":{"name":"worker"},"host":{"name":"host-c"},"event":{"dataset":"app.logs"},"log":{"level":"warn"},"env":"staging","status":"warn","value":22.0}
{"create":{"_index":"metrics-default-generic"}}
{"@timestamp":"${TS3}","service.name":"api","host.name":"host-a","env":"prod","cpu.pct":0.43,"latency_ms":121,"requests":240}
{"create":{"_index":"metrics-default-generic"}}
{"@timestamp":"${TS4}","service.name":"api","host.name":"host-b","env":"prod","cpu.pct":0.88,"latency_ms":292,"requests":310}
{"create":{"_index":"metrics-default-generic"}}
{"@timestamp":"${TS5}","service.name":"worker","host.name":"host-c","env":"staging","cpu.pct":0.36,"latency_ms":95,"requests":125}
EOF

echo "Seeding indices logs-default-generic + metrics-default-generic ..."
bulk_response="$(curl -fsS -H "Content-Type: application/x-ndjson" \
  -XPOST "http://localhost:9200/_bulk?refresh=true" \
  --data-binary @/tmp/explore-seed.ndjson)"

if printf '%s' "${bulk_response}" | grep -qE '"errors":[[:space:]]*true'; then
  echo "Elasticsearch bulk seeding returned item-level errors." >&2
  printf '%s\n' "${bulk_response}" >&2
  exit 1
fi

# Create data views so Lens is immediately usable (Kibana never auto-creates these)
echo "Creating data views ..."
for DV in "logs-*" "metrics-*"; do
  curl -fsS -X POST "http://localhost:443/api/data_views/data_view" \
    -H "kbn-xsrf: true" \
    -H "Content-Type: application/json" \
    -d "{\"data_view\":{\"title\":\"${DV}\",\"name\":\"${DV}\",\"timeFieldName\":\"@timestamp\"}}" \
    >/dev/null
  echo "  Created data view: ${DV}"
done

echo "Bootstrap complete."
echo "- Elasticsearch: http://localhost:9200"
echo "- Kibana:        http://localhost:443"
echo "- Data views:    logs-*, metrics-*"
