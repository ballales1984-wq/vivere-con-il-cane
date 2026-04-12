# AI Article Generator

## Setup API Key

### Option 1: Grok (xAI) - Recommended
```bash
# On Render: Add environment variable
GROK_API_KEY = gsk_LvPoxJxQgwEhsCDhpIy8WGdyb3FYF6jTXN7bG3jpDxcSXz1

# Locally (Windows):
set GROK_API_KEY=gsk_LvPoxJxQgwEhsCDhpIy8WGdyb3FYF6jTXN7bG3jpDxcSXz1

# Locally (Mac/Linux):
export GROK_API_KEY=gsk_LvPoxJxQgwEhsCDhpIy8WGdyb3FYF6jTXN7bG3jpDxcSXz1
```

### Option 2: OpenAI (fallback)
```bash
set OPENAI_API_KEY=sk-...
```

## Usage

### Generate an article
```bash
python manage.py generate_article "nome del cane" --category "Educazione" --save
```

### Parameters
- `topic`: The article topic (required)
- `--category`: Category name (optional)
- `--save`: Save to database (optional)
- `--importance`: high/medium/low (default: medium)
- `--length`: short/medium/long (default: medium)

### Examples
```bash
# Generate and show (don't save)
python manage.py generate_article "come educare un cane"

# Generate and save
python manage.py generate_article "come educare un cane" --save

# With category
python manage.py generate_article "cane in appartamento" --category "Vita Quotidiana" --save

# High importance, long article
python manage.py generate_article "completa guida alimentazione" --importance high --length long --save
```

## Topics suggestions

### Educazione
- come educare un cane in casa
- comandi base: seduto, vieni,terra
- richiamo affidabile

### Salute
- vaccinazioni cane
- antiparassitari
- sterilizzazione

### Alimentazione
- quante crocchette al giorno
- cibi tossici per cani
- diete fai da te

### Vita Quotidiana
- cane in appartamento
- passeggiate
- routine giornaliera

### Problemi
- cane che abbaia
- ansia da separazione
- tira al guinzaglio