#!/bin/bash
set -e

# Exit immediately if a command exits with a non-zero status.
# set -e

# branch from parameter
if [ -z "$1" ]; then
    echo "Error: Branch parameter is empty. Please provide a valid branch name."
    exit 1
fi
BRANCH="$1"

# If the repository already exists at /git/agent-zero, skip cloning.
if [ -d "/git/agent-zero" ]; then
  echo "Repository /git/agent-zero already exists. Skipping clone."
else
  # Clone from GitHub for the requested branch
  echo "Cloning repository from branch $BRANCH..."
  git clone -b "$BRANCH" "https://github.com/agent0ai/agent-zero" "/git/agent-zero" || {
      echo "CRITICAL ERROR: Failed to clone repository. Branch: $BRANCH"
      exit 1
  }
fi

. "/ins/setup_venv.sh" "$@"

# Install remaining A0 python packages
uv pip install -r /git/agent-zero/requirements.txt
# override for packages that have unnecessarily strict dependencies
uv pip install -r /git/agent-zero/requirements2.txt

# install playwright
bash /ins/install_playwright.sh "$@"

# Preload A0
python /git/agent-zero/preload.py --dockerized=true
