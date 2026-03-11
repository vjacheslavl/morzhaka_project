#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

if [ ! -f "venv/.deps_installed" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    touch venv/.deps_installed
fi

echo "Starting Dungeon Crawler..."
python game.py
