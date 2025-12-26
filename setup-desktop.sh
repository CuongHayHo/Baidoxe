#!/bin/bash
###################################################################
# Baidoxe Desktop App Setup - macOS/Linux
###################################################################

set -e

echo ""
echo "==================================================================="
echo "   BAIDOXE DESKTOP APP SETUP"
echo "==================================================================="
echo ""

# Check Node.js
echo "[1/2] Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js not found! Please install Node.js 16+"
    echo "Download from: https://nodejs.org/"
    exit 1
fi
echo "   ✓ $(node --version) installed"
echo ""

# Setup Desktop
echo "[2/2] Installing Desktop App dependencies..."
cd desktop
echo "   This may take 5-10 minutes..."
npm install
cd ..
echo "   ✓ Desktop setup complete"
echo ""

echo "==================================================================="
echo "   ✓ DESKTOP APP READY!"
echo "==================================================================="
echo ""
echo "Next step:"
echo "   Run './run-dev.sh' to start the application"
echo ""
