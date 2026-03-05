#!/bin/bash
set -euo pipefail

# Dynamically substitute the clone name into UI static files at container start
if [ -n "${A0_CLONE_NAME:-}" ]; then
  echo "[outer-entrypoint] Applying clone name: ${A0_CLONE_NAME}"
  if [ -d "/a0/UI" ] || [ -d "/a0/hive-product-page" ]; then
    find /a0/UI /a0/hive-product-page -type f \( -name '*.html' -o -name '*.js' -o -name '*.css' \) -exec sed -i "s/Agent Zero/${A0_CLONE_NAME}/g" {} \; 2>/dev/null || true
  fi
fi

# Forward to docker-entrypoint (which will handle BRANCH)
exec /a0/usr/scripts/docker-entrypoint.sh "$@"
