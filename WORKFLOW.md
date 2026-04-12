# Workflow: Locale → Online

## Come funziona

1. **Modifiche in locale** → fai cambiamenti sul tuo PC
2. **Push** → `git add -A && git commit && git push`
3. **Render** → deploy automatico

## Per il database

Il database (`db.sqlite3`) è nel repo. Dopo aver modificato articoli:

```bash
# Esporta articoli dal db locale
python manage.py dumpdata blog > blog/fixtures/blog_data.json

# Commit tutto
git add -A
git commit -m "Update articles"
git push
```

Oppure se hai modificato direttamente il db:

```bash
git add -f db.sqlite3  
git commit -m "Update database"
git push
```

## Di default

- Codice (Python, HTML, CSS): si sincronizza automaticamente
- Database: serve push manuale

##Nota

Se il container Render viene ricreato, il db viene riscritto. Per ora è necessario il push manuale del db.