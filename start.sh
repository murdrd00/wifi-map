#!/bin/bash
cd "$(dirname "$0")"

echo "Starting WiFi Heatmap Builder..."

# Find Python
if command -v python3 &>/dev/null; then
    PY=python3
elif command -v python &>/dev/null; then
    PY=python
else
    echo "Python not found! Please install Python from https://python.org"
    exit 1
fi

echo "Found $PY"
echo "Opening browser..."

# Open browser (works on macOS and Linux)
if [[ "$OSTYPE" == "darwin"* ]]; then
    open http://localhost:8199 &
else
    xdg-open http://localhost:8199 2>/dev/null &
fi

$PY server.py
