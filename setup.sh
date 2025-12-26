#!/bin/bash
###################################################################
# Baidoxe Setup Script - macOS/Linux
# Cài đặt tất cả dependencies cho backend, frontend, desktop
###################################################################

set -e  # Exit on error

echo ""
echo "==================================================================="
echo "   BAIDOXE PARKING MANAGEMENT SYSTEM - SETUP"
echo "==================================================================="
echo ""

# Check Node.js
echo "[1/5] Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js not found! Please install Node.js 16+"
    echo "Download from: https://nodejs.org/"
    exit 1
fi
echo "   ✓ $(node --version) installed"
echo ""

# Check Python
echo "[2/5] Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python not found! Please install Python 3.8+"
    echo "Download from: https://www.python.org/"
    exit 1
fi
echo "   ✓ $(python3 --version) installed"
echo ""

# Setup Backend
echo "[3/5] Setting up Backend..."
cd backend
if [ ! -d "venv" ]; then
    echo "   Creating virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate
echo "   Installing dependencies..."
pip install -q -r requirements.txt
echo "   ✓ Backend setup complete"
cd ..
echo ""

# Setup Frontend
echo "[4/5] Setting up Frontend..."
cd frontend
echo "   Installing dependencies (this may take a few minutes)..."
npm install
echo "   ✓ Frontend setup complete"
cd ..
echo ""

# Setup Desktop (Optional)
echo "[5/5] Setting up Desktop App (optional)..."
cd desktop
echo "   Installing dependencies (this may take a few minutes)..."
if npm install; then
    echo "   ✓ Desktop setup complete"
else
    echo "WARNING: Desktop app setup failed (optional)"
    echo "You can skip this if you only need web + backend"
fi
cd ..
echo ""

echo "==================================================================="
echo "   ✓ SETUP COMPLETE!"
echo "==================================================================="
echo ""
echo "Next steps:"
echo "   1. Run './run-dev.sh' to start development environment"
echo "   2. Or read INSTALL.md for detailed instructions"
echo ""
