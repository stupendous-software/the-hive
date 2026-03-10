#!/usr/bin/env bash
set -euo pipefail

# Build and push the Hive Docker image with both beta and latest tags
# Requires Docker Hub credentials in /a0/usr/.secrets

REPOSITORY="brianheston/the-hive"
BUILD_CONTEXT="/a0"
DOCKERFILE="docker/run/Dockerfile"

# Load credentials
if [ ! -f "/a0/usr/.secrets" ]; then
  echo "ERROR: /a0/usr/.secrets not found" >&2
  exit 1
fi
source /a0/usr/.secrets

echo "Logging into Docker Hub..."
echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USERNAME" --password-stdin

echo "Building image with tags: $REPOSITORY:beta and $REPOSITORY:latest"
docker build \
  -t "$REPOSITORY:beta" \
  -t "$REPOSITORY:latest" \
  -f "$DOCKERFILE" \
  "$BUILD_CONTEXT"

echo "Pushing beta tag..."
docker push "$REPOSITORY:beta"

echo "Pushing latest tag..."
docker push "$REPOSITORY:latest"

echo "Done. Both tags have been pushed."
