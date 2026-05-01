FROM python:3.11-slim

WORKDIR /app

# Installa dipendenze di sistema
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    pkg-config \
    libcairo2-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements e installa
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia il codice
COPY . .

# Crea directory per i log e staticfiles
RUN mkdir -p /app/logs /app/staticfiles

# Raccogli static files con una SECRET_KEY temporanea per la build
RUN SECRET_KEY=build-time-dummy-secret-key-not-used-in-prod DEBUG=False \
    python manage.py collectstatic --noinput

EXPOSE 8000

# Usa gunicorn per la produzione
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120"]
