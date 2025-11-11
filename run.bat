@echo off
REM Quick run script for Job Description Generator
REM Activates virtual environment and launches the application

echo Starting Job Description Generator...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found!
    echo Please run setup.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if Streamlit is installed
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo Streamlit not found!
    echo Please run setup.bat to install dependencies.
    pause
    exit /b 1
)

REM Launch the application
echo Launching application...
echo The app will open in your default browser.
echo Press Ctrl+C to stop the application.
echo.

streamlit run app.py
