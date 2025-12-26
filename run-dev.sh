#!/bin/bash
###################################################################
# Baidoxe Development Runner - macOS/Linux
# Starts Backend (Flask) + Frontend (React)
###################################################################

set -e  # Exit on error

echo ""
echo "==================================================================="
echo "   BAIDOXE PARKING MANAGEMENT SYSTEM - DEVELOPMENT"
echo "==================================================================="
echo ""

# Setup Python dependencies if needed
echo "[1/3] Setting up Python backend dependencies..."
cd backend
if [ ! -d "venv" ]; then
    echo "   Creating virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate
echo "   Installing Python packages..."
pip install -q -r requirements.txt
cd ..
echo "   ✓ Backend dependencies installed"
echo ""

# Initialize database if needed
if [ ! -f "backend/data/parking_system.db" ]; then
    echo "[2/3] Initializing database..."
    cd backend
    source venv/bin/activate
    python scripts/init_db.py
    cd ..
    echo "   ✓ Database initialized"
    echo ""
fi

echo "[3/3] Starting Backend (Flask) on http://localhost:5000..."
cd backend
source venv/bin/activate
python run.py &
BACKEND_PID=$!
cd ..
sleep 2
echo ""

echo "Starting Frontend (React) on http://localhost:3000..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..
sleep 3

echo ""
echo "==================================================================="
echo "   ✓ DEVELOPMENT ENVIRONMENT STARTED"
echo "==================================================================="
echo ""
echo "   Backend:  http://localhost:5000"
echo "   Frontend: http://localhost:3000"
echo "   API Docs: http://localhost:5000/api/docs"
echo ""
echo "To stop: Press Ctrl+C"
echo ""

# Wait for Ctrl+C
wait
