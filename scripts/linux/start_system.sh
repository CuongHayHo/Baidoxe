#!/bin/bash

echo "================================================================"
echo "   🚗 PARKING SYSTEM - QUICK START"
echo "================================================================"
echo

# Check if we're in the right directory
if [ ! -f "api_server.py" ]; then
    echo "❌ Error: api_server.py not found!"
    echo "Please run this script from the Baidoxe folder."
    read -p "Press Enter to exit..."
    exit 1
fi

echo "📋 Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    PIP_CMD="pip"
else
    echo "❌ Python not found!"
    echo "Please install Python:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  macOS: brew install python3"
    read -p "Press Enter to exit..."
    exit 1
fi

echo "✅ Python found!"
$PYTHON_CMD --version

echo
echo "📦 Installing required packages..."
$PIP_CMD install flask flask-cors requests > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Packages installed successfully!"
else
    echo "⚠️  Package installation may have issues, but continuing..."
fi

echo
echo "🚀 Starting Parking System Server..."
echo
echo "🌐 Web interface will be available at:"
echo "   👉 http://localhost:5000"
echo
echo "🔧 Hardware endpoints:"
echo "   👉 Arduino UNO R4: Create WiFi AP \"Arduino_AP\""
echo "   👉 ESP32: Connect to WiFi and use IP 192.168.4.5"
echo
echo "📱 To access from other devices on LAN:"
echo "   👉 http://[YOUR_IP]:5000"
echo
echo "⏹️  Press Ctrl+C to stop the server"
echo "================================================================"
echo

# Start the server
$PYTHON_CMD api_server.py

echo
echo "🛑 Server stopped."
read -p "Press Enter to exit..."