# Guida Completa: Configurazione Google OAuth per "Vivere con il Cane"

Questa guida dettagliata spiega come configurare **due tipi di autenticazione Google OAuth** nel progetto Django "Vivere con il Cane":

1. **Google Social Login** (django-allauth) - per accesso rapido dell'utente
2. **Google Health/Fit OAuth** - per sincronizzare dati salute (passi, frequenza cardiaca) dai dispositivi Google

---

## 📋 Prerequisiti

- Un account Google (Gmail)
- Accesso a [Google Cloud Console](https://console.cloud.google.com/)
- Progetto Django configurato e funzionante in locale

---

## 🏗️ Parte 1: Creazione Progetto Google Cloud

### Passo 1.1: Crea un nuovo progetto

1. Vai su [Google Cloud Console](https://console.cloud.google.com/)
2. Clicca **SELEZIONA UN PROGETTO** → **NUOVO PROGETTO**
3. Compila i campi:
   - **Nome progetto**: `Vivere con il Cane` (o un nome a tua scelta)
   - **Localizzazione**: lascia default o seleziona un'organizzazione se applicabile
4. Clicca **CREA**

> **Nota**: Il nome del progetto è solo per riferimento interno. Non influisce sulle credenziali OAuth.

### Passo 1.2: Abilita le API necessarie

Il progetto richiede **due API diverse** a seconda del flusso:

#### Per Google Social Login (allauth):
Non è necessario abilitare API specifiche oltre l'OAuth stesso.

#### Per Google Health/Fit Data Sync:
Abilita **Google Fit API** (consigliata) o **Health Connect API** (sperimentale):

1. Nel menu sinistro, vai su **APIs & Services** → **Library**
2. Cerca **"Google Fit API"**
3. Seleziona **Google Fit API**
4. Clicca **ENABLE**
5. (Opzionale) Cerca anche **"Health Connect API"** e abilitala se vuoi usare l'API più recente

---

## 🔐 Parte 2: Configurazione OAuth 2.0 Credentials

### Passo 2.1: Abilita OAuth Consent Screen

Prima di creare le credenziali, configura lo schermo di consenso OAuth:

1. Nel menu sinistro, vai su **APIs & Services** → **OAuth consent screen**
2. Scegli **External** (per app pubbliche) → **CREATE**
3. Compila il form:

   **App Information:**
   - **App name**: `Vivere con il Cane`
   - **User support email**: la tua email
   - **Developer contact information**: la tua email

   **Scopes** (per Google Fit):
   - Clicca **ADD OR REMOVE SCOPES**
   - Seleziona:
     - `.../auth/fitness.activity.read` (per passi e attività)
     - `.../auth/fitness.body.read` (per dati corporei)
     - `.../auth/fitness.heart_rate.read` (per frequenza cardiaca)
     - `.../auth/fitness.location.read` (per dati di percorso, se necessario)
   - Clicca **UPDATE**

   **Test Users** (in sviluppo):
   - Clicca **ADD USERS**
   - Aggiungi il tuo indirizzo Gmail
   - Questo permette di testare l'OAuth anche se l'app non è verificata da Google

4. Clicca **SAVE AND CONTINUE** fino al completamento
5. Nella schermata finale, clicca **PUBLISH APP** (in sviluppo va bene anche "Testing")

> **Importante**: Se non pubblichi l'app, solo gli utenti test possono usarla. Per produzione, dovrai sottoporre l'app a verifica Google.

### Passo 2.2: Crea OAuth 2.0 Client ID

1. Nel menu sinistro, vai su **APIs & Services** → **Credentials**
2. Clicca **+ CREATE CREDENTIALS** → **OAuth client ID**
3. Seleziona **Web application** come tipo
4. Nel campo **Name**, inserisci: `Vivere con il Cane - Web Client`
5. **Authorized redirect URIs**: vedi prossima sezione dettagliata
6. Clicca **CREATE**

**Risultato:**
Verranno mostrati due valori **DA NON CONDIVIDERE**:
- **Client ID**: (es. `123456789-abc...apps.googleusercontent.com`)
- **Client Secret**: (una stringa lunga, es. `GOCSPX-...`)

**Salvali in un luogo sicuro temporaneamente** (passeremo al .env dopo).

---

## 🔀 Parte 3: Redirect URI Autorizzati

### IMPORTANTE: Due Flussi OAuth, Due Set di Redirect URI

Questo progetto usa **DUE configurazioni OAuth separate** che richiedono URI diversi:

#### Flusso A: Google Social Login (django-allauth)

Used for: Login/signup standard con Google

| Ambiente | Redirect URI |
|----------|-------------|
| Sviluppo locale | `http://localhost:8000/accounts/google/login/callback/` |
| Produzione (Render) | `https://vivere-con-il-cane.onrender.com/accounts/google/login/callback/` |
| Staging (ngrok) | `https://[tuo-tunnel].ngrok-free.dev/accounts/google/login/callback/` |

#### Flusso B: Google Health/Fit OAuth (Custom)

Used for: Sincronizzazione dati salute da Google Fit/Health Connect (viste in `canine_tools/views.py:438-524`)

| Ambiente | Redirect URI |
|----------|-------------|
| Sviluppo locale | `http://localhost:8000/auth/google/callback` |
| Produzione (Render) | `https://vivere-con-il-cane.onrender.com/auth/google/callback` |
| Staging (ngrok) | `https://[tuo-tunnel].ngrok-free.dev/auth/google/callback` |

### Passo 3.1: Aggiungi tutti i Redirect URI in Google Cloud Console

Nella schermata **Create OAuth client ID**, nella sezione **Authorized redirect URIs**, aggiungi **TUTTE E QUATTRO** le righe seguenti (per avere una configurazione completa per dev e produzione):

```
http://localhost:8000/accounts/google/login/callback/
https://vivere-con-il-cane.onrender.com/accounts/google/login/callback/
http://localhost:8000/auth/google/callback
https://vivere-con-il-cane.onrender.com/auth/google/callback
```

> **Note:**
> - Ogni URI va su una riga separata
> - Gli URI di sviluppo (localhost) sono **necessari** per testare in locale
> - Gli URI di produzione sono **obbligatori** per il deploy su Render
> - Se usi ngrok per tunneling, aggiungi anche quelli (es. `https://abc123.ngrok-free.dev/accounts/google/login/callback/`)

### Passo 3.2: Verifica della configurazione

Dopo aver creato il client, verifica in **Credentials**:
- Il client appare nella lista
- Cliccando sul nome, puoi vedere e modificare i redirect URI
- Puoi aggiungere URI aggiuntivi in futuro senza creare un nuovo client

---

## ⚙️ Parte 4: Variabili d'Ambiente (.env)

### Passo 4.1: Modifica il file `.env` (sviluppo locale)

Il progetto ha già un file `.env` nella root. Modificalo aggiungendo le variabili per Google OAuth:

```bash
# File: .env (nella root del progetto)
# ======================================

# --- RIMUOVI o COMMENTA eventuali valori vecchi/errati ---
# Se esistono chiavi con nomi diversi, assicurati di usare i nomi corretti sotto

# Google OAuth per Social Login + Health/Fit Sync
GOOGLE_OAUTH_CLIENT_ID=Il-tuo-client-id-apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=Il-tuo-client-secret-lungo

# (Opzionale) Redirect URI esplicito - se omesso, usa default in settings.py:
# Sviluppo: http://localhost:8000/auth/google/callback
# Produzione:肩上没写，请参考 settings.py 的默认值或自行配置
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8000/auth/google/callback
```

**Esempio completo del file `.env` dopo la modifica:**

```env
# Environment variables for Vivere con il Cane
# =============================================

# Grok API Key (da xAI)
GROK_API_KEY=<rimuovi-prima-del-push>

# OpenAI (opzionale, fallback)
OPENAI_API_KEY=

# Google OAuth 2.0 Credentials
# Client ID e Secret da Google Cloud Console → APIs & Services → Credentials
GOOGLE_OAUTH_CLIENT_ID=123456789-abc123def456.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=GOCSPX-AbCdEfGhIjKlMnOpQrStUvWxYz123456789
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8000/auth/google/callback

# Email Settings (Gmail o altro SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tuoemail@gmail.com
EMAIL_HOST_PASSWORD=la-tua-app-password
DEFAULT_FROM_EMAIL=tuoemail@gmail.com
```

> **IMPORTANTE:**  
> - Non usare `Client ID` e `Client secret` di **"OAuth 2.0 Client IDs"** di tipo "Desktop" o "Android/iOS". Devono essere **Web application**.
> - Il file `.env` **NON deve essere commitato** nel repository (è in `.gitignore`).
> - Per sicurezza, ruota (cambia) periodicamente il `Client Secret` in Google Cloud Console.

### Passo 4.2: Variabili d'ambiente per produzione (Render.com)

Se deployi su **Render.com** (attualmente in uso: `vivere-con-il-cane.onrender.com`):

1. Vai sul dashboard di Render → seleziona il tuo servizio web
2. Vai su **Environment** → **Environment Variables**
3. Aggiungi/Varia le seguenti variabili:

| Chiave | Valore | Note |
|--------|--------|------|
| `GOOGLE_OAUTH_CLIENT_ID` | Il tuo Client ID (stesso di locale) | |
| `GOOGLE_OAUTH_CLIENT_SECRET` | Il tuo Client Secret (stesso di locale) | |
| `GOOGLE_OAUTH_REDIRECT_URI` | `https://vivere-con-il-cane.onrender.com/auth/google/callback` | **Diverso da locale!** |

**Differenze rispetto a locale:**
- `GOOGLE_OAUTH_REDIRECT_URI` deve essere **esattamente** `https://vivere-con-il-cane.onrender.com/auth/google/callback`
- Il `Client ID` e `Client Secret` possono essere gli stessi di locale (Google permette multipli redirect URI nello stesso client)

> **Nota su Render**: Se il dominio cambia (es. da `.onrender.com` a personalizzato), aggiorna sia il redirect URI in Google Cloud Console che la variabile d'ambiente.

---

## 🧪 Parte 5: Test della Configurazione

### Passo 5.1: Verifica prerequisites

Prima di testare, assicurati che:

1. Il file `.env` esiste e contiene le tre variabili Google OAuth
2. `django-allauth` è installato (controlla `requirements.txt`: `django-allauth>=65.0`)
3. Le migrazioni sono state applicate:

```bash
python manage.py migrate
```

### Passo 5.2: Test del Social Login (allauth)

1. Avvia il server di sviluppo:

```bash
python manage.py runserver
```

2. Vai su: http://localhost:8000/accounts/login/
3. Clicca il pulsante **"Accedi con Google"**
4. Dovresti essere reindirizzato a Google per autorizzare l'accesso
5. Dopo l'autorizzazione, torni al sito loggato

**Se vedi un errore "redirect_uri_mismatch":**
- Controlla che `http://localhost:8000/accounts/google/login/callback/` sia nei redirect URI autorizzati in Google Cloud Console
- Verifica che non ci siano slash di troppo o mancanti

**Se il bottone Google non appare:**
- Controlla che in `settings.py` ci siano le app `allauth` e `allauth.socialaccount.providers.google` in `INSTALLED_APPS`
- Assicurati che le variabili d'ambiente siano caricate (controlla `python manage.py diffsettings` o aggiungi un print temporaneo)

### Passo 5.3: Test di Google Health/Fit OAuth

1. Vai su: http://localhost:8000/accounts/login/
2. Effettua il login (con Google o con username/password)
3. Vai alla pagina **Tool** → **Google Health Sync**
   URL: http://localhost:8000/tool/health-sync/
4. Clicca **"Connetti Google Fit"** (o simile)
5. Verrà avviato il flusso OAuth per Google Fit/Health
6. Autorizza l'accesso ai dati salute
7. Sei reindirizzato a `/auth/google/callback` e poi torni alla pagina sync

**Se ricevi errori:**
- `GOOGLE_OAUTH_CLIENT_ID not configured` → Variabile d'ambiente non letta
- `redirect_uri_mismatch` → URI non corrisponde a quello in Google Cloud
- `access_denied` → Hai negato l'autorizzazione nel popup Google
- `invalid_grant` → Client ID/Secret sbagliati o codice già usato

---

## ❌ Parte 6: Errori Comuni e Soluzioni

### Errore 1: `redirect_uri_mismatch`

**Sintomo:** Google mostra "Error: redirect_uri_mismatch"

**Cause possibili:**
1. Il redirect URI in Google Cloud Console **non è identico** a quello usato dall'app
   - Manca/extra slash (`/` vs `//`)
   - `http` vs `https`
   - Porta differente (`:8000` vs nessuna porta)
   - Path diverso (`/auth/google/callback` vs `/accounts/google/login/callback/`)
2. Stai usando un dominio diverso (es. ngrok) non autorizzato
3. L'URI in `.env` non corrisponde a quello in Google Cloud

**Soluzione:**
```bash
# 1. Verifica l'URI in uso:
# - Per social login: /accounts/google/login/callback/
# - Per Health Sync: /auth/google/callback

# 2. In Google Cloud Console → Credentials → Tuo Client → Edit
# Assicurati che sia nella lista Authorized redirect URIs:
# [ambiente] http://localhost:8000/[path]

# 3. Se in produzione su Render, usa:
# https://vivere-con-il-cane.onrender.com/[path]

# 4. Riavvia il server Django dopo aver modificato .env
```

---

### Errore 2: `invalid_client` o `unauthorized_client`

**Sintomo:** "Error: invalid_client" o "unauthorized_client"

**Cause:**
- `GOOGLE_OAUTH_CLIENT_ID` o `GOOGLE_OAUTH_CLIENT_SECRET` errati nel `.env`
- Client ID non è di tipo "Web application"
- Le credenziali sono di un progetto Google Cloud diverso da quello con le API abilitate

**Soluzione:**
```bash
# 1. Ricrea le credenziali:
# Google Cloud Console → APIs & Services → Credentials
# DELETE il client esistente (se incerto)
# CREATE → OAuth client ID → Web application

# 2. Copia PRECISAMENTE:
# Client ID: (inizia con numeri, poi .apps.googleusercontent.com)
# Client Secret: (inizia con GOCSPX- o simile)

# 3. Verifica in .env:
echo $GOOGLE_OAUTH_CLIENT_ID  # non deve essere vuoto
echo $GOOGLE_OAUTH_CLIENT_SECRET

# 4. Assicurati che il file .env sia nella ROOT del progetto
# (stessa directory di manage.py)
```

---

### Errore 3: `access_denied` (utente nega permessi)

**Sintomo:** L'utente clicca "Deny" nel popup Google e viene reindirizzato a una pagina d'errore

**Normalmente NON è un problema di configurazione.** L'utente ha scelto di non autorizzare.

**Se accade per errore:**
- Assicurati che gli **scope richiesti** (`fitness.activity.read`, `fitness.heart_rate.read`, ecc.) siano appropriati per la tua app
- Troppi scope possono spaventare gli utenti → considera se servono tutti

---

### Errore 4: `token exchange failed` (callback)

**Sintomo:** Dopo autorizzazione, la vista `google_fit_callback` restituisce JSON: `{"error": "Token exchange failed: ..."}`

**Cause:**
1. Client Secret errato
2. Redirect URI in callback NON corrisponde a quello nello step iniziale
3. Codice (`code`) scaduto (validità ~10 minuti)
4. Il client OAuth non ha abilitato l'API Google Fit

**Soluzione:**
```bash
# 1. Verifica GOOGLE_OAUTH_REDIRECT_URI in .env:
# Deve essere IDENTICO allo stesso URI usato in google_fit_auth_start

# 2. In google_fit_auth_start (views.py:455), viene usato:
redirect_uri=settings.GOOGLE_OAUTH_REDIRECT_URI

# 3. In settings.py, default è:
# "http://localhost:8000/auth/google/callback"
# Assicurati che .env non lo sovrascriva con valore sbagliato

# 4. Abilita Google Fit API:
# Google Cloud Console → APIs & Services → Library → "Google Fit API" → ENABLE
```

---

### Errore 5: Bottoni Google non visibili

**Sintomo:** La pagina di login non mostra il bottone "Accedi con Google"

**Cause:**
1. `django-allauth` non installato o non in `INSTALLED_APPS`
2. Template non carica il tag `{% provider_login_url 'google' %}`
3. Provider Google non abilitato in `settings.py`

**Soluzione:**
```bash
# 1. Verifica requirements.txt:
cat requirements.txt | grep allauth
# Deve esserci: django-allauth>=65.0

# Se manca, aggiungi e installa:
pip install django-allauth>=65.0

# 2. In settings.py, verifica:
INSTALLED_APPS = [
    ...
    'django.contrib.sites',        # Required
    'allauth',                     # Core
    'allauth.account',             # Account management
    'allauth.socialaccount',       # Social accounts
    'allauth.socialaccount.providers.google',  # Google provider
    ...
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# 3. Verifica template (templates/account/login.html):
{% provider_login_url 'google' %}  # Deve essere presente

# 4. Assicurati SITE_ID = 1 in settings.py
```

---

### Errore 6: `GOOGLE_OAUTH_CLIENT_ID not configured` in template

**Sintomo:** Nel template `socialaccount/snippets/provider_list.html` compare: "(Configura GOOGLE_OAUTH_CLIENT_ID in .env per abilitare)"

**Cause:** Allauth non trova le variabili d'ambiente.

**Soluzione:**
```bash
# 1. Verifica che il file .env sia nella directory corretta:
# Deve essere nella ROOT: C:\vivere-con-il-cane\.env
# (stessa directory di manage.py)

# 2. Controlla che settings.py carichi .env correttamente:
# In settings.py, riga 20:
load_dotenv(_BASE_DIR / ".env")

# 3. Verifica variabili:
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('GOOGLE_OAUTH_CLIENT_ID', 'NOT_SET'))"

# 4. Se non stampa il client ID, il .env non viene letto:
# - Controlla sintassi .env (niente spazi attorno all'=)
# - Riavvia il server Django
```

---

### Errore 7: L'utente viene creato ma senza email

**Sintomo:** Login con Google funziona, ma l'utente ha email vuota nel database Django

**Cause:**
Scope OAuth non includono `email` o `profile`

**Soluzione:**
```python
# In settings.py, SCOPE per Google:
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'OAUTH_PKCE_ENABLED': True,
    }
}

# Dopo modifica, riavvia server e riconnetti l'account Google
# (potrebbe richiedere disconnettersi prima)
```

---

### Errore 8: "Project is not found" in Google Cloud

**Sintomo:** Errore durante autorizzazione: "Error: project not found"

**Cause:** Il progetto Google Cloud non esiste o non è selezionato.

**Soluzione:**
```bash
# 1. Verifica di aver creato il progetto in:
# https://console.cloud.google.com/

# 2. Assicurati che le credenziali (OAuth client) siano
# associate al progetto CORRETTO (controlla in alto a sinistra)

# 3. Se hai più progetti, seleziona quello giusto dal dropdown
```

---

## 🏭 Parte 7: Considerazioni per Produzione

### 7.1 Domini Autorizzati (Authorized domains)

In **Google Cloud Console** → **OAuth consent screen**:

1. Nella sezione **"Authorized domains"**, aggiungi:
   - `vivere-con-il-cane.onrender.com` (dominio attuale)
   - Il tuo dominio personalizzato se lo usi (es. `vivereconilcane.com`)

2. Per **App Verification** (se l'app cresce):
   - Se oltre 100 utenti, Google richiede verifica dell'app
   - Vai su **OAuth consent screen** → **Publish App** → Submit for verification
   - Preparati a fornire: video dimostrativo, privacy policy, screenshot

### 7.2 HTTPS obbligatorio in produzione

**IMPORTANTE:** In produzione (`*.onrender.com` o dominio personalizzato):
- Google OAuth richiede **HTTPS** per tutti i redirect URI tranne `localhost`
- Non usare `http://` su Render/domini pubblici
- Usa sempre `https://` in produzione

### 7.3 Variabili d'ambiente sicure su Render

**Render.com Environment Variables:**

| Variabile | Consiglio sicurezza |
|-----------|-------------------|
| `GOOGLE_OAUTH_CLIENT_ID` | Pubblico, può essere esposto (non segreto) |
| `GOOGLE_OAUTH_CLIENT_SECRET` | **SEGRETO** - non loggare mai |
| `GOOGLE_OAUTH_REDIRECT_URI` | Pubblico, può essere esposto |

**Best practices:**
- Non commitare `.env` nel repository
- Su Render, le variabili d'ambiente sono crittografate
- Ruota il `Client Secret` ogni 6-12 mesi
- Limita accesso al progetto Google Cloud solo ai collaboratori necessari

### 7.4 Multiple redirect URIs

**Puoi avere TUTTI questi URI nello stesso OAuth Client:**

```
# Development
http://localhost:8000/accounts/google/login/callback/
http://localhost:8000/auth/google/callback

# Production (Render)
https://vivere-con-il-cane.onrender.com/accounts/google/login/callback/
https://vivere-con-il-cane.onrender.com/auth/google/callback

# Staging (es. ngrok)
https://abc123.ngrok-free.dev/accounts/google/login/callback/
https://abc123.ngrok-free.dev/auth/google/callback
```

**Non serve creare client separati** per dev e prod — un singolo client può gestire tutti gli ambienti.

### 7.5 Debug in produzione

Se il login Google non funziona su Render:

```bash
# 1. Log di Django su Render:
# Render → Logs → runtime (mostra errori Django)

# Cerca errori come:
# - allauth.socialaccount.providers.google.views.OAuth2CallbackView
# - google.auth.exceptions.OAuth2Error

# 2. Verifica variabili d'ambiente su Render:
# Render → Environment → controlla che GOOGLE_OAUTH_CLIENT_ID sia impostato

# 3. Test redirect URI:
# Apri in browser incognito:
# https://vivere-con-il-cane.onrender.com/accounts/google/login/
# Dovrebbe reindirizzare a accounts.google.com...

# 4. Verifica Google Cloud Console:
# APIs & Services → OAuth consent screen
# Assicurati che "vivere-con-il-cane.onrender.com" sia in "Authorized domains"
```

---

## 📁 Parte 8: File di Riferimento

### Struttura delle configurazioni nel codice:

```
config/settings.py (linee 53-98):
├── GOOGLE_OAUTH_CLIENT_ID = env.get("GOOGLE_OAUTH_CLIENT_ID", "")
├── GOOGLE_OAUTH_CLIENT_SECRET = env.get("GOOGLE_OAUTH_CLIENT_SECRET", "")
├── GOOGLE_OAUTH_REDIRECT_URI = env.get("GOOGLE_OAUTH_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
├── SOCIALACCOUNT_PROVIDERS = {
│   └── 'google': { 'SCOPE': ['profile', 'email'], ... }
│   }
└── INSTALLED_APPS include: allauth*, sites

canine_tools/views.py (linee 437-524):
├── google_fit_auth_start()        → Flusso OAuth custom per Health/Fit
└── google_fit_callback()          → Riceve code e scambia con token

templates/account/login.html (linea 20):
└── <a href="{% provider_login_url 'google' %}"> → Usa allauth
```

### Diagramma dei flussi OAuth:

```
┌─────────────────┐
│   Utente clicks  │
│  "Accedi Google" │
└────────┬────────┘
         │
         ▼
┌──────────────────────────────────────┐
│   django-allauth genera URL OAuth    │
│   redirect_uri: /accounts/google/... │
└────────┬─────────────────────────────┘
         │
         ▼
   ┌─────────────┐
   │  Google     │
   │  (login +   │
   │   consenso) │
   └──────┬──────┘
          │
          ▼
   ┌─────────────┐
   │ Callback a │
   │ /accounts/  │
   │google/callback │
   └──────┬──────┘
          │
          ▼
┌─────────────────────────────────────┐
│  Allauth crea/aggiorna User +       │
│  SocialAccount, logga utente        │
└─────────────────────────────────────┘


┌─────────────────┐
│ Utente clicca   │
│ "Connetti Fit"  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ google_fit_auth_start() genera URL  │
│ redirect_uri: /auth/google/callback │
│ Scope: fitness.heart_rate.read ecc. │
└────────┬────────────────────────────┘
         │
         ▼
   ┌─────────────┐
   │  Google     │
   │  (consenso  │
   │   specifico)│
   └──────┬──────┘
          │
          ▼
┌─────────────────────────────────────┐
│  google_fit_callback() riceve code  │
│  → Scambia con access_token         │
│  → Salva HealthConnectToken nel DB  │
│  → Redirect a /tool/health-sync/    │
└─────────────────────────────────────┘
```

---

## 🚀 Parte 9: Checklist Rapida

Prima di considerare completato il setup:

- [ ] Google Cloud Project creato
- [ ] Google Fit API abilitata (se usi Health Sync)
- [ ] OAuth Consent Screen configurato (con test user)
- [ ] OAuth 2.0 Client ID (Web application) creato
- [ ] **TUTTI** i redirect URI necessari aggiunti in Google Cloud Console:
  - [ ] `http://localhost:8000/accounts/google/login/callback/`
  - [ ] `https://vivere-con-il-cane.onrender.com/accounts/google/login/callback/`
  - [ ] `http://localhost:8000/auth/google/callback`
  - [ ] `https://vivere-con-il-cane.onrender.com/auth/google/callback`
- [ ] `.env` locale contiene `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`, `GOOGLE_OAUTH_REDIRECT_URI`
- [ ] Variabili d'ambiente Render configurate (se in produzione)
- [ ] `python manage.py migrate` eseguito (per tabelle `socialaccount_socialapp`, `healthconnecttoken`, etc.)
- [ ] Test login Google su http://localhost:8000/accounts/login/ funziona
- [ ] Test Health Sync su http://localhost:8000/tool/health-sync/ funziona
- [ ] Authorized domains in Google Cloud include `vivere-con-il-cane.onrender.com`

---

## 📚 Riferamenti Utili

- **django-allauth docs**: https://docs.allauth.org/en/latest/
- **Google OAuth 2.0**: https://developers.google.com/identity/protocols/oauth2
- **Google Fit API**: https://developers.google.com/fit
- **Health Connect API**: https://developers.google.com/health
- **OAuth consent screen**: https://console.cloud.google.com/apis/credentials/consent

---

## 🆘 Supporto

Se riscontri problemi non trattati in questa guida:

1. Controlla i log Django: `python manage.py runserver` mostra errori dettagliati
2. Verifica le variabili d'ambiente: `python -c "import os; print(os.getenv('GOOGLE_OAUTH_CLIENT_ID'))"`
3. Consulta i template: `templates/account/login.html`, `templates/socialaccount/snippets/`
4. Controlla le viste: `canine_tools/views.py` per Health Sync

**Buon lavoro!** 🐕❤️
