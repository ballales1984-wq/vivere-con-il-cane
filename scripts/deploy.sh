#!/bin/bash
# Vivere con il Cane - Deployment Helper Scripts
# Questi script semplificano operazioni comuni di sviluppo e deployment

set -e  # Exit on error

echo "🐕 Vivere con il Cane - Deployment Helper"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Helper function
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Main menu
show_menu() {
    echo ""
    echo "Seleziona un'operazione:"
    echo "  1) Setup ambiente sviluppp (locale)"
    echo "  2) Inizializza database (migrazioni + fixtures)"
    echo "  3) Esegui test completi"
    echo "  4) Build Docker image"
    echo "  5) Deploy su Render (tramite git)"
    echo "  6) Pulisci file temporanei"
    echo "  7) Genera report coverage"
    echo "  8) Crea superuser"
    echo "  9) Esci"
    echo ""
    read -p "Scelta [1-9]: " choice
}

# 1. Setup ambiente locale
setup_local() {
    log_info "Setup ambiente di sviluppo..."

    if [ ! -d "venv" ]; then
        log_info "Creazione virtual environment..."
        python3 -m venv venv
    fi

    log_info "Attivazione venv..."
    source venv/bin/activate

    log_info "Installazione dipendenze..."
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install pytest pytest-django pytest-cov black ruff

    if [ ! -f ".env" ]; then
        log_info "Copia .env.example in .env..."
        cp .env.example .env
        log_warn "Modifica il file .env con le tue configurazioni!"
    fi

    log_info "Setup completato. Attiva il venv con: source venv/bin/activate"
}

# 2. Inizializza database
init_db() {
    log_info "Inizializzazione database..."

    if [ -z "${VIRTUAL_ENV}" ]; then
        log_warn "Consigliato attivare il venv prima"
    fi

    python manage.py migrate --noinput
    log_info "Migrazioni applicate"

    # Load fixtures if available
    if [ -f "knowledge/fixtures/knowledge_data.json" ]; then
        python manage.py loaddata knowledge/fixtures/knowledge_data.json --ignorenonexistent
        log_info "Knowledge fixtures caricate"
    fi

    if [ -f "blog/fixtures/blog_data.json" ]; then
        python manage.py loaddata blog/fixtures/blog_data.json --ignorenonexistent
        log_info "Blog fixtures caricate"
    fi

    log_info "Database pronto!"
}

# 3. Esegui test
run_tests() {
    log_info "Esecuzione test suite..."

    if [ -z "${VIRTUAL_ENV}" ]; then
        log_warn "Attivazione venv consigliata"
    fi

    # Run with coverage
    python -m pytest --ds=config.settings -v --cov=. --cov-report=term --cov-report=html

    log_info "Test completati. Report coverage in htmlcov/index.html"
}

# 4. Build Docker
build_docker() {
    log_info "Build Docker image..."

    docker build -t vivere-con-il-cane:latest .

    log_info "Image creata: vivere-con-il-cane:latest"
    log_info "Per eseguire: docker-compose up -d"
}

# 5. Deploy su Render
deploy_render() {
    log_info "Deploy su Render..."

    if ! command_exists git; then
        log_error "Git non installato"
        exit 1
    fi

    echo ""
    log_info "Verifica configurazione per deployment:"
    echo "  1. Assicurati che il repository sia su GitHub"
    echo "  2. Crea Web Service su Render.com"
    echo "  3. Collega il repository"
    echo "  4. Build command: pip install -r requirements.txt"
    echo "  5. Start command: gunicorn config.wsgi:application"
    echo ""
    read -p "Il repository è già su GitHub e configurato su Render? (s/N): " confirm

    if [[ $confirm =~ ^[Ss]$ ]]; then
        log_info "Push a Git per trigger auto-deploy..."
        git add .
        git commit -m "Deploy: $(date '+%Y-%m-%d %H:%M')" || log_warn "Nessun cambiamento da committare"
        git push origin main || log_error "Push fallito"
        log_info "Deploy triggerato! Attendi 2-5 minuti."
    else
        log_warn "Configura prima il deployment su Render"
    fi
}

# 6. Pulisci file temporanei
clean_temp() {
    log_info "Pulizia file temporanei..."

    # Python cache
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -delete 2>/dev/null || true

    # Coverage
    rm -rf htmlcov/ .coverage coverage.xml 2>/dev/null || true

    # Django static/media
    rm -rf staticfiles/ media/tmp 2>/dev/null || true

    # Logs
    rm -rf *.log start*.log test_*.log 2>/dev/null || true

    # Temporary files
    rm -rf temp_release/ envelope_debug.json 2>/dev/null || true

    log_info "Pulizia completata"
}

# 7. Coverage report
coverage_report() {
    log_info "Generazione report coverage dettagliato..."

    python -m pytest --ds=config.settings --cov=. --cov-report=term-missing:skip-covered --cov-report=html

    echo ""
    log_info "Report HTML: file://$(pwd)/htmlcov/index.html"
    log_info "Report Test: TEST_REPORT.md (da generare con: python -m pytest --ds=config.settings -v > TEST_REPORT.md)"
}

# 8. Crea superuser
create_superuser() {
    log_info "Creazione superuser..."
    python manage.py createsuperuser
}

# Main loop
while true; do
    show_menu
    case $choice in
        1) setup_local ;;
        2) init_db ;;
        3) run_tests ;;
        4) build_docker ;;
        5) deploy_render ;;
        6) clean_temp ;;
        7) coverage_report ;;
        8) create_superuser ;;
        9) log_info "Uscita..."; exit 0 ;;
        *) log_error "Scelta non valida" ;;
    esac
    echo ""
    read -p "Premi INVIO per continuare..."
done
