@echo off
REM StudyDuel - Quick Start Script for Windows
REM This script starts both backend and frontend in separate windows

echo ============================================
echo StudyDuel - Quick Start
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not installed or not in PATH
    echo Download from: https://www.python.org/
    pause
    exit /b 1
)

REM Check if Node is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not installed or not in PATH
    echo Download from: https://nodejs.org/
    pause
    exit /b 1
)

echo Python: OK
echo Node.js: OK
echo.

REM Check if we're in the right directory
if not exist "backend\requirements.txt" (
    echo ERROR: backend/requirements.txt not found
    echo Make sure you run this script from the project root directory
    pause
    exit /b 1
)

if not exist "frontend\package.json" (
    echo ERROR: frontend/package.json not found
    echo Make sure you run this script from the project root directory
    pause
    exit /b 1
)

echo Setting up backend...
cd backend

if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing backend dependencies...
pip install -q -r requirements.txt

echo.
echo Starting backend server (http://localhost:8000)...
echo API Docs: http://localhost:8000/docs
echo.
echo IMPORTANT: Keep this window open!
echo Press Ctrl+C to stop the server
echo.

start cmd /k "cd backend && call venv\Scripts\activate.bat && uvicorn app.main:app --reload --port 8000"

timeout /t 3 /nobreak

cd ..

echo.
echo Setting up frontend...
cd frontend

if not exist "node_modules" (
    echo Installing frontend dependencies...
    call npm install
)

echo.
echo Starting frontend dev server (http://localhost:5173)...
echo.
echo IMPORTANT: Keep this window open!
echo Press Ctrl+C to stop the server
echo.

start cmd /k "cd frontend && npm run dev"

timeout /t 2 /nobreak

cd ..

echo.
echo ============================================
echo StudyDuel is starting!
echo ============================================
echo.
echo Frontend: http://localhost:5173
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Two new windows should have opened:
echo 1. Backend server (Uvicorn)
echo 2. Frontend dev server (Vite)
echo.
echo Open http://localhost:5173 in your browser to get started!
echo.
echo To stop everything: Close both command windows
echo.
pause
