# Database Management for Vivere con il Cane

## Il database è già su GitHub!

Il file `db.sqlite3` è incluso nel repository e viene caricato automaticamente su Render.

## Come aggiornare gli articoli

### 1. Modifica locale (sul tuo PC)
```bash
python manage.py runserver
# Vai su http://127.0.0.1:8000/admin
# Aggiungi/modifica articoli
# Ferma il server
```

### 2. Esporta le modifiche
```bash
python manage.py dumpdata blog > blog/fixtures/blog_data.json
git add blog/fixtures/blog_data.json
git commit -m "Update articles"
git push
```

### 3. Render farà il deploy automaticamente

## Come Scaricare il database dal sito (backup)

Se vuoi scaricare tutto il database dal sito su Render:

```bash
# Scarica db.sqlite3 dal container Render (via SSH se hai piano a pagamento)
# Oppure usa l'admin per esportare
```

## Note

- Il database su GitHub è quello locale/aggiornato
- Per ora è circa 176KB (piccolo)
- Render free tier: il container viene ricreato ad ogni restart, quindi serve il db nel repo