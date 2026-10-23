#!/usr/bin/env bash
# Venice Chat Standalone Uninstaller
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/venice_chat.py" uninstall "$@"
