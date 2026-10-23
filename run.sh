#!/usr/bin/env bash
# Venice Chat Launcher Script

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

# Check Python3
if ! command -v python3 &>/dev/null; then
    echo "Error: Python 3 is required to run Venice Chat."
    exit 1
fi

# Run Venice Chat TUI
python3 venice_chat.py "$@"
