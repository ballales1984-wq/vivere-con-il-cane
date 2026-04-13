# Piano di Sviluppo Unificato - Vivere con il Cane

> Ultimo aggiornamento: 13 Aprile 2026

## Obiettivo

Trasformare il sito da blog informativo a **sistema AI che risolve problemi del cane**,
poi espandere in portale.

Regola: ogni feature deve rispondere a "porta utenti o migliora l'uso?" - se no, non farla ora.

---

## Stack Reale (NON cambiare)

| Componente | Tecnologia | Note |
|------------|-----------|------|
| Backend | **Django 5.x** | Gia funzionante |
| Frontend | **Django Templates + CSS** | Nessun React/Vue necessario |
| Database | **SQLite** (locale) / **PostgreSQL** (Render) | Gia configurato |
| AI | **Grok API** -> fallback **OpenAI** -> fallback generico | Gia funzionante |
| Deploy | **Render** (auto-deploy da GitHub) | Gia attivo |

**IMPORTANTE**: I piani precedenti suggerivano Flask, React, PostgreSQL separato.
Tutto questo e gia coperto dal tuo stack Django. Non serve riscrivere nulla.

---

## Stato Attuale (Cosa Esiste Gia)

### Funzionante
| Componente | App Django | Stato |
|------------|-----------|-------|
| 8 articoli blog | `blog` | Pubblicati con voti, categorie |
| AI Analisi problemi | `knowledge` | Grok/OpenAI con contesto cane |
| Profilo cane | `dog_profile` | CRUD + eventi salute + log giornalieri |
| 3 problemi nel DB | `knowledge` | Abbaia, tira guinzaglio, ansia separazione |
| 3 razze nel DB | `knowledge` | Labrador, Golden, Pastore Tedesco |
| Calcolatore cibo | `canine_tools` | Formula kcal per peso/eta/attivita |
| Calcolatore eta | `canine_tools` | Conversione per taglia |
| Quiz linguaggio | `canine_tools` | 3 domande con punteggio |
| Votazione articoli | `blog` (PostVote) | AJAX, 1 voto per IP |
| AI article generator | `blog` (command) | `manage.py generate_article` |
| Google Analytics | `base.html` | Attivo |
| Google AdSense | `base.html` | Attivo |

### Mancante
| Cosa | Dove | Priorita |
|------|------|----------|
| Problemi nel DB (solo 3, servono 10+) | `knowledge` fixture | ALTA |
| Razze nel DB (solo 3, servono 10+) | `knowledge` fixture | MEDIA |
| Articoli SEO mirati (3 nuovi scritti, non nel DB) | `blog` fixture | ALTA |
| CTA "Analizza il tuo caso" negli articoli | `templates/blog/detail.html` | ALTA |
| Homepage con input AI centrale | `templates/home.html` | ALTA |
| Link interni tra articoli | `templates/blog/detail.html` | MEDIA |
| Meta SEO (title/description) | `blog/models.py` + template | MEDIA |
| Sitemap.xml | nuovo | MEDIA |
| robots.txt | nuovo | BASSA |

---

# ROADMAP

## FASE 1 - Core Prodotto (Settimana 1-2)

**Obiettivo**: Il sistema AI risolve davvero i problemi

### 1.1 Espandere Knowledge Base (10 problemi)

Aggiungere a `knowledge/fixtures/knowledge_data.json`:

| # | Problema | Slug | Categoria | Cause | Soluzioni | Nel DB? |
|---|----------|------|-----------|-------|-----------|---------|
| 1 | Abbaia troppo | abbaia-troppo | behavior | 2 | 2 | SI |
| 2 | Tira al guinzaglio | tira-al-guinzaglio | behavior | - | - | SI |
| 3 | Ansia da separazione | ansia-da-separazione | behavior | - | - | SI |
| 4 | Morde mani/oggetti | morde | behavior | 3+ | 3+ | NO |
| 5 | Non mangia | non-mangia | health | 3+ | 3+ | NO |
| 6 | Paura rumori/temporali | paura-rumori | behavior | 3+ | 3+ | NO |
| 7 | Salta addosso alle persone | salta-addosso | behavior | 2+ | 2+ | NO |
| 8 | Non risponde al richiamo | non-richiamo | training | 2+ | 2+ | NO |
| 9 | Distrugge oggetti/casa | distrugge-casa | behavior | 3+ | 3+ | NO |
| 10 | Eccitazione eccessiva | eccitazione-eccessiva | behavior | 2+ | 2+ | NO |

**File da modificare**: `knowledge/fixtures/knowledge_data.json`
**Azione**: Aggiungere 7 Problem + relative Cause + Solution

### 1.2 Completare cause/soluzioni per problemi esistenti

I problemi 2 e 3 (tira, ansia) nel DB non hanno cause e soluzioni collegate.
Aggiungere dati completi.

### 1.3 Aggiungere 3 nuovi articoli al blog

Contenuti gia scritti (dal piano precedente):

| Titolo | Slug | Categoria | pk |
|--------|------|-----------|----|
| Cane abbaia sempre: cause e soluzioni efficaci | cane-abbaia-sempre | 3 (Problemi) | 9 |
| Cane tira al guinzaglio: come risolvere definitivamente | cane-tira-al-guinzaglio-come-risolvere | 3 (Problemi) | 10 |
| Cane morde: perche succede e come fermarlo subito | cane-morde-perche-succede | 3 (Problemi) | 11 |

**File da modificare**: `blog/fixtures/blog_data.json`

### 1.4 CTA in ogni articolo blog

In `templates/blog/detail.html` aggiungere in fondo a ogni articolo:

```html
<div class="cta-analyze">
    <h3>Ogni cane e diverso</h3>
    <p>Descrivi il problema del tuo cane e ottieni una soluzione personalizzata.</p>
    <a href="{% url 'analyze_problem' %}" class="btn">Analizza il tuo caso</a>
</div>
```

---

## FASE 2 - Homepage come Prodotto (Settimana 2-3)

**Obiettivo**: L'utente capisce subito cosa puo fare

### 2.1 Ridisegnare Homepage

Struttura `templates/home.html`:

1. **Hero**: Titolo + input testo problema + bottone "Analizza con AI"
   - Il form punta a `/knowledge/analizza/` con pre-fill del campo descrizione
2. **Problemi rapidi**: 3-4 card cliccabili (abbaia, morde, tira, ansia)
   - Link a `/knowledge/problemi/<slug>/`
3. **Come funziona**: 3 step (scrivi problema -> AI analizza -> ricevi soluzione)
4. **Articoli recenti**: Ultimi 3 post con bottone "Analizza il tuo caso"
5. **Tool**: Link a calcolatori

### 2.2 Collegare Blog <-> Knowledge

In `templates/blog/detail.html`:
- CTA verso AI (gia in 1.4)
- Link interni verso articoli correlati (stesso problema)

In `templates/knowledge/problem_detail.html`:
- Link all'articolo blog correlato (se esiste)

---

## FASE 3 - SEO (Settimana 3-4)

**Obiettivo**: Google porta traffico

### 3.1 Meta SEO per articoli

Aggiungere campo `meta_description` a `BlogPost`:
```python
meta_description = models.CharField(max_length=160, blank=True)
```

In `templates/base.html`:
```html
<meta name="description" content="{% block meta_description %}Vivere con il Cane - Educazione cinofila{% endblock %}">
```

### 3.2 Schema.org Article

In `templates/blog/detail.html` aggiungere JSON-LD:
```html
<script type="application/ld+json">
{
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "{{ post.title }}",
    "datePublished": "{{ post.publish_date|date:'c' }}",
    "author": {"@type": "Organization", "name": "Vivere con il Cane"}
}
</script>
```

### 3.3 Sitemap + robots.txt

- Aggiungere `django.contrib.sitemaps` a INSTALLED_APPS
- Creare `blog/sitemaps.py` con BlogPostSitemap, ProblemSitemap, BreedSitemap
- robots.txt statico in `static/`

### 3.4 Link interni (cluster SEO)

Ogni articolo su un problema deve linkare a:
- Gli altri articoli dello stesso cluster (problemi comportamentali)
- La pagina AI analisi
- La pagina del problema in knowledge

---

## FASE 4 - Espandere Razze (Settimana 5-6)

**Obiettivo**: Piu porte d'ingresso SEO

### 4.1 Aggiungere razze al DB

Da 3 a 10+ razze in `knowledge/fixtures/knowledge_data.json`:

| Razza | Energia | Problemi comuni |
|-------|---------|----------------|
| Labrador | alta | iperattivita (GIA) |
| Golden Retriever | alta | (GIA) |
| Pastore Tedesco | alta | (GIA) |
| Chihuahua | media | ansia, abbaio |
| Bulldog Francese | bassa | respirazione, cibo |
| Border Collie | molto alta | distruzione, noia |
| Beagle | alta | abbaio, fuga |
| Jack Russell | molto alta | eccitazione, scavo |
| Rottweiler | alta | tira guinzaglio, territorialita |
| Cocker Spaniel | media | ansia, cibo |

### 4.2 Collegamento Razza -> Problemi -> AI

In `templates/knowledge/breed_detail.html`:
- Mostrare problemi comuni della razza
- CTA: "Il tuo [razza] ha un problema? Analizzalo"

---

## FASE 5 - Retention (Settimana 7-8)

**Obiettivo**: L'utente torna

### 5.1 Storico Analisi

Il modello `DogAnalysis` esiste gia e salva le analisi.
Aggiungere una view che mostra le analisi precedenti per un profilo cane:

```python
# knowledge/views.py
def analysis_history(request, dog_id):
    analyses = DogAnalysis.objects.filter(dog_id=dog_id).order_by('-created_at')
    return render(request, 'knowledge/analysis_history.html', {'analyses': analyses})
```

### 5.2 Risposte personalizzate

L'AI gia riceve i dati del cane nel prompt. Migliorare il contesto:
- Includere storico analisi precedenti nel prompt
- "Questo cane ha gia avuto problemi di: [lista]"

---

## FASE 6 - Monetizzazione (Dopo traffico)

Solo quando superi 1000 visitatori/mese.

### 6.1 AdSense
- Gia configurato in `base.html` (ca-pub-2145959534306055)
- Aggiungere unit ads dentro articoli e pagine tool

### 6.2 Affiliazioni
- Link affiliate in articoli su alimentazione/accessori
- Sezione "Prodotti consigliati" nelle pagine problema

---

## FASE 7 - Ecosistema (Futuro)

SOLO dopo che fasi 1-6 funzionano.

- Autenticazione utente (login/sessioni per profili cane privati)
- Servizi (educatori cinofili, veterinari)
- Eventi
- Newsletter

---

## Riepilogo Priorita

| Cosa | Priorita | Sforzo | Impatto |
|------|----------|--------|---------|
| +7 problemi nel knowledge DB | CRITICA | Basso (fixture) | Alto |
| +3 articoli SEO nel blog DB | CRITICA | Basso (fixture) | Alto |
| CTA "Analizza" in articoli blog | CRITICA | Basso (1 template) | Alto |
| Homepage con input AI | ALTA | Medio (1 template) | Alto |
| Collegamento blog <-> knowledge | ALTA | Basso (template) | Alto |
| Meta SEO + schema.org | MEDIA | Basso | Medio |
| Sitemap + robots.txt | MEDIA | Basso | Medio |
| +7 razze nel knowledge DB | MEDIA | Basso (fixture) | Medio |
| Storico analisi | BASSA | Basso (view) | Medio |
| Autenticazione utente | BASSA | Alto | Basso (ora) |
| Affiliazioni | BASSA | Basso | Basso (ora) |

---

## File Principali da Modificare

| File | Azione |
|------|--------|
| `knowledge/fixtures/knowledge_data.json` | +7 problemi con cause/soluzioni, +7 razze |
| `blog/fixtures/blog_data.json` | +3 articoli SEO |
| `templates/home.html` | Redesign con input AI centrale |
| `templates/blog/detail.html` | CTA analisi + link interni + schema.org |
| `templates/knowledge/problem_detail.html` | Link a articolo blog correlato |
| `templates/knowledge/breed_detail.html` | CTA analisi per razza |
| `templates/base.html` | Meta description block |
| `blog/models.py` | Campo meta_description |
| `blog/sitemaps.py` | Nuovo: sitemap per blog + knowledge |
| `config/urls.py` | Aggiungere sitemap URL |
| `knowledge/views.py` | View storico analisi |

---

## Cosa NON Fare Ora

- NON riscrivere in Flask o React (Django funziona gia)
- NON aggiungere PostgreSQL locale (SQLite va bene per sviluppo)
- NON creare un "DogEngine" separato (knowledge app fa gia questo)
- NON aggiungere autenticazione (ancora non serve)
- NON aggiungere shop/eventi/servizi (troppo presto)
- NON fare 100 articoli generici (meglio 10 mirati con CTA)
