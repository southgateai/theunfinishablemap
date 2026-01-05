#!/bin/bash
# Netlify build script for The Unfinishable Map

set -e

# Install uv if not present
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# Sync dependencies and run build
uv sync
uv run python scripts/build.py --output public "$@"
