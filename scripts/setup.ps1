#!/usr/bin/env pwsh
# Quick setup script for Vivere con il Cane development environment (Windows/PowerShell)

$ErrorActionPreference = 'Stop'

Write-Host "🐕 Vivere con il Cane - Quick Setup" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

function Log-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Log-Warn {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Log-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check Python
Log-Info "Checking Python installation..."
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Log-Error "Python 3.11+ non trovato. Installa Python e riprova."
    exit 1
}

$pythonVersion = python -c "import sys; print('.'.join(map(str, sys.version_info[:2])))"
Log-Info "Python version: $pythonVersion"

# Create virtual environment
if (-not (Test-Path "venv")) {
    Log-Info "Creating virtual environment..."
    python -m venv venv
} else {
    Log-Info "Virtual environment already exists"
}

# Activate venv
Log-Info "Activating virtual environment..."
& .\venv\Scripts\Activate.ps1

# Upgrade pip
Log-Info "Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
Log-Info "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Install dev dependencies
Log-Info "Installing development dependencies..."
pip install pytest pytest-django pytest-cov black ruff

# Create .env if not exists
if (-not (Test-Path ".env")) {
    Log-Info "Creating .env from template..."
    Copy-Item .env.example .env
    Log-Warn "⚠️  Please edit .env and add your:"
    Log-Warn "   - SECRET_KEY (generate one: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"
    Log-Warn "   - GROQ_API_KEY (get from https://console.groq.com/)"
    Log-Warn "   - (Optional) Google OAuth credentials"
} else {
    Log-Info ".env file already exists"
}

# Run migrations
Log-Info "Running database migrations..."
python manage.py migrate --noinput

# Load fixtures
Log-Info "Loading knowledge fixtures..."
python manage.py loaddata knowledge/fixtures/knowledge_data.json --ignorenonexistent 2>$null || $true

Log-Info "Loading blog fixtures..."
python manage.py loaddata blog/fixtures/blog_data.json --ignorenonexistent 2>$null || $true

# Check superuser
Log-Info "Checking for superuser..."
$superuserExists = python manage.py shell -c "from django.contrib.auth.models import User; print('YES' if User.objects.filter(is_superuser=True).exists() else 'NO')" 2>$null
if ($superuserExists -eq "NO") {
    Log-Warn "No superuser found. Create one with: python manage.py createsuperuser"
} else {
    Log-Info "Superuser already exists"
}

# Collect static files
Log-Info "Collecting static files..."
python manage.py collectstatic --noinput

Write-Host ""
Log-Info "✅ Setup completato!"
Write-Host ""
Write-Host "Per avviare il server di sviluppo:"
Write-Host "  venv\Scripts\Activate.ps1"
Write-Host "  python manage.py runserver"
Write-Host ""
Write-Host "Visita: http://127.0.0.1:8000"
Write-Host ""
Log-Warn "Non dimenticare di configurare il file .env con le API keys!"
