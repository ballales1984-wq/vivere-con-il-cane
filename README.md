# 🐕 Vivere con il Cane

> **Piattaforma educativa per l'analisi del comportamento canino con AI avanzata**  
> Blog di educazione cinofila con strumenti gratuiti, community e analisi intelligente del comportamento

[![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-FFD43B?style=for-the-badge&logo=python&logoColor=blue)](https://www.python.org/)
[![AI](https://img.shields.io/badge/AI-Groq%20Llama%203-orange?style=for-the-badge)](https://groq.com/)
[![License MIT](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-vivere--con--il--cane.onrender.com-brightgreen?style=for-the-badge)](https://vivere-con-il-cane.onrender.com)

🌍 [**Leggi la documentazione in italiano →**](README.it.md)

---

## 📸 Anteprima dell'Applicazione

### 🏠 Homepage - Analisi IA del Comportamento
![Homepage - Vivere con il Cane](https://raw.githubusercontent.com/ballales1984-wq/vivere-con-il-cane/main/docs/screenshots/homepage.png)

### 📚 Blog Hub
![Blog Section](https://raw.githubusercontent.com/ballales1984-wq/vivere-con-il-cane/main/docs/screenshots/blog-section.png)

---

## 📚 Indice

- [✨ Caratteristiche Principali](#-caratteristiche-principali)
- [🎯 Proposta di Valore](#-proposta-di-valore-unica)
- [🏗️ Architettura di Sistema](#️-architettura-di-sistema)
- [🛠️ Stack Tecnologico](#️-stack-tecnologico)
- [📦 Installazione](#-installazione)
- [🔧 Configurazione](#-configurazione)
- [🚀 Utilizzo](#-utilizzo)
- [🧪 Testing](#-testing)
- [☁️ Deployment](#️-deployment)
- [📡 Endpoint API](#-endpoint-api)
- [❤️ Analisi dei Suoni Cardiaci](#️-analisi-dei-suoni-cardiaci)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## ✨ Caratteristiche Principali

### 🧠 AI & Analisi Comportamentale
- **Analisi del Comportamento con IA**: Descrivi il comportamento del tuo cane e ricevi consigli personalizzati  
- **Memoria Longitudinale**: L'IA mantiene la cronologia medica del cane per analisi più accurate

### 🛠️ Strumenti Gratuiti Interattivi
- **Calcolatore del Cibo** - Porzioni giuste per il tuo cane
- **Convertitore di Età** - Anni del cane a anni umani
- **Quiz sulla Comunicazione Canina** - Testa la tua conoscenza
- **Registratore Cardiaco** - Monitora il battito del tuo cane

### 📚 Risorse Educative
- **Hub di Apprendimento**: Articoli, guide e risorse su educazione, salute e nutrizione
- **Base di Conoscenza Strutturata**: Matrice relazionale sintomi-cause-soluzioni
- **Blog SEO Ottimizzato**: Contenuti per proprietari di cani

### 👥 Community e Social
- **Forum Comunità**: Condividi esperienze e ricevi supporto da altri proprietari
- **Newsletter Automatizzata**: Sequenza di onboarding con email personalizzate
- **Dashboard Personale**: Traccia il profilo del tuo cane e la cronologia delle analisi

### 🌐 Esperienza Utente Moderna
- **Multi-lingua**: Supporto italiano e inglese
- **PWA Ready**: Funziona offline, installabile come app mobile
- **Design Moderno**: Glassmorphism design con gradienti accattivanti
- **SEO Ottimizzato**: Meta tag, structured data (JSON-LD), sitemap
- **Ready per Pubblicità**: Integrazione Google AdSense

### 🔒 Sicurezza
- **Autenticazione Robusta**: Password reset, verifica email, OAuth
- **Social Login**: Accesso con Google e altri provider
- **Privacy First**: Rispetto della privacy degli utenti

---

## 🎯 Proposta di Valore Unica

### 1️⃣ **Motore IA con Memoria Longitudinale (Dynamic Routing)**
A differenza dei semplici wrapper di ChatGPT, il nostro motore IA (powered by Llama-3 via Groq) utilizza routing contestuale:
- ✅ Gestisce un **Profilo Medico Persistente** per ogni cane (età, peso, genetica)
- ✅ Prima di interrogare l'LLM, il backend genera algoritmicamente un "Super-Prompt" che inietta l'intera cronologia clinica
- ✅ **Risultato**: Quando l'utente scrive "zoppica", l'IA sa automaticamente che analizza un *meticcio di 10 anni in sovrappeso con storia di artrite*, fornendo risposte **10x più accurate**

### 2️⃣ **Cartella Medica Unificata (Pronta per il Veterinario)**
- Unisce le "viste mediche" tradizionali (vaccini, infortuni) con la **cronologia delle analisi comportamentali IA** in un'unica Timeline
- Export in stile **WhatsApp** o generazione di **PDF puliti** perfetti da allegare al veterinario
- Preparazione per integrazione future con portali veterinari

### 3️⃣ **Matrice Relazionale (Sintomi-Cause-Soluzioni)**
Il cuore del sistema non è un semplice blog testuale. La nostra *Knowledge Base* è una matrice strutturata nel database:
- Sintomi, Cause Scatenanti e Rimedi Pratici sono entità distinte collegate nel backend
- L'IA non "azzarda": usa questa matrice incrociandola con il profilo della razza per mappare in tempo reale il problema alla causa più probabile

### 4️⃣ **HealthTech Platform Orientata alla Conversione**
- L'interfaccia si presenta come un **Premium Hub** con design Glassmorphism
- Adozione completa delle direttive SEO con **Schema.org JSON-LD** per trasformare i lettori occasionali dei motori di ricerca in utenti abituali della piattaforma diagnostica

---

## 🏗️ Architettura di Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                      VIVERE CON IL CANE                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐         ┌────────────────────────┐   │
│  │   Frontend       │◄────────│   Django Backend       │   │
│  │  (HTML/CSS/JS)   │         │  (Python 3.10+)        │   │
│  └──────────────────┘         └────────────────────────┘   │
│                                          │                   │
│                        ┌─────────────────┼─────────────────┐ │
│                        ▼                 ▼                 ▼ │
│                  ┌──────────┐     ┌──────────┐     ┌─────────┐ │
│                  │ SQLite   │     │PostgreSQL│     │Groq LLM │ │
│                  │(Dev)     │     │(Prod)    │     │(IA)     │ │
│                  └──────────┘     └──────────┘     └─────────┘ │
│                                                               │
│                         DATA LAYER                           │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Stack Tecnologico

| Componente | Tecnologia | Versione |
|-----------|-----------|----------|
| **Backend** | Django | 4.2+ |
| **Linguaggio** | Python | 3.10+ |
| **Frontend** | HTML5 + CSS3 + HTMX | Latest |
| **Database (Dev)** | SQLite | 3.x |
| **Database (Prod)** | PostgreSQL | 12+ |
| **AI/ML** | Groq API + Llama 3 | Latest |
| **Server (Prod)** | Gunicorn | 21.0+ |
| **Static Files** | WhiteNoise | Latest |
| **Container** | Docker | Latest |
| **Autenticazione** | django-allauth | 65.0+ |
| **Email** | SMTP / Console | - |

**Dipendenze Principali:**
- `Django`: Framework web principale
- `django-allauth`: Autenticazione social (Google, etc.)
- `groq`: SDK per API AI
- `gunicorn`: Server WSGI per produzione
- `dj-database-url`: Gestione URL database

---

## 📦 Installazione

### Prerequisiti

```bash
✓ Python 3.10+ (recommended 3.10 or 3.11)
✓ pip (Package Manager)
✓ Git
✓ Docker (opzionale)
✓ PostgreSQL (opzionale, per produzione)
```

### Guida Rapida

#### 1️⃣ Clone del Repository
```bash
git clone https://github.com/ballales1984-wq/vivere-con-il-cane.git
cd vivere-con-il-cane
```

#### 2️⃣ Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3️⃣ Installa Dipendenze
```bash
pip install -r requirements.txt
```

#### 4️⃣ Configurazione Environment
```bash
# Crea file .env
cp .env.example .env

# Modifica .env con le tue impostazioni
# Variabili minime:
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
```

#### 5️⃣ Inizializza Database
```bash
# Crea le tabelle
python manage.py migrate

# Carica dati di esempio (opzionale)
python manage.py loaddata knowledge/fixtures/knowledge_data.json --ignorenonexistent
python manage.py loaddata blog/fixtures/blog_data.json --ignorenonexistent

# Crea superuser
python manage.py createsuperuser

# Oppure usa credenziali di default:
# Admin: admin@vivereconilcane.com / Admin123!
# Test: test@vivereconilcane.com / Test123!
```

#### 6️⃣ Avvia Development Server
```bash
python manage.py runserver
```

✅ Visita: http://127.0.0.1:8000

---

## 🔧 Configurazione

### Variabili di Ambiente

| Variabile | Descrizione | Esempio |
|-----------|-----------|---------|
| `DEBUG` | Modalità debug | `True` / `False` |
| `SECRET_KEY` | Chiave segreta Django | `django-insecure-...` |
| `ALLOWED_HOSTS` | Host consentiti | `localhost,127.0.0.1` |
| `DATABASE_URL` | URL database | `sqlite:///db.sqlite3` |
| `EMAIL_BACKEND` | Backend email | `django.core.mail.backends.console.EmailBackend` |
| `GROQ_API_KEY` | API Key Groq/Llama | `gsk_...` |
| `OPENAI_API_KEY` | API Key OpenAI (fallback) | `sk-...` |
| `GOOGLE_OAUTH_CLIENT_ID` | Google OAuth ID | `...googleusercontent.com` |
| `GOOGLE_OAUTH_CLIENT_SECRET` | Google OAuth Secret | `GOCSPX-...` |

### Configurazione Email

**Development (Console Backend):**
```bash
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

**Production (SMTP):**
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Configurazione IA (Groq/Llama)

```bash
# API Key Groq (primaria)
GROQ_API_KEY=gsk_your-api-key-from-groq

# API Key OpenAI (fallback)
OPENAI_API_KEY=sk-your-openai-key
```

---

## 🚀 Utilizzo

### Dashboard Admin

Accedi a: `/admin/` con le credenziali di superuser

### URL Principali

| URL | Descrizione |
|-----|-----------|
| `/` | Home - Modulo analisi IA |
| `/it/blog/` | Blog e articoli |
| `/it/tool/` | Strumenti gratuiti |
| `/it/knowledge/` | Hub educativo |
| `/it/community/` | Forum comunità |
| `/it/cane/` | Profilo del tuo cane (login richiesto) |
| `/it/newsletter/subscribe/` | Iscrizione newsletter |
| `/unsubscribe/<token>/` | Disiscriviti newsletter |

### Funzionalità Principali

#### 📊 Analisi Comportamentale IA
1. Visita la homepage
2. Descrivi il comportamento del tuo cane
3. Ricevi analisi personalizzata basata su:
   - Razza
   - Età
   - Conoscenza veterinaria
   - Best practice educative

#### 📧 Newsletter
- Iscrizione automatica al `/landing/`
- Email di benvenuto immediata
- Sequenza follow-up:
  - Day 2: Come usare l'IA per il tuo cane
  - Day 5: Monitora la salute del tuo cane

#### 🧪 Strumenti Gratuiti
- Calcolatore cibo
- Convertitore età
- Quiz comunicazione
- Registratore cardiaco

---

## ❤️ Analisi dei Suoni Cardiaci

### Funzionalità Avanzate

Il sistema include strumenti avanzati per analizzare i suoni cardiaci del cane:

#### 🔬 Cardiac Analysis Tool
- **BPM Detection**: Rilevamento automatico del battito cardiaco da file audio
- **S1/S2 Classification**: Identificazione dei battiti (apertura/chiusura valvole)
- **HRV Metrics**: Heart Rate Variability (SDNN, RMSSD, pNN50%)
- **Peak Detection**: Algoritmi adattivi per segnali deboli
- **Noise Filtering**: Filtro bandpass 20-150 Hz + pulizia artefatti

#### 📊 Come Usare

1. **Registra audio cardiaco**:
   ```
   Vai a: Heart → Phonocardiograph Recorder
   Seleziona tipo (🐕 Cane o 👤 Umano)
   Upload file WAV o registra direttamente
   ```

2. **Analisi automatica**:
   ```bash
   python test_cuore_tool.py
   ```

3. **Risultati**:
   - BPM stimato (con correzione cane/umano)
   - Conteggio battiti
   - Confidence (0-1)
   - Tempi picchi S1/S2
   - Metriche HRV (variabilità cardiaca)

#### 🧪 Suite di Test

```bash
# Test TUTTI i file audio
python test_all_audio_files.py

# Test con diversi tipi di soggetto
python test_final_subject_type.py
```

**Funzionalità Testate:**
- ✅ Analisi multi-formato (WAV, WebM, OGG)
- ✅ Rilevamento picchi adattivo (algoritmo MAD)
- ✅ Classificazione S1/S2 intelligente
- ✅ Calcolo BPM differenziale (cane vs umano)
- ✅ Metriche HRV (SDNN, RMSSD, pNN50)
- ✅ Gestione segnali deboli e rumore

---

## 📁 Struttura Progetto

```
vivere-con-il-cane/
├── .github/                    # GitHub Actions, issue templates
├── .kilo/                      # Kilo CLI config (commands, agents)
├── blog/                       # App principale: home, about, blog
│   ├── models.py              # BlogPost, BlogCategory
│   ├── views.py               # Home, articoli, analisi IA
│   └── templates/             # Template HTML
├── canine_tools/              # Strumenti: calcolatori, quiz, cardio
│   ├── models.py              # HeartSoundRecording
│   └── views.py               # Tool views
├── community/                 # Forum e discussioni
├── dog_profile/               # Profili cane e analytics
├── knowledge/                 # Learning hub: articoli, problemi
├── marketing/                 # Newsletter e email automation
├── config/                    # Django settings, URLs, WSGI
├── static/                    # CSS, JS, immagini
│   ├── css/                   # Stylesheet principale
│   ├── js/                    # JavaScript vanilla + HTMX
│   └── images/                # Logo, foto, icone
├── templates/                 # Template base HTML
├── media/                     # File utenti (non in repo)
├── docs/                      # Documentazione e screenshot
├── manage.py                  # Django management
├── requirements.txt           # Dipendenze Python
├── Dockerfile                 # Config Docker
├── .env.example               # Template variabili ambiente
└── README.md                  # Questo file
```

### Applicazioni Principali

| App | Descrizione | Modelli Chiave |
|-----|-----------|----------------|
| **blog** | Home, about, post blog, analisi IA | BlogPost, BlogCategory |
| **canine_tools** | Strumenti interattivi gratuiti | HeartSoundRecording, Tool |
| **community** | Forum discussioni | Discussion, Comment |
| **dog_profile** | Profilo cane e cronologia | DogProfile, DogAnalysis |
| **knowledge** | Contenuto educativo | KnowledgeProblem, Solution |
| **marketing** | Newsletter e automazione email | NewsletterSubscriber, Email |

---

## 🧪 Testing

### Esegui Test Suite

```bash
# Tutti i test
python manage.py test --debug-mode

# Test app specifiche
python manage.py test blog knowledge marketing --debug-mode

# Output verboso
python manage.py test blog -v 2
```

### Coverage Test

- ✅ Models: Validazione, metodi, relazioni
- ✅ Views: Status code, template, contesto
- ✅ Forms: Validazione, elaborazione
- ✅ Utils: Funzioni helper, integrazione IA (mock)

---

## ☁️ Deployment

### 🔥 Render.com (Consigliato)

1. **Fork repository**
2. **Crea Web Service su Render**
3. **Collega repository GitHub**
4. **Build command**:
   ```bash
   pip install -r requirements.txt
   python manage.py migrate
   ```
5. **Start command**:
   ```bash
   gunicorn config.wsgi:application
   ```
6. **Variabili ambiente** nel dashboard Render
7. **Auto-deploy** al push

### 🐳 Docker

```bash
# Build immagine
docker build -t vivere-con-il-cane .

# Esegui container
docker run -p 8000:8000 \
  -e DEBUG=False \
  -e SECRET_KEY=your-secret-key \
  -e ALLOWED_HOSTS=yourdomain.com \
  vivere-con-il-cane
```

### 🖥️ Server Tradizionale

1. Installa Python 3.10+, pip, virtualenv
2. Segui passi installazione sopra
3. Imposta `DEBUG=False` in produzione
4. Configura server WSGI (Gunicorn, uWSGI)
5. Setup reverse proxy (Nginx, Apache)
6. Abilita SSL (Let's Encrypt)

---

## 📡 Endpoint API

### Endpoint Pubblici

| Metodo | URL | Descrizione |
|--------|-----|-----------|
| GET | `/` | Home con form analisi IA |
| GET | `/analizza/` | Submit comportamento per analisi |
| GET | `/it/blog/` | Blog articoli |
| GET | `/it/tool/` | Index strumenti gratuiti |
| GET | `/it/knowledge/` | Index learning hub |
| GET | `/it/community/` | Forum comunità |
| POST | `/it/newsletter/subscribe/` | Iscrizione newsletter (HTMX) |
| GET | `/unsubscribe/<token>/` | Disiscriviti newsletter |

### Endpoint Protetti (Autenticazione Richiesta)

| Metodo | URL | Descrizione |
|--------|-----|-----------|
| GET | `/it/cane/` | Dashboard profilo cane |
| GET | `/it/accounts/profile/` | Profilo utente |
| GET | `/it/accounts/logout/` | Logout |
| GET | `/it/dashboard/` | Dashboard utente |

### Endpoint Admin

| Metodo | URL | Descrizione |
|--------|-----|-----------|
| GET | `/admin/` | Admin panel |
| GET | `/admin/blog/` | Gestione blog post |
| GET | `/admin/marketing/` | Gestione subscriber |
| GET | `/admin/dog_profile/` | Gestione profili cane |

---

## 🤝 Contributing

Contributi sono benvenuti! Segui questi passi:

### 1️⃣ Fork Repository
```bash
# Su GitHub: clicca "Fork"
```

### 2️⃣ Clone e Branch
```bash
git clone https://github.com/YOUR-USERNAME/vivere-con-il-cane.git
cd vivere-con-il-cane
git checkout -b feature/amazing-feature
```

### 3️⃣ Fai Modifiche
- Segui PEP 8 per Python
- Scrivi test per nuove feature
- Aggiorna documentazione se necessario

### 4️⃣ Commit e Push
```bash
git add .
git commit -m "Add amazing feature"
git push origin feature/amazing-feature
```

### 5️⃣ Pull Request
- Apri PR su GitHub
- Descrivi i cambiamenti
- Aspetta review

### Linee Guida Sviluppo

- ✅ Segui PEP 8 per Python
- ✅ Scrivi test per nuove funzionalità
- ✅ Commit atomici e descrittivi
- ✅ Aggiorna documentazione
- ✅ Rispetta lo stile di codice

### Segnala Bug

Usa GitHub Issues per:
- 🐛 Bug reports
- ✨ Feature requests
- 📚 Miglioramenti documentazione

---

## 📄 License

Progetto distribuito sotto **MIT License** - vedi [LICENSE](LICENSE) per dettagli.

---

## 🙏 Acknowledgements

- **Alessio** - Founder e esperto comportamento canino
- **Django Community** - Framework e supporto open-source
- **Groq/Meta** - Llama 3 e infrastruttura AI
- **Contributors** - Sviluppatori e tester
- **Dog Owners Everywhere** - La comunità che rende questo progetto significativo

---

## 📱 Links Utili

- 🌐 **Live Demo**: https://vivere-con-il-cane.onrender.com
- 📖 **Documentazione**: [README.it.md](README.it.md)
- 🐛 **Issues**: [GitHub Issues](https://github.com/ballales1984-wq/vivere-con-il-cane/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/ballales1984-wq/vivere-con-il-cane/discussions)

---

<div align="center">

**Made with ❤️ for dogs and their humans**

*Educazione cinofila moderna con Intelligenza Artificiale*

</div>
