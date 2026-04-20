@echo off
REM HR Policy Assistant - Windows Quick Start Script

echo.
echo ======================================
echo HR Policy Assistant - Quick Start
echo ======================================
echo.

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from python.org
    pause
    exit /b 1
)

echo [1/5] Creating virtual environment...
if not exist venv (
    python -m venv venv
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)

echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/5] Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo [4/5] Setting up environment...
if not exist .env (
    copy .env.example .env
    echo .env file created. Please add your GROQ_API_KEY!
    pause
)

echo.
echo [5/5] Starting Streamlit UI...
echo.
echo ======================================
echo Open your browser to: http://localhost:8501
echo Press Ctrl+C to stop the server
echo ======================================
echo.

streamlit run capstone_streamlit.py

pause
