# 🐕 Vivere con il Cane - Piattaforma HealthTech AI

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)
![AI](https://img.shields.io/badge/AI-Groq%20Llama%203-orange?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)

*🌍 [Read the English documentation](README.md)*

**Vivere con il Cane** non è un semplice blog: è una piattaforma **HealthTech** moderna basata sull'Intelligenza Artificiale. Funziona come un **Assistente Veterinario Virtuale H24**, capace di incrociare lo storico medico e comportamentale del cane per fornire raccomandazioni diagnostiche altamente personalizzate e legate al contesto.

---

## 🌟 Unique Value Proposition (Il Nostro Vantaggio Competitivo)

### 🧠 1. Motore IA a Memoria Longitudinale (Dynamic Routing)
A differenza dei normali "wrapper" di ChatGPT, il nostro motore IA (alimentato da Llama-3 via Groq) usa il routing contestuale.
- Gestisce un **Profilo Medico Persistente** per ogni cane (età, peso, genetica).
- Prima di interrogare l'LLM, il backend Django genera algoritmicamente un "Super-Prompt" che inietta l'intera storia clinica passata dell'animale.
- *Risultato:* Se l'utente scrive "zoppica", l'IA sa automaticamente che sta analizzando un *meticcio di 10 anni in sovrappeso con storico di artrite*, fornendo risposte 10 volte più accurate e sicure.

### 📋 2. Cartella Clinica Medica Unificata (Pronta per il Veterinario)
- Il sistema unisce le tradizionali "viste mediche" (vaccini, infortuni) con lo **storico delle analisi comportamentali dell'IA** in un'unica Timeline Cronologica.
- Pensata per l'uso nel mondo reale: la cartella clinica offre l'esportazione testo istantanea in stile **WhatsApp** o la generazione di un **PDF pulito senza elementi grafici inutili**, perfetto da allegare in un'email al medico curante.

### 📚 3. Matrice Relazionale (Sintomi-Cause-Soluzioni)
Il cuore del sistema non è un banale blog di testo. La nostra *Knowledge Base* è una matrice strutturata nel database:
- **Sintomi**, **Cause Scatenanti** e **Rimedi Pratici** sono entità distinte connesse tra loro nel backend.
- L'IA non "indovina": utilizza questa matrice incrociandola con il profilo della razza (livelli di energia, predisposizioni) per mappare in tempo reale il problema alla causa più statisticamente probabile.

### 📈 4. Piattaforma HealthTech Orientata alla Conversione
- Più di una semplice App Web, l'interfaccia si presenta come un Hub Premium con **Design in Glassmorphism** e gradienti accattivanti.
- Completa adozione delle direttive SEO con **Schema.org JSON-LD** iniettato dinamicamente per trasformare i lettori casuali dei motori di ricerca in utenti abituali della piattaforma diagnostica.


## 🏗️ Architettura del Sistema

```mermaid
graph TD
    User([Utente]) -->|Interagisce| UI[Frontend UI/Templates]
    UI -->|Salva Profilo & Interroga IA| Core(Backend Django)
    
    subgraph Data Layer
        Core --> DB[(SQLite / PostgreSQL)]
        DB -->|Anagrafica| Profiles[Profili Cani]
        DB -->|Editoriale| Blog[Blog SEO]
        DB -->|Diagnostici| KB[Knowledge Base]
    end
    
    Core <-->|Prompting Avanzato Longitudinale| AI[API Groq / Llama 3 70b]
    AI -->|Analisi Diagnostica| UI
```

## 🛠️ Stack Tecnologico

- **Applicativo Backend**: Python 3.10+, Framework Django 5+
- **Frontend Layer**: Template Django HTML5, Variabili CSS pure, Design Responsivo (Mobile First)
- **Logica Intelligenza Artificiale**: Costruzione di prompt agentici tramite API REST Groq e modelli Open-Source allo stato dell'arte.
- **Database**: SQLite (Ambiente di Sviluppo) / PostgreSQL (Ambiente di Produzione)
- **Deployment & Scaling**: Render PaaS, WhiteNoise per l'ottimizzazione e compressione dei file statici.

---

## 🏥 Funzionalità di Analisi Cardiaca (Heart Sound Analysis)

La piattaforma include strumenti avanzati per l'analisi dei suoni cardiaci dei cani:

### 🔬 Cardiac Analysis Tool
- **Rilevamento BPM**: Frequenza cardiaca automatica da file audio (WAV, WebM, OGG)
- **S1/S2 Classification**: Identifica i battiti cardiaci (chiusura/apertura valvole)
- **HRV Metrics**: Heart Rate Variability (SDNN, RMSSD, pNN50%)
- **Peak Detection**: Algoritmi adattivi per segnali deboli
- **Noise Filtering**: Filtro passabanda 20-150 Hz e pulizia artefatti

### 📊 Utilizzo

1. **Registra un audio cardiaco**:
   - Vai su `Cuore → Registratore Fonocardiografico`
   - Seleziona il **tipo di soggetto** (Cane 🐕 o Umano 👤)
   - Carica un file WAV o registra direttamente
   
2. **Analisi automatica**:
   ```bash
   # Test locale con file WAV
   python test_cuore_tool.py
   ```

3. **Risultati**:
   - BPM stimato (con correzione per cani o umani)
   - Conteggio battiti
   - Confidenza (0-1)
   - Tempi picchi S1/S2 (separazione valvole)
   - Metriche HRV (variabilità cardiaca)

### 🧪 Test Suite

```bash
# Testa TUTTI i file audio disponibili
python test_all_audio_files.py

# Test con diversi tipi di soggetto
python test_final_subject_type.py
```

Funzionalità testate:
- ✅ Analisi audio multi-formato (WAV, WebM)
- ✅ Rilevamento picchi adattivo (algoritmo MAD)
- ✅ Classificazione S1/S2 con accoppiamento intelligente
- ✅ Calcolo BPM differenziato (cane vs umano)
- ✅ Metriche HRV (SDNN, RMSSD, pNN50)
- ✅ Gestione segnali deboli e rumore

---

## 🚀 Guida all'Avvio Rapido (Quick Start)

### Prerequisiti
- Python 3.8+
- Git

### Istruzioni di Installazione

1. **Clona il repository sul tuo ambiente locale**
   ```bash
   git clone https://github.com/ballales1984-wq/vivere-con-il-cane.git
   cd vivere-con-il-cane
   ```

2. **Crea e attiva un Ambiente Virtuale Sicuro**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Su Windows: venv\Scripts\activate
   ```

3. **Installa tutte le Dipendenze**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurazione delle Variabili d'Ambiente**
   Crea un file `.env` nella directory principale per simulare la configurazione di produzione:
   ```env
   DEBUG=True
   SECRET_KEY=inserisci_una_chiave_segreta_sicura
   GROK_API_KEY=la_tua_chiave_api_groq_qui
   ```

5. **Migrazione Database e Inizializzazione Dati (Fixtures)**
   ```bash
   python manage.py migrate
   
   # Questo popolerà il database con contenuti IA, relazioni mediche e blog post SEO:
   python manage.py loaddata blog/fixtures/blog_data.json
   python manage.py loaddata knowledge/fixtures/knowledge_data.json
   ```

6. **Esegui il Server di Sviluppo**
   ```bash
   python manage.py runserver
   ```
   Ora puoi accedere alla piattaforma navigando a `http://127.0.0.1:8000`.

---

## 💡 Il "Segreto" del Motore IA

La vera innovazione di *Vivere con il Cane* risiede nel **Routing del Prompt**. Quando un utente fa una domanda generica (es. "Perché zoppica?"), il backend non inoltra la frase così com'è. Invece, assembla un **Super-Prompt dinamico arricchito di contesto**:
1. Estrae in background i dati biometrici del cane attivo (es. "Cane anziano di 10 anni, 25kg").
2. Recupera e processa lo storico medico pregresso del cane (es. "Nei log precedenti figurano problemi di incontinenza e dolori al bacino").
3. Impacchetta dinamicamente queste informazioni (System Prompt + User Context + User Message) e le instrada all'LLM.
*Risultato finale*: Un chatbot che non si comporta come Wikipedia, ma che simula il **flusso cognitivo reale di un medico veterinario**, individuando nessi di causalità e allarmi correlati all'età, senza che l'utente debba reinserire la propria storia ogni volta.

---

## 🤝 Contribuire
I contributi sono vitali per questo progetto, che mira a democratizzare l'informazione di altissimo livello per la salute e il benessere cinofilo. 
1. Esegui il Fork del Progetto
2. Crea un Branch per la tua modifica (`git checkout -b feature/SviluppoStrabiliante`)
3. Fai un Commit logico (`git commit -m 'Aggiunta funzionalità SviluppoStrabiliante'`)
4. Fai il Push del Branch (`git push origin feature/SviluppoStrabiliante`)
5. Apri una Pull Request documentata.

## 📄 Licenza
Il progetto è distribuito sotto Licenza Open Source MIT. Fai riferimento al file `LICENSE` per i dettagli legali completi.
