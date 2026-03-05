#!/bin/bash
set -e

# Set clone identity if provided
if [ -n "$A0_CLONE_NAME" ]; then
    echo "$A0_CLONE_NAME" > /.identity
    hostname "$A0_CLONE_NAME" 2>/dev/null || true
fi

# Forward BRANCH to initialize.sh
if [ "$1" = "/exe/initialize.sh" ] && [ -n "$BRANCH" ]; then
  set -- /exe/initialize.sh "$BRANCH"
fi

exec "$@"
