#!/bin/bash
set -euo pipefail

echo "[docker-entrypoint] Starting; A0_CLONE_NAME=${A0_CLONE_NAME:-unset}, BRANCH=${BRANCH:-unset}" >&2

# Write identity
if [ -n "${A0_CLONE_NAME:-}" ]; then
  echo "${A0_CLONE_NAME}" > /.identity
  echo "[docker-entrypoint] Wrote identity: ${A0_CLONE_NAME}" >&2
else
  echo "clone" > /.identity
  echo "[docker-entrypoint] Wrote default identity 'clone'" >&2
fi

# Bootstrapped marker
touch /a0/.bootstrapped 2>/dev/null || true
echo "[docker-entrypoint] Touched /a0/.bootstrapped" >&2

# Start the main initialization in background (it will copy source to /a0 and start services)
echo "[docker-entrypoint] Launching /exe/initialize.sh with BRANCH=${BRANCH:-local}" >&2
/exe/initialize.sh "${BRANCH:-local}" &
INIT_PID=$!

# Cleanup handler to forward signals and exit
cleanup() {
  echo "[docker-entrypoint] Caught signal, terminating child PID $INIT_PID" >&2
  kill $INIT_PID 2>/dev/null || true
  wait $INIT_PID 2>/dev/null || true
  exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# Wait for webui index.html to appear and contain "Agent Zero", then substitute
# Timeout after 60 seconds but continue
TIMEOUT=60
while [ $TIMEOUT -gt 0 ]; do
  if [ -f /a0/webui/index.html ] && grep -q "Agent Zero" /a0/webui/index.html; then
    echo "[docker-entrypoint] Performing post-copy clone name substitution (A0_CLONE_NAME=${A0_CLONE_NAME})..." >&2
    # Broad replacement in all text files under /a0
    find /a0 -type f -exec grep -Iq . {} \; -exec sed -i "s/Agent Zero/${A0_CLONE_NAME}/g" {} \; 2>/dev/null || true
    # Explicitly target webui files to be sure
    for f in /a0/webui/index.html /a0/webui/index.js /a0/webui/index.css; do
      [ -f "$f" ] && sed -i "s/Agent Zero/${A0_CLONE_NAME}/g" "$f" 2>/dev/null || true
    done
    echo "[docker-entrypoint] Substitution complete." >&2
    break
  fi
  sleep 1
  TIMEOUT=$((TIMEOUT-1))
done

# Wait for the child process (the main application) to exit
wait $INIT_PID
