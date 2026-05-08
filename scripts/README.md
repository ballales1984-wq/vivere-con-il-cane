# Vivere con il Cane - Deployment Scripts

Questa cartella contiene script di utilità per semplificare operazioni di setup, deployment e manutenzione del progetto.

## 📜 Scripts Disponibili

### `setup.sh` / `setup.ps1` (Setup Rapido)
Configura l'ambiente di sviluppo da zero.

**Linux/macOS:**
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

**Windows PowerShell:**
```powershell
.\scripts\setup.ps1
```

**Cosa fa:**
- Crea virtual environment
- Installa tutte le dipendenze (prod + dev)
- Crea file `.env` da `.env.example`
- Applica migrazioni database
- Carica fixtures (knowledge, blog)
- Cerca/verifica superuser
- Colleziona static files

---

### `deploy.sh` / `deploy.ps1` (Menu Interattivo)
Menu interattivo con tutte le operazioni comuni.

**Linux/macOS:**
```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

**Windows PowerShell:**
```powershell
.\scripts\deploy.ps1
```

**Operazioni disponibili:**
1. **Setup ambiente sviluppo** — come `setup.sh` ma interattivo
2. **Inizializza database** — migrate + loaddata
3. **Esegui test completi** — pytest con coverage
4. **Build Docker image** — `docker build`
5. **Deploy su Render** — git push per auto-deploy
6. **Pulisci file temporanei** — rimuove cache, logs, coverage
7. **Genera report coverage** — output dettagliato
8. **Crea superuser** — `createsuperuser`
9. **Esci**

---

### `test_all.sh` (Test Suite Completa)
Esegue tutti i test con configurazioni diverse.

```bash
chmod +x scripts/test_all.sh
./scripts/test_all.sh
```

Output:
- Test normali (DEBUG=True)
- Test in modalità debug
- Coverage report HTML

---

### `deploy_docker.sh` (Deployment Docker Completo)
Build e deploy in un comando solo.

```bash
chmod +x scripts/deploy_docker.sh
./scripts/deploy_docker.sh
```

Comprende:
- Build image
- Stop container vecchio
- Run nuovo container
- Show logs

---

### `clean.sh` / `clean.ps1` (Pulizia Completa)
Rimuove tutti i file temporanei, cache, database di sviluppo.

```bash
# Linux/macOS
./scripts/clean.sh

# Windows
.\scripts\clean.ps1
```

Rimuove:
- `__pycache__/`, `*.pyc`, `*.pyo`
- `htmlcov/`, `.coverage`, `coverage.xml`
- `staticfiles/` (Django collected static)
- `*.log` (tutti i log)
- `db.sqlite3` (solo se development)
- `temp_release/`, `envelope_debug.json`

---

## 🚀 Uso Rapido (One-liner)

```bash
# Setup completo in una riga (Linux/macOS)
curl -s https://raw.githubusercontent.com/ballales1984-wq/vivere-con-il-cane/main/scripts/setup.sh | bash

# Windows PowerShell
Invoke-WebRequest -Uri https://raw.githubusercontent.com/ballales1984-wq/vivere-con-il-cane/main/scripts/setup.ps1 -OutFile setup.ps1; .\setup.ps1
```

---

## 📋 Prerequisiti

- Python 3.11 o 3.12
- pip
- (Opzionale) Docker per container
- (Opzionale) Git per deployment

---

## 🔧 Configurazione

Prima del deployment, assicurati di aver configurato:

1. **Variabili d'ambiente** in `.env`:
   ```bash
   SECRET_KEY=<genera-chiave-sicura>
   GROQ_API_KEY=<da-console.groq.com>
   DATABASE_URL=postgres://...
   ```

2. **Database di produzione** (PostgreSQL):
   ```bash
   # Su Render.com, la variabile DATABASE_URL viene fornita automaticamente
   # Localmente: crea un DB PostgreSQL o usa SQLite per development
   ```

3. **OAuth Google** (opzionale):
   - Vai su Google Cloud Console
   - Crea OAuth 2.0 credentials
   - Aggiungi redirect URI: `https://vivere-con-il-cane.onrender.com/auth/google/callback`
   - Inserisci ID e Secret in `.env`

---

## 🐳 Docker vs Native

### **Docker (Consigliato per produzione)**
```bash
# Build e run con docker-compose
docker-compose up -d

# View logs
docker-compose logs -f web

# Stop
docker-compose down
```

### **Native (Sviluppo locale)**
```bash
# Dopo setup.sh
source venv/bin/activate  # Linux/macOS
# o
venv\Scripts\Activate.ps1  # Windows

python manage.py runserver
```

---

## 🧪 Testing

```bash
# Tutti i test
./scripts/deploy.sh  # opzione 3

# Test specifico app
python manage.py test blog canine_tools --debug-mode

# Coverage dettagliato
./scripts/deploy.sh  # opzione 7

# Test paralleli (se pytest-xinstallato)
pytest --ds=config.settings -n auto
```

---

## 📦 Deployment

### **Render.com (Auto-Deploy)**
```bash
# Trigger deploy manuale
./scripts/deploy.sh  # opzione 5

# Oppure push manuale
git add .
git commit -m "Deploy: description"
git push origin main
```

Render auto-deployerà in 2-5 minuti.

### **Docker (Self-Hosted)**
```bash
./scripts/deploy_docker.sh
```

---

## 🛠️ Manutenzione

### **Database Backup**
```bash
# Backup manuale SQLite (development)
cp db.sqlite3 db.sqlite3.backup

# PostgreSQL (production)
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
```

### **Aggiornare fixtures**
```bash
# Ricreare fixtures da dati attuali
python manage.py dumpdata knowledge --indent 2 > knowledge/fixtures/knowledge_data.json
python manage.py dumpdata blog --indent 2 > blog/fixtures/blog_data.json
```

### **Pulizia cache**
```bash
./scripts/clean.sh
```

---

## 📁 Struttura Cartelle

```
vivere-con-il-cane/
├── scripts/
│   ├── setup.sh               # Setup automatico (Unix)
│   ├── setup.ps1              # Setup automatico (Windows)
│   ├── deploy.sh              # Menu interattivo (Unix)
│   ├── deploy.ps1             # Menu interattivo (Windows)
│   ├── deploy_docker.sh       # Deploy Docker completo
│   ├── test_all.sh            # Test suite automatizzata
│   ├── clean.sh               # Pulizia (Unix)
│   ├── clean.ps1              # Pulizia (Windows)
│   └── README.md              # Questo file
├── .env.example               # Template variabili ambiente
├── requirements.txt           # Dipendenze Python
├── docker-compose.yml         # Docker config
├── Dockerfile                 # Container image
└── manage.py                  # Django CLI
```

---

## ⚠️ Note Importanti

- **Non committare** il file `.env` — è in `.gitignore`
- **GROQ_API_KEY** è richiesta per l'AI; senza, le funzioni AI non funzionano
- In produzione, **DEBUG=False** obbligatorio
- I test richiedono **PostgreSQL** per passare completamente (locale usa SQLite)
- I fixtures sono opzionali; il sito funziona anche senza

---

## 🆘 Troubleshooting

### "python: command not found"
Installa Python 3.11+ da python.org e aggiungi al PATH.

### "ModuleNotFoundError: No module named 'django'"
Attiva il virtual environment: `source venv/bin/activate` o `venv\Scripts\Activate.ps1`

### "Permission denied" su script Unix
```bash
chmod +x scripts/*.sh
```

### Groq API non funziona
Verifica che `GROQ_API_KEY` sia corretta in `.env`. Test:
```bash
python manage.py shell -c "from canine_tools.services.ai_client import test_groq; test_groq()"
```

### Database errors
```bash
# Resetta database (ATTENZIONE: perde tutti i dati!)
python manage.py flush --noinput
./scripts/deploy.sh  # opzione 2 (re-migrate)
```

---

## 📞 Supporto

- **Issues:** https://github.com/ballales1984-wq/vivere-con-il-cane/issues
- **Documentazione principale:** README.md
- **Guida contribuzione:** CONTRIBUTING.md

---

**Made with ❤️ for dogs and their humans**
