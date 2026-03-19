#!/usr/bin/env bash
set -euo pipefail

APP_NAME="NEO Code"
GENERIC_NAME="Educational Python IDE"
COMMENT="Python IDE for STEM and Robotics students"
DESKTOP_FILE="$HOME/.local/share/applications/neo-code.desktop"

mkdir -p "$(dirname "$DESKTOP_FILE")"

if command -v neo-code >/dev/null 2>&1; then
    EXEC_PATH="$(command -v neo-code)"
elif command -v python3 >/dev/null 2>&1; then
    EXEC_PATH="python3 -m neo_code"
else
    echo "Error: 'neo-code' not found and python3 is unavailable." >&2
    exit 1
fi

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=$APP_NAME
GenericName=$GENERIC_NAME
Comment=$COMMENT
Exec=$EXEC_PATH
Terminal=false
Categories=Education;Development;IDE;
Keywords=python;ide;code;kids;stem;
StartupNotify=true
EOF

echo "Created desktop entry: $DESKTOP_FILE"
