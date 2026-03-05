#!/bin/bash
set -e

# Set clone identity if provided
if [ -n "$A0_CLONE_NAME" ]; then
    echo "$A0_CLONE_NAME" > /.identity
    hostname "$A0_CLONE_NAME" 2>/dev/null || true
fi

# Forward to initialize.sh with BRANCH if available
if [ -n "$BRANCH" ]; then
    exec /exe/initialize.sh "$BRANCH"
else
    exec /exe/initialize.sh
fi
