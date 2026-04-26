# Google OAuth Setup per Vivere con il Cane

Questa guida spiega come configurare l'autenticazione Google OAuth per il sito "Vivere con il Cane".

## Prerequisiti
- Un account Google Developer Console: https://console.cloud.google.com/
- Progetto creato nel Google Cloud Console

## Passo 1: Abilita Google+ API
1. Vai su https://console.cloud.google.com/apis/library
2. Cerca "Google+ API" o "People API" e abilitala

## Passo 2: Crea OAuth 2.0 Credentials
1. Vai su **APIs & Services** → **Credentials**
2. Clicca **CREATE CREDENTIALS** → **OAuth client ID**
3. Scegli tipo **Web application**
4. Dai un nome (es. "Vivere con il Cane - Login")

## Passo 3: Configura Authorized Redirect URIs
Aggiungi questi URL (sostituendo con il tuo dominio):

**Per sviluppo locale:**
```
http://localhost:8000/accounts/google/login/callback/
```

**Per produzione (Render):**
```
https://vivere-con-il-cane.onrender.com/accounts/google/login/callback/
```

**Per staging:**
```
https://[tuo-dominio-ngrok].ngrok-free.dev/accounts/google/login/callback/
```

## Passo 4: Ottieni le Credenziali
Dopo aver creato, vedrai:
- **Client ID**: (es. `123456-abcdef.apps.googleusercontent.com`)
- **Client Secret**: (una stringa lunga)

## Passo 5: Configura l'Ambiente

### Opzione A: .env file (Locale)
Crea/modifica il file `.env` nella root del progetto:

```env
GOOGLE_OAUTH_CLIENT_ID=123456-abcdef.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=il-tuo-client-secret
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8000/accounts/google/login/callback/
```

### Opzione B: Variabili d'Ambiente (Render/Deploy)
Nel pannello di controllo di Render:
1. Vai su **Environment** → **Environment Variables**
2. Aggiungi:
   - `GOOGLE_OAUTH_CLIENT_ID` = il tuo Client ID
   - `GOOGLE_OAUTH_CLIENT_SECRET` = il tuo Client Secret

## Passo 6: Test
Riavvia l'applicazione e vai su http://localhost:8000
Clicca "Accedi con Google" nella pagina di login.

## Risoluzione Problemi

### Errore redirect_uri_mismatch
Assicurati che l'URL di redirect sia **esattamente** lo stesso in:
- Google Cloud Console
- `.env` o variabili d'ambiente
- Il link nella pagina di login

### Errore "Project is not found"
Assicurati che il progetto sia attivo nel Google Cloud Console.

### Gli utenti non vengono creati
Controlla i log Django per errori. Verifica che `django-allauth` sia in `INSTALLED_APPS`.

## Note Importanti
- **Non commitare** il file `.env` o i secret nel repository!
- Limita gli accessi al progetto Google Cloud solo ai membri necessari
- Considera di impostare una scadenza per i Secret e ruotarli periodicamente

## Riferimenti
- django-allauth: https://docs.allauth.org/en/latest/
- Google OAuth: https://developers.google.com/identity/protocols/oauth2
