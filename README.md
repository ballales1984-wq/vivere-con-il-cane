# Vivere con il Cane 🐕 / Living with the Dog 🐕

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Language](https://img.shields.io/badge/Python-48.8%25-blue?logo=python)
![HTML](https://img.shields.io/badge/HTML-38.3%25-orange?logo=html5)
![CSS](https://img.shields.io/badge/CSS-11.7%25-blueviolet?logo=css3)

> IT: Un blog dedicato all'educazione cinofila, con articoli, guide pratiche e risorse per proprietari di cani consapevoli.
> 
> EN: A blog dedicated to dog training, with articles, practical guides and resources for aware dog owners.

## 📋 Sommario / Table of Contents

- [Descrizione / Description](#descrizione--description)
- [Funzionalità / Features](#funzionalità--features)
- [Stack Tecnologico / Tech Stack](#stack-tecnologico--tech-stack)
- [Installazione / Installation](#installazione--installation)
- [Configurazione / Configuration](#configurazione--configuration)
- [Utilizzo / Usage](#utilizzo--usage)
- [Struttura del Progetto / Project Structure](#struttura-del-progetto--project-structure)
- [Contribuire / Contributing](#contribuire--contributing)
- [Licenza / License](#licenza--license)

---

## 📖 Descrizione / Description

**Vivere con il Cane** (EN: **Living with the Dog**) è un blog educativo interattivo dedicato all'educazione cinofila. Fornisce articoli approfonditi, guide pratiche, consigli comportamentali e risorse per aiutare proprietari di cani e appassionati a comprendere meglio il proprio animale domestico.

EN: **Living with the Dog** is an interactive educational blog dedicated to dog training. It provides in-depth articles, practical guides, behavioral advice and resources to help dog owners and enthusiasts better understand their pets.

Il progetto combina Python (backend), HTML e CSS (frontend) per offrire un'esperienza web moderna e user-friendly.

EN: The project combines Python (backend), HTML and CSS (frontend) to offer a modern and user-friendly web experience.

---

## ✨ Funzionalità / Features

| IT | EN |
|---|---|
| 📝 **Articoli Educativi**: Contenuti curati su comportamento, addestramento e salute del cane | 📝 **Educational Articles**: Curated content on dog behavior, training and health |
| 🔍 **Sistema di Ricerca**: Trova facilmente articoli per argomento | 🔍 **Search System**: Easily find articles by topic |
| 📱 **Design Responsivo**: Perfettamente ottimizzato per desktop, tablet e dispositivi mobili | 📱 **Responsive Design**: Perfectly optimized for desktop, tablet and mobile |
| 💬 **Sezione Commenti**: Interazione con la comunità | 💬 **Comments Section**: Community interaction |
| 🏷️ **Categorie e Tag**: Navigazione intuitiva per argomenti | 🏷️ **Categories and Tags**: Intuitive navigation by topics |
| 📊 **Dashboard Admin**: Gestione semplice dei contenuti | 📊 **Admin Dashboard**: Easy content management |
| 🔐 **Autenticazione**: Protezione dell'area amministrativa | 🔐 **Authentication**: Admin area protection |

---

## 🛠️ Stack Tecnologico / Tech Stack

| Componente / Component | Tecnologie / Technologies |
|-----------------------|---------------------------|
| **Backend** | Python (48.8%) |
| **Frontend** | HTML (38.3%), CSS (11.7%) |
| **Framework** | Django |
| **Database** | SQLite / PostgreSQL |
| **Altro / Other** | JavaScript per interattività / for interactivity (1.2%) |

---

## 📦 Installazione / Installation

### Prerequisiti / Prerequisites

- Python 3.8+ / Python 3.8+
- pip (gestore pacchetti Python / Python package manager)
- Git

### Passaggi / Steps

1. **Clona il repository / Clone the repository**
   ```bash
   git clone https://github.com/ballales1984-wq/vivere-con-il-cane.git
   cd vivere-con-il-cane
   ```

2. **Crea un ambiente virtuale / Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Su Windows / On Windows: venv\Scripts\activate
   ```

3. **Installa le dipendenze / Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura le variabili d'ambiente / Configure environment variables**
   ```bash
   cp .env.example .env
   # Modifica .env con le tue configurazioni / Edit .env with your settings
   ```

5. **Avvia il server di sviluppo / Start the development server**
   ```bash
   python manage.py runserver
   ```

6. **Accedi al blog / Access the blog**
   Apri il browser e vai a / Open your browser and go to: `http://localhost:8000`

---

## ⚙️ Configurazione / Configuration

### Variabili d'Ambiente (.env) / Environment Variables (.env)

```env
DEBUG=True
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

### Database

Per inizializzare il database / To initialize the database:

```bash
python manage.py migrate
python manage.py createsuperuser
```

---

## 🚀 Utilizzo / Usage

### Struttura di Base / Basic Structure

| IT | EN |
|---|---|
| **Homepage**: Visualizza gli articoli più recenti | **Homepage**: Displays recent articles |
| **Articoli**: Pagine dedicate con contenuto completo | **Articles**: Dedicated pages with full content |
| **Categorie**: Filtri per argomento | **Categories**: Filters by topic |
| **Admin Panel**: Gestione contenuti per amministratori | **Admin Panel**: Content management for administrators |

### Creazione di Articoli / Creating Articles

1. Accedi all'area amministrativa / Access the admin area: `/admin`
2. Clicca su "Nuovo Articolo" / Click "New Article"
3. Compila il modulo (titolo, contenuto, categoria, tag) / Fill in the form (title, content, category, tags)
4. Pubblica l'articolo / Publish the article

---

## 📁 Struttura del Progetto / Project Structure

```
vivere-con-il-cane/
│
├── manage.py                 # Django management / Django management
├── requirements.txt         # Python dependencies / Python dependencies
├── .env.example             # Environment template / Environment template
├── .gitignore               # Git ignore / Git ignore
│
├── config/                  # Django settings / Django settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── blog/                    # Main blog app / Main blog app
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── static/                  # Static files / Static files
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
│
├── templates/               # HTML templates / HTML templates
│   ├── base.html
│   ├── index.html
│   ├── article.html
│   └── admin.html
│
└── tests/                  # Unit tests / Unit tests
    └── test_app.py
```

---

## 🤝 Contribuire / Contributing

I contributi sono benvenuti! Per contribuire / Contributions are welcome! To contribute:

1. **Fork il repository / Fork the repository**
   ```bash
   git clone https://github.com/ballales1984-wq/vivere-con-il-cane.git
   ```

2. **Crea un branch per la tua feature / Create a branch for your feature**
   ```bash
   git checkout -b feature/descrizione-feature
   ```

3. **Commit i tuoi cambiamenti / Commit your changes**
   ```bash
   git commit -m "docs: Aggiungi descrizione chiara dei cambiamenti"
   ```

4. **Push al branch / Push to branch**
   ```bash
   git push origin feature/descrizione-feature
   ```

5. **Apri una Pull Request / Open a Pull Request**
   Descrivi chiaramente i tuoi cambiamenti e il motivo della modifica / Clearly describe your changes and the reason for the modification

### Linee Guida per i Contributi / Contribution Guidelines

- Segui lo stile di codice esistente / Follow existing code style
- Aggiungi commenti per codice complesso / Add comments for complex code
- Testa i tuoi cambiamenti prima di inviare / Test your changes before submitting
- Mantieni messaggi di commit chiari e descrittivi / Keep commit messages clear and descriptive

---

## 📄 Licenza / License

Questo progetto è distribuito sotto la licenza MIT. Vedi il file [LICENSE](LICENSE) per dettagli.

EN: This project is distributed under the MIT license. See the [LICENSE](LICENSE) file for details.

---

## 📞 Contatti e Supporto / Contacts and Support

| | |
|---|---|
| **Autore / Author** | ballales1984-wq |
| **Repository** | [GitHub - vivere-con-il-cane](https://github.com/ballales1984-wq/vivere-con-il-cane) |
| **Issues** | [Report a problem / Report a problem](https://github.com/ballales1984-wq/vivere-con-il-cane/issues) |

---

**Ultimo aggiornamento / Last update**: 16 Aprile 2026 / April 16, 2026