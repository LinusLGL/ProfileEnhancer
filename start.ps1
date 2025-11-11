# Quick Start Script for Job Description Generator
# Run this script to set up and launch the application

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Job Description Generator - Quick Start" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "✓ $pythonVersion found" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.8 or higher" -ForegroundColor Red
    exit 1
}

# Check if virtual environment exists
if (-Not (Test-Path "venv")) {
    Write-Host ""
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Check if requirements are installed
Write-Host ""
Write-Host "Checking dependencies..." -ForegroundColor Yellow
$installed = pip list 2>$null
if ($installed -notmatch "streamlit") {
    Write-Host "Installing dependencies (this may take a few minutes)..." -ForegroundColor Yellow
    pip install -r requirements.txt
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✓ Dependencies already installed" -ForegroundColor Green
}

# Check for .env file
Write-Host ""
if (-Not (Test-Path ".env")) {
    Write-Host "⚠ Warning: .env file not found" -ForegroundColor Yellow
    Write-Host "You'll need to enter your OpenAI API key in the application" -ForegroundColor Yellow
    Write-Host ""
    $createEnv = Read-Host "Would you like to create a .env file now? (y/n)"
    if ($createEnv -eq "y") {
        $apiKey = Read-Host "Enter your OpenAI API key"
        "OPENAI_API_KEY=$apiKey" | Out-File -FilePath ".env" -Encoding utf8
        Write-Host "✓ .env file created" -ForegroundColor Green
    }
} else {
    Write-Host "✓ .env file found" -ForegroundColor Green
}

# Launch the application
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Launching Streamlit application..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "The application will open in your default browser" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the application" -ForegroundColor Yellow
Write-Host ""

streamlit run app.py
