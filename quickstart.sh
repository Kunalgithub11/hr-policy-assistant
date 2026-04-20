#!/bin/bash

# HR Policy Assistant - macOS/Linux Quick Start Script

echo ""
echo "======================================"
echo "HR Policy Assistant - Quick Start"
echo "======================================"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.9+ from python.org"
    exit 1
fi

echo "[1/5] Creating virtual environment..."
if [ ! -d venv ]; then
    python3 -m venv venv
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi

echo "[2/5] Activating virtual environment..."
source venv/bin/activate

echo "[3/5] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "[4/5] Setting up environment..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo ".env file created. Please add your GROQ_API_KEY!"
    read -p "Press Enter to continue..."
fi

echo ""
echo "[5/5] Starting Streamlit UI..."
echo ""
echo "======================================"
echo "Open your browser to: http://localhost:8501"
echo "Press Ctrl+C to stop the server"
echo "======================================"
echo ""

streamlit run capstone_streamlit.py
