#!/bin/bash
set -euo pipefail
export OTEL_EXPORTER_OTLP_ENDPOINT=${OTEL_EXPORTER_OTLP_ENDPOINT:-http://localhost:4318/v1/traces}
export OTEL_SERVICE_NAME=${OTEL_SERVICE_NAME:-agent-zero}
echo "[entrypoint] Starting; A0_CLONE_NAME=${A0_CLONE_NAME:-}, BRANCH=${BRANCH:-}" >&2
# Set identity
if [ -n "${A0_CLONE_NAME:-}" ]; then
  echo "${A0_CLONE_NAME}" > /.identity
  # Set system hostname to match clone name ( ineffective in unprivileged container, but harmless )
  if command -v hostname >/dev/null 2>&1; then
    hostname "${A0_CLONE_NAME}" 2>/dev/null || true
  fi
  if [ -w /etc/hostname ]; then
    echo "${A0_CLONE_NAME}" > /etc/hostname
  fi
else
  echo "clone" > /.identity
  if command -v hostname >/dev/null 2>&1; then
    hostname "clone" 2>/dev/null || true
  fi
  if [ -w /etc/hostname ]; then
    echo "clone" > /etc/hostname
  fi
fi
# Ensure settings.json with A2A keys
if [ ! -f /a0/usr/settings.json ]; then
  echo "[entrypoint] Creating default settings.json" >&2
  cat > /a0/usr/settings.json <<'JSON'
{
  "rfc_password": "AgentZeroA2A@2025",
  "a2a_enabled": true,
  "fasta2a_enabled": true,
  "mcp_server_token": "AgentZeroA2A@2025"
}
JSON
else
  python3 - <<'PY'
import json
p = '/a0/usr/settings.json'
with open(p) as f: d = json.load(f)
changed=False
for k in ['rfc_password','a2a_enabled','fasta2a_enabled','mcp_server_token']:
  if k not in d:
    if k=='rfc_password': d[k]='AgentZeroA2A@2025'
    if k in ['a2a_enabled','fasta2a_enabled']: d[k]=True
    if k=='mcp_server_token': d[k]='AgentZeroA2A@2025'
    changed=True
if changed:
  with open(p,'w') as f: json.dump(d,f,indent=2)
  print('[entrypoint] Updated settings.json')
else:
  print('[entrypoint] settings.json OK')
PY
fi
# Create bootstrapped marker early

# Auto-enable all discovered skills (ensures new skills are available)
if [ -x /a0/usr/workdir/scripts/auto_enable_skills.py ]; then
  python3 /a0/usr/workdir/scripts/auto_enable_skills.py
fi
touch /a0/.bootstrapped 2>/dev/null || true
echo "[entrypoint] Bootstrapped marker created (early)" >&2
# Start initialize
/exe/initialize.sh "${BRANCH:-local}" &
INIT_PID=$!
# Wait for webui
TIMEOUT=180
while [ $TIMEOUT -gt 0 ]; do
  if [ -f /a0/webui/index.html ]; then
    echo "[entrypoint] initialize ready" >&2
    break
  fi
  sleep 1
  TIMEOUT=$((TIMEOUT-1))
done
# Run parent_clone_manager background
if [ -f /a0/usr/scripts/parent_clone_manager.py ]; then
  echo "[entrypoint] Running parent_clone_manager (background)" >&2
  /opt/venv-a0/bin/python /a0/usr/scripts/parent_clone_manager.py &
  PM_PID=$!
else
  PM_PID=""
fi
# Substitute clone name: replace 'Agent Zero' with clone name
if [ -f /a0/webui/index.html ] && grep -q 'Agent Zero' /a0/webui/index.html; then
  echo "[entrypoint] Performing clone name substitution" >&2
  find /a0 -type f -exec grep -Iq . {} \; -exec sed -i "s/Agent Zero/${A0_CLONE_NAME:-clone}/g" {} \; 2>/dev/null || true
fi
# Ensure A2A agent.json has correct agent name
for f in /a0/agent/.well-known/agent.json /.well-known/agent.json; do
  if [ -f "$f" ]; then
    if grep -q '"name"\s*:\s*"Agent Zero"' "$f"; then
      echo "[entrypoint] Updating A2A agent name in $f" >&2
      sed -i "s/\"name\"\s*:\s*\"Agent Zero\"/\"name\"\s*:\s*\"${A0_CLONE_NAME:-clone}\"/g" "$f"
    fi
  fi
done
# Ensure bootstrapped
touch /a0/.bootstrapped 2>/dev/null || true
if [ -f /a0/.bootstrapped ]; then
  echo "[entrypoint] Bootstrapped marker verified" >&2
else
  echo "[entrypoint] ERROR: Could not create /a0/.bootstrapped" >&2
fi
# Wait for initialize
wait $INIT_PID
if [ -n "$PM_PID" ]; then
  wait $PM_PID 2>/dev/null || true
fi
