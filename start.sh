#!/bin/bash

# StudyDuel - Quick Start Script for macOS/Linux
# This script starts both backend and frontend in separate terminal tabs/windows

set -e  # Exit on any error

echo "============================================"
echo "StudyDuel - Quick Start"
echo "============================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not installed"
    echo "Install with: brew install python3 (macOS) or apt install python3 (Linux)"
    exit 1
fi

# Check if Node is installed
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js not installed"
    echo "Install from: https://nodejs.org/"
    exit 1
fi

echo "Python $(python3 --version | cut -d' ' -f2): OK"
echo "Node $(node --version): OK"
echo ""

# Check if we're in the right directory
if [ ! -f "backend/requirements.txt" ]; then
    echo "ERROR: backend/requirements.txt not found"
    echo "Make sure you run this script from the project root directory"
    exit 1
fi

if [ ! -f "frontend/package.json" ]; then
    echo "ERROR: frontend/package.json not found"
    echo "Make sure you run this script from the project root directory"
    exit 1
fi

# Setup backend
echo "Setting up backend..."
cd backend

# Create virtual environment if needed
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Install dependencies
echo "Installing backend dependencies..."
source venv/bin/activate
pip install -q -r requirements.txt

# Setup frontend
cd ..
echo "Setting up frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

cd ..

echo ""
echo "============================================"
echo "Starting StudyDuel services..."
echo "============================================"
echo ""
echo "Frontend: http://localhost:5173"
echo "Backend:  http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""

# Detect if we're on macOS or Linux
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS - use osascript to open Terminal tabs
    echo "Opening services in new Terminal windows..."
    
    # Backend
    osascript -e "tell app \"Terminal\"
        do script \"cd '$(pwd)/backend' && source venv/bin/activate && uvicorn app.main:app --reload --port 8000\"
    end tell" 2>/dev/null || true
    
    sleep 2
    
    # Frontend
    osascript -e "tell app \"Terminal\"
        do script \"cd '$(pwd)/frontend' && npm run dev\"
    end tell" 2>/dev/null || true
    
    echo "New Terminal windows opened!"
    
else
    # Linux - use gnome-terminal or xterm fallback
    echo "Opening services in new terminal windows..."
    
    # Backend
    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal -- bash -c "cd '$(pwd)/backend' && source venv/bin/activate && uvicorn app.main:app --reload --port 8000; bash" &
    elif command -v xterm &> /dev/null; then
        xterm -e "cd '$(pwd)/backend' && source venv/bin/activate && uvicorn app.main:app --reload --port 8000" &
    else
        echo "No terminal emulator found. Starting in current shell..."
        cd backend
        source venv/bin/activate
        uvicorn app.main:app --reload --port 8000 &
        cd ..
    fi
    
    sleep 2
    
    # Frontend
    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal -- bash -c "cd '$(pwd)/frontend' && npm run dev; bash" &
    elif command -v xterm &> /dev/null; then
        xterm -e "cd '$(pwd)/frontend' && npm run dev" &
    fi
fi

echo ""
echo "Services are starting..."
echo ""
echo "Open your browser and navigate to:"
echo "  http://localhost:5173"
echo ""
echo "To stop everything:"
echo "  - Close the terminal windows, or"
echo "  - Press Ctrl+C in each window"
echo ""
echo "To stop just the backend/frontend:"
echo "  - Press Ctrl+C in the respective terminal"
echo ""
