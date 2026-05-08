#!/bin/bash
# Quick setup script for Vivere con il Cane development environment

set -e

echo "🐕 Vivere con il Cane - Quick Setup"
echo "===================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check Python
log_info "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    log_error "Python 3.11+ non trovato. Installa Python e riprova."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
log_info "Python version: $PYTHON_VERSION"

# Create virtual environment
if [ ! -d "venv" ]; then
    log_info "Creating virtual environment..."
    python3 -m venv venv
else
    log_info "Virtual environment already exists"
fi

# Activate venv
log_info "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
log_info "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
log_info "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Install dev dependencies
log_info "Installing development dependencies..."
pip install pytest pytest-django pytest-cov black ruff

# Create .env if not exists
if [ ! -f ".env" ]; then
    log_info "Creating .env from template..."
    cp .env.example .env
    log_warn "⚠️  Please edit .env and add your:"
    log_warn "   - SECRET_KEY (generate one: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"
    log_warn "   - GROQ_API_KEY (get from https://console.groq.com/)"
    log_warn "   - (Optional) Google OAuth credentials"
else
    log_info ".env file already exists"
fi

# Run migrations
log_info "Running database migrations..."
python manage.py migrate --noinput

# Load fixtures
log_info "Loading knowledge fixtures..."
python manage.py loaddata knowledge/fixtures/knowledge_data.json --ignorenonexistent || true

log_info "Loading blog fixtures..."
python manage.py loaddata blog/fixtures/blog_data.json --ignorenonexistent || true

# Create superuser if not exists
log_info "Checking for superuser..."
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(is_superuser=True).exists() or print('MISSING')" 2>/dev/null | grep -q MISSING && {
    log_warn "No superuser found. Create one with: python manage.py createsuperuser"
} || log_info "Superuser already exists"

# Collect static files
log_info "Collecting static files..."
python manage.py collectstatic --noinput

echo ""
log_info "✅ Setup completato!"
echo ""
echo "Per avviare il server di sviluppo:"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "Visita: http://127.0.0.1:8000"
echo ""
log_warn "Non dimenticare di configurare il file .env con le API keys!"
