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
# --- Build seed NDJSON with realistic volume ---
# 3 hosts, 3 services, spread across the 15-minute window so date histograms
# and breakdowns have enough data to look realistic.
# Produces ~30 log docs + ~15 metric docs = ~45 documents.
HOSTS=(host-a host-b host-c)
HOST_IPS=(10.0.0.1 10.0.0.2 10.0.0.3)
SERVICES=(api worker frontend)
ENVS=(production staging production)
LEVELS=(info warn error info info info)  # weighted toward info
METHODS=(GET POST PUT DELETE GET GET)
PATHS=(/api/v1/users /api/v1/orders /api/v1/health /api/v1/sessions /api/v1/products /)
CODES=(200 200 200 201 301 400 401 404 500 503)
AGENTS=(curl python-requests "Mozilla/5.0" ELB-HealthChecker Go-http-client)

: > /tmp/explore-seed.ndjson

# Generate 30 log documents (one per 30s over the last 15 min)
for i in $(seq 0 29); do
  ts="$(epoch_to_iso $((NOW_EPOCH - 870 + i * 30)))"
  h=$((i % 3)); s=$((i % 3))
  lvl="${LEVELS[$((i % ${#LEVELS[@]}))]}"
  method="${METHODS[$((i % ${#METHODS[@]}))]}"
  path="${PATHS[$((i % ${#PATHS[@]}))]}"
  code="${CODES[$((i % ${#CODES[@]}))]}"
  bytes=$(( (i + 1) * 128 ))
  agent="${AGENTS[$((i % ${#AGENTS[@]}))]}"
  env="${ENVS[$s]}"
  echo '{"create":{"_index":"logs-default-generic"}}' >> /tmp/explore-seed.ndjson
  echo "{\"@timestamp\":\"${ts}\",\"message\":\"${method} ${path} ${code}\",\"log\":{\"level\":\"${lvl}\"},\"service\":{\"name\":\"${SERVICES[$s]}\",\"version\":\"1.2.0\",\"environment\":\"${env}\"},\"host\":{\"name\":\"${HOSTS[$h]}\",\"ip\":\"${HOST_IPS[$h]}\"},\"event\":{\"dataset\":\"app.logs\",\"module\":\"${SERVICES[$s]}\"},\"http\":{\"request\":{\"method\":\"${method}\"},\"response\":{\"status_code\":${code},\"bytes\":${bytes}}},\"url\":{\"path\":\"${path}\"},\"user_agent\":{\"name\":\"${agent}\"}}" >> /tmp/explore-seed.ndjson
done

# Generate 15 metric documents (one per minute per host over 5 min)
for minute in $(seq 0 4); do
  ts="$(epoch_to_iso $((NOW_EPOCH - 600 + minute * 60)))"
  for h in 0 1 2; do
    cpu_user="0.$((20 + h * 25 + minute * 3))"
    cpu_sys="0.$((5 + h * 3 + minute))"
    mem_pct="0.$((55 + h * 15 + minute * 2))"
    mem_bytes=$(( 2400000000 + h * 500000000 + minute * 100000000 ))
    load1="$((h + minute)).$(( (h + minute) % 10 ))"
    echo '{"create":{"_index":"metrics-default-generic"}}' >> /tmp/explore-seed.ndjson
    echo "{\"@timestamp\":\"${ts}\",\"service\":{\"name\":\"${SERVICES[$h]}\"},\"host\":{\"name\":\"${HOSTS[$h]}\",\"ip\":\"${HOST_IPS[$h]}\"},\"event\":{\"dataset\":\"system.cpu\",\"module\":\"system\"},\"system\":{\"cpu\":{\"user\":{\"pct\":${cpu_user}},\"system\":{\"pct\":${cpu_sys}},\"total\":{\"pct\":${cpu_user}}},\"memory\":{\"used\":{\"pct\":${mem_pct},\"bytes\":${mem_bytes}},\"total\":{\"bytes\":4294967296}},\"load\":{\"1\":${load1},\"5\":0.8,\"15\":0.6}},\"metricset\":{\"name\":\"cpu\"}}" >> /tmp/explore-seed.ndjson
  done
done

echo "Seeded $(grep -c 'logs-default-generic' /tmp/explore-seed.ndjson) log docs + $(grep -c 'metrics-default-generic' /tmp/explore-seed.ndjson) metric docs"

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
