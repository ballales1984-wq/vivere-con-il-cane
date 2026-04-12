# Vivere con il Cane 🐕

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Language](https://img.shields.io/badge/Python-48.8%25-blue?logo=python)
![HTML](https://img.shields.io/badge/HTML-38.3%25-orange?logo=html5)
![CSS](https://img.shields.io/badge/CSS-11.7%25-blueviolet?logo=css3)

> Un blog dedicato all'educazione cinofila, con articoli, guide pratiche e risorse per proprietari di cani consapevoli.

## 📋 Sommario

- [Descrizione](#descrizione)
- [Funzionalità](#funzionalità)
- [Stack Tecnologico](#stack-tecnologico)
- [Installazione](#installazione)
- [Configurazione](#configurazione)
- [Utilizzo](#utilizzo)
- [Struttura del Progetto](#struttura-del-progetto)
- [Contribuire](#contribuire)
- [Licenza](#licenza)

## 📖 Descrizione

**Vivere con il Cane** è un blog educativo interattivo dedicato all'educazione cinofila. Fornisce articoli approfonditi, guide pratiche, consigli comportamentali e risorse per aiutare proprietari di cani e appassionati a comprendere meglio il proprio animale domestico.

Il progetto combina Python (backend), HTML e CSS (frontend) per offrire un'esperienza web moderna e user-friendly.

## ✨ Funzionalità

- 📝 **Articoli Educativi**: Contenuti curati su comportamento, addestramento e salute del cane
- 🔍 **Sistema di Ricerca**: Trova facilmente articoli per argomento
- 📱 **Design Responsivo**: Perfettamente ottimizzato per desktop, tablet e dispositivi mobili
- 💬 **Sezione Commenti**: Interazione con la comunità
- 🏷️ **Categorie e Tag**: Navigazione intuitiva per argomenti
- 📊 **Dashboard Admin**: Gestione semplice dei contenuti
- 🔐 **Autenticazione**: Protezione dell'area amministrativa

## 🛠️ Stack Tecnologico

| Componente | Tecnologie |
|-----------|-----------|
| **Backend** | Python (48.8%) |
| **Frontend** | HTML (38.3%), CSS (11.7%) |
| **Framework** | Flask/Django |
| **Database** | SQLite / PostgreSQL |
| **Altro** | JavaScript per interattività (1.2%) |

## 📦 Installazione

### Prerequisiti

- Python 3.8+
- pip (gestore pacchetti Python)
- Git

### Passaggi

1. **Clona il repository**
   ```bash
   git clone https://github.com/ballales1984-wq/vivere-con-il-cane.git
   cd vivere-con-il-cane
   ```

2. **Crea un ambiente virtuale**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Su Windows: venv\Scripts\activate
   ```

3. **Installa le dipendenze**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura le variabili d'ambiente**
   ```bash
   cp .env.example .env
   # Modifica .env con le tue configurazioni
   ```

5. **Avvia il server di sviluppo**
   ```bash
   python app.py
   ```

6. **Accedi al blog**
   Apri il browser e vai a `http://localhost:5000`

## ⚙️ Configurazione

### Variabili d'Ambiente (.env)

```env
FLASK_ENV=development
SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite:///blog.db
DEBUG=True
```

### Database

Per inizializzare il database:

```bash
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
```

## 🚀 Utilizzo

### Struttura di Base

- **Homepage**: Visualizza gli articoli più recenti
- **Articoli**: Pagine dedicate con contenuto completo
- **Categorie**: Filtri per argomento
- **Admin Panel**: Gestione contenuti per amministratori

### Creazione di Articoli

1. Accedi all'area amministrativa
2. Clicca su "Nuovo Articolo"
3. Compila il modulo (titolo, contenuto, categoria, tag)
4. Pubblica l'articolo

## 📁 Struttura del Progetto

```
vivere-con-il-cane/
│
├── app.py                 # Entry point dell'applicazione
├── requirements.txt       # Dipendenze Python
├── .env.example          # Template variabili d'ambiente
├── .gitignore            # File da escludere da Git
│
├── static/               # File statici
│   ├── css/              # Fogli di stile CSS
│   │   └── style.css
│   └── js/               # File JavaScript
│       └── main.js
│
├── templates/            # Template HTML
│   ├── base.html
│   ├── index.html
│   ├── article.html
│   └── admin.html
│
├── models/               # Modelli dati (ORM)
│   ├── article.py
│   └── user.py
│
├── routes/               # Route API/Web
│   ├── main.py
│   └── admin.py
│
└── tests/                # Test unitari
    └── test_app.py
```

## 🤝 Contribuire

I contributi sono benvenuti! Per contribuire:

1. **Fork il repository**
   ```bash
   git clone https://github.com/ballales1984-wq/vivere-con-il-cane.git
   ```

2. **Crea un branch per la tua feature**
   ```bash
   git checkout -b feature/descrizione-feature
   ```

3. **Commit i tuoi cambiamenti**
   ```bash
   git commit -m "docs: Aggiungi descrizione chiara dei cambiamenti"
   ```

4. **Push al branch**
   ```bash
   git push origin feature/descrizione-feature
   ```

5. **Apri una Pull Request**
   Descrivi chiaramente i tuoi cambiamenti e il motivo della modifica

### Linee Guida per i Contributi

- Segui lo stile di codice esistente
- Aggiungi commenti per codice complesso
- Testa i tuoi cambiamenti prima di inviare
- Mantieni messaggi di commit chiari e descrittivi

## 📄 Licenza

Questo progetto è distribuito sotto la licenza MIT. Vedi il file [LICENSE](LICENSE) per dettagli.

## 📞 Contatti e Supporto

- **Autore**: ballales1984-wq
- **Repository**: [GitHub - vivere-con-il-cane](https://github.com/ballales1984-wq/vivere-con-il-cane)
- **Issues**: [Report un problema](https://github.com/ballales1984-wq/vivere-con-il-cane/issues)

---

**Ultimo aggiornamento**: 12 Aprile 2026