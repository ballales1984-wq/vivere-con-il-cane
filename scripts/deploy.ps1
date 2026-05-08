#!/usr/bin/env pwsh
# Vivere con il Cane - Deployment Helper Scripts for Windows/PowerShell
# Questi script semplificano operazioni comuni di sviluppo e deployment

$ErrorActionPreference = 'Stop'

Write-Host "🐕 Vivere con il Cane - Deployment Helper" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Helper functions
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

# Check if command exists
function Command-Exists {
    param([string]$Command)
    $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
}

# Main menu
function Show-Menu {
    Clear-Host
    Write-Host ""
    Write-Host "Seleziona un'operazione:"
    Write-Host "  1) Setup ambiente sviluppo (locale)"
    Write-Host "  2) Inizializza database (migrazioni + fixtures)"
    Write-Host "  3) Esegui test completi"
    Write-Host "  4) Build Docker image"
    Write-Host "  5) Deploy su Render (tramite git)"
    Write-Host "  6) Pulisci file temporanei"
    Write-Host "  7) Genera report coverage"
    Write-Host "  8) Crea superuser"
    Write-Host "  9) Esci"
    Write-Host ""
    $choice = Read-Host "Scelta [1-9]"
    return $choice
}

# 1. Setup ambiente locale
function Setup-Local {
    Log-Info "Setup ambiente di sviluppo..."

    if (-not (Test-Path "venv")) {
        Log-Info "Creazione virtual environment..."
        python -m venv venv
    }

    Log-Info "Attivazione venv..."
    .\venv\Scripts\Activate.ps1

    Log-Info "Installazione dipendenze..."
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    pip install pytest pytest-django pytest-cov black ruff

    if (-not (Test-Path ".env")) {
        Log-Info "Copia .env.example in .env..."
        Copy-Item .env.example .env
        Log-Warn "Modifica il file .env con le tue configurazioni!"
    }

    Log-Info "Setup completato. Attiva il venv con: venv\Scripts\Activate.ps1"
    Read-Host "Premi INVIO per continuare"
}

# 2. Inizializza database
function Init-DB {
    Log-Info "Inizializzazione database..."

    if ($env:VIRTUAL_ENV -eq $null) {
        Log-Warn "Consigliato attivare il venv prima"
    }

    python manage.py migrate --noinput
    Log-Info "Migrazioni applicate"

    # Load fixtures if available
    if (Test-Path "knowledge/fixtures/knowledge_data.json") {
        python manage.py loaddata knowledge/fixtures/knowledge_data.json --ignorenonexistent
        Log-Info "Knowledge fixtures caricate"
    }

    if (Test-Path "blog/fixtures/blog_data.json") {
        python manage.py loaddata blog/fixtures/blog_data.json --ignorenonexistent
        Log-Info "Blog fixtures caricate"
    }

    Log-Info "Database pronto!"
    Read-Host "Premi INVIO per continuare"
}

# 3. Esegui test
function Run-Tests {
    Log-Info "Esecuzione test suite..."

    if ($env:VIRTUAL_ENV -eq $null) {
        Log-Warn "Attivazione venv consigliata"
    }

    # Run with coverage
    python -m pytest --ds=config.settings -v --cov=. --cov-report=term --cov-report=html

    Log-Info "Test completati. Report coverage in htmlcov/index.html"
    Read-Host "Premi INVIO per continuare"
}

# 4. Build Docker
function Build-Docker {
    Log-Info "Build Docker image..."

    docker build -t vivere-con-il-cane:latest .

    Log-Info "Image creata: vivere-con-il-cane:latest"
    Log-Info "Per eseguire: docker-compose up -d"
    Read-Host "Premi INVIO per continuare"
}

# 5. Deploy su Render
function Deploy-Render {
    Log-Info "Deploy su Render..."

    if (-not (Command-Exists "git")) {
        Log-Error "Git non installato"
        exit 1
    }

    Write-Host ""
    Log-Info "Verifica configurazione per deployment:"
    Write-Host "  1. Assicurati che il repository sia su GitHub"
    Write-Host "  2. Crea Web Service su Render.com"
    Write-Host "  3. Collega il repository"
    Write-Host "  4. Build command: pip install -r requirements.txt"
    Write-Host "  5. Start command: gunicorn config.wsgi:application"
    Write-Host ""
    $confirm = Read-Host "Il repository è già su GitHub e configurato su Render? (s/N)"

    if ($confirm -match '^[Ss]$') {
        Log-Info "Push a Git per trigger auto-deploy..."
        git add .
        git commit -m "Deploy: $(Get-Date -Format 'yyyy-MM-dd HH:mm')" 2>$null
        if ($LASTEXITCODE -ne 0) {
            Log-Warn "Nessun cambiamento da committare"
        }
        git push origin main
        Log-Info "Deploy triggerato! Attendi 2-5 minuti."
    } else {
        Log-Warn "Configura prima il deployment su Render"
    }
    Read-Host "Premi INVIO per continuare"
}

# 6. Pulisci file temporanei
function Clean-Temp {
    Log-Info "Pulizia file temporanei..."

    # Python cache
    Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Path . -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Path . -Recurse -Filter "*.pyo" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue

    # Coverage
    Remove-Item -Recurse -Force htmlcov, .coverage, coverage.xml -ErrorAction SilentlyContinue

    # Django static/media
    Remove-Item -Recurse -Force staticfiles, media/tmp -ErrorAction SilentlyContinue

    # Logs
    Get-ChildItem -Path . -Filter "*.log" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Path . -Filter "start*.log" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Path . -Filter "test_*.log" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue

    # Temporary files
    Remove-Item -Recurse -Force temp_release, envelope_debug.json -ErrorAction SilentlyContinue

    Log-Info "Pulizia completata"
    Read-Host "Premi INVIO per continuare"
}

# 7. Coverage report
function Coverage-Report {
    Log-Info "Generazione report coverage dettagliato..."

    python -m pytest --ds=config.settings --cov=. --cov-report=term-missing:skip-covered --cov-report=html

    Write-Host ""
    Log-Info "Report HTML: file://$(Get-Location)/htmlcov/index.html"
    Log-Info "Report Test: TEST_REPORT.md (da generare con: python -m pytest --ds=config.settings -v > TEST_REPORT.md)"
    Read-Host "Premi INVIO per continuare"
}

# 8. Crea superuser
function Create-Superuser {
    Log-Info "Creazione superuser..."
    python manage.py createsuperuser
    Read-Host "Premi INVIO per continuare"
}

# Main loop
while ($true) {
    $choice = Show-Menu

    switch ($choice) {
        '1' { Setup-Local }
        '2' { Init-DB }
        '3' { Run-Tests }
        '4' { Build-Docker }
        '5' { Deploy-Render }
        '6' { Clean-Temp }
        '7' { Coverage-Report }
        '8' { Create-Superuser }
        '9' {
            Log-Info "Uscita..."
            exit 0
        }
        default {
            Log-Error "Scelta non valida"
            Start-Sleep -Seconds 2
        }
    }
}
