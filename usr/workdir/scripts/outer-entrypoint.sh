#!/bin/bash
set -euo pipefail
if [ -n "${A0_CLONE_NAME:-}" ]; then
  echo "[outer-entrypoint] Applying clone name: ${A0_CLONE_NAME}" >&2
  if [ -d "/a0" ]; then
    find /a0 -type f -exec grep -Iq . {} \; -exec sed -i "s/Agent Zero/${A0_CLONE_NAME}/g" {} \; 2>/dev/null || true
  fi
fi
exec /a0/usr/scripts/docker-entrypoint.sh
