#!/usr/bin/env bash
# Venice Chat Cross-Platform Installer (macOS & Linux)
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$HOME/.local/bin"

echo ""
echo "============================================="
echo "   Venice AI Chat Installer (macOS / Linux)  "
echo "============================================="
echo ""

# 1. Check Python
if ! command -v python3 &>/dev/null; then
    echo "[!] Error: python3 is not installed. Please install Python 3.8+."
    exit 1
fi

echo "[1/3] Checking Python environment: $(python3 --version)"

# 2. Install Python dependencies
echo "[2/3] Installing dependencies from requirements.txt..."
python3 -m pip install -q -r "$SCRIPT_DIR/requirements.txt" || {
    echo "Warning: pip install encountered issues; continuing..."
}

# 3. Setup bin directory
mkdir -p "$BIN_DIR"

# 4. Create global executable wrapper
echo "[3/3] Creating global 'venice' command at $BIN_DIR/venice..."
WRAPPER="$BIN_DIR/venice"
cat << EOF > "$WRAPPER"
#!/usr/bin/env bash
exec python3 "$SCRIPT_DIR/venice_chat.py" "\$@"
EOF
chmod +x "$WRAPPER"

# 5. Check for .env file
if [ ! -f "$SCRIPT_DIR/.env" ] && [ -f "$SCRIPT_DIR/.env.example" ]; then
    cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
fi

# 6. Verify PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo ""
    echo "Notice: $BIN_DIR is not in your current PATH."
    echo "Add it by adding this line to your ~/.zshrc or ~/.bashrc:"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
fi

echo ""
echo "=========================================================="
echo "  ✔ Venice Chat successfully installed!"
echo "  Run it anywhere by simply typing: venice"
echo "  To uninstall completely, run: venice uninstall"
echo "=========================================================="
echo ""
