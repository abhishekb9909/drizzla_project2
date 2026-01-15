@echo off
REM Windows Setup Script for Document RAG Pipeline
REM Run with: setup.bat

setlocal enabledelayedexpansion

echo.
echo ================================================
echo   Document RAG Pipeline - Windows Setup
echo ================================================
echo.

REM Check Python
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.9+
    pause
    exit /b 1
)
echo [OK] Python found
echo.

REM Create venv
echo [2/5] Creating virtual environment...
if exist venv (
    echo [WARNING] venv already exists. Skipping...
) else (
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create venv
        pause
        exit /b 1
    )
    echo [OK] venv created
)
echo.

REM Activate venv
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate venv
    pause
    exit /b 1
)
echo [OK] venv activated
echo.

REM Upgrade pip
echo [4/5] Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Failed to upgrade pip (non-critical)
) else (
    echo [OK] pip upgraded
)
echo.

REM Install requirements
echo [5/5] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

REM Copy .env if doesn't exist
if not exist .env (
    echo Creating .env from template...
    copy .env.example .env
    echo [OK] .env created - Please edit with your credentials
) else (
    echo [OK] .env already exists
)
echo.

REM Initialize submodule
echo Initializing Git submodule...
git submodule update --init --recursive >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Failed to initialize submodule (check git installation)
) else (
    echo [OK] Submodule initialized
)
echo.

echo ================================================
echo   Setup Complete!
echo ================================================
echo.
echo Next steps:
echo   1. Edit .env with your Azure OpenAI credentials
echo   2. Run Phase 1: cd document-rag-pipeline
echo      - python main.py (to ingest documents)
echo      - python vectorize.py (to create vectors)
echo   3. Run Phase 2: cd ..
echo      - python src/main_app.py (interactive CLI)
echo      - python src/api_server.py (REST API)
echo   4. For debugging: python src/debug_tools.py
echo.
echo venv is activated in this terminal.
echo Close and reopen terminal to re-activate.
echo.
pause
