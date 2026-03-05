#!/bin/bash
set -euo pipefail

# Set identity if A0_CLONE_NAME provided
CLONE_NAME="${A0_CLONE_NAME:-$(hostname)}"
if [ "$(id -u)" -eq 0 ]; then
  echo "$CLONE_NAME" > /etc/hostname
  hostname "$CLONE_NAME" 2>/dev/null || true
  echo "$CLONE_NAME" > /.identity
  chmod 644 /.identity
else
  echo "outer-entrypoint: Must run as root to set identity" >&2
fi

# Execute docker-entrypoint.sh, passing BRANCH if set
if [ -n "$BRANCH" ]; then
  exec /a0/usr/scripts/docker-entrypoint.sh "$BRANCH"
else
  exec /a0/usr/scripts/docker-entrypoint.sh
fi
