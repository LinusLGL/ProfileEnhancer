@echo off
REM Job Description Generator - Windows Installation Script
REM For users who prefer Command Prompt over PowerShell

echo ========================================
echo Job Description Generator - Setup
echo ========================================
echo.

REM Check Python installation
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.8 or higher from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment already exists
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1
echo [OK] pip upgraded
echo.

REM Install requirements
echo Installing dependencies...
echo This may take a few minutes...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

REM Check for .env file
if not exist ".env" (
    echo.
    echo ========================================
    echo WARNING: .env file not found
    echo ========================================
    echo.
    echo You need an OpenAI API key to use this application.
    echo.
    echo Option 1: Create .env file manually
    echo    - Copy env_template.txt to .env
    echo    - Add your OpenAI API key
    echo.
    echo Option 2: Enter API key in the application
    echo    - You can enter it when the app starts
    echo.
    set /p create_env="Would you like to create .env file now? (y/n): "
    if /i "%create_env%"=="y" (
        set /p api_key="Enter your OpenAI API key: "
        echo OPENAI_API_KEY=!api_key! > .env
        echo [OK] .env file created
    )
) else (
    echo [OK] .env file found
)
echo.

REM Create sample Excel file
echo Creating sample Excel file...
python create_sample_excel.py >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Could not create sample Excel file
) else (
    echo [OK] Sample Excel file created: sample_input.xlsx
)
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the application, run:
echo    streamlit run app.py
echo.
echo Or simply run:
echo    start.ps1 (PowerShell)
echo    run.bat (Command Prompt)
echo.
echo Documentation:
echo    - README.md: Quick overview
echo    - SETUP_GUIDE.md: Detailed instructions
echo    - QUICK_START.md: Getting started guide
echo.
pause
