# Progressive Web App (PWA) Setup Guide

This guide covers configuring and optimizing the app as a **Progressive Web App**.

## Table of Contents

- [What is a PWA?](#what-is-a-pwa)
- [Current Setup](#current-setup)
- [Configuration](#configuration)
- [Service Worker](#service-worker)
- [Testing](#testing)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

## What is a PWA?

A **Progressive Web App** is a web app that works like a native app:

✅ **Installable** - Users can install from browser
✅ **Offline capable** - Works without internet
✅ **Fast** - Cached assets load instantly
✅ **Responsive** - Works on phone, tablet, desktop
✅ **Secure** - HTTPS only

## Current Setup

Your app includes PWA support:

- ✅ `manifest.json` - App metadata
- ✅ Service worker - Offline support
- ✅ Icons - Different sizes for devices
- ✅ HTTPS ready - Works with Render, Docker
- ✅ Responsive design - Mobile-first

## Configuration

### Web Manifest

**Location:** `static/manifest.json`

Controls how your app appears when installed:

```json
{
  "name": "Vivere con il Cane",
  "short_name": "VivereCanine",
  "description": "AI-powered dog behavior analysis and education",
  "start_url": "/",
  "scope": "/",
  "display": "standalone",
  "orientation": "portrait-or-landscape",
  "theme_color": "#8B4513",
  "background_color": "#FFFFFF",
  "categories": ["education", "lifestyle"],
  "screenshots": [
    {
      "src": "/static/images/screenshot-540.png",
      "sizes": "540x720",
      "type": "image/png",
      "form_factor": "narrow"
    },
    {
      "src": "/static/images/screenshot-1280.png",
      "sizes": "1280x720",
      "type": "image/png",
      "form_factor": "wide"
    }
  ],
  "icons": [
    {
      "src": "/static/images/icon-192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/static/images/icon-512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/static/images/maskable-icon-192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "maskable"
    }
  ],
  "shortcuts": [
    {
      "name": "Analyze Behavior",
      "short_name": "Analyze",
      "description": "Analyze your dog's behavior with AI",
      "url": "/analizza/?source=pwa",
      "icons": [
        {
          "src": "/static/images/analyze-192.png",
          "sizes": "192x192"
        }
      ]
    },
    {
      "name": "My Dog",
      "short_name": "Dog",
      "description": "View your dog's profile",
      "url": "/it/cane/",
      "icons": [
        {
          "src": "/static/images/dog-192.png",
          "sizes": "192x192"
        }
      ]
    }
  ],
  "share_target": {
    "action": "/share/",
    "method": "POST",
    "enctype": "application/x-www-form-urlencoded",
    "params": {
      "title": "title",
      "text": "text",
      "url": "url"
    }
  }
}
```

### Manifest Fields Explained

| Field | Purpose | Example |
|-------|---------|---------|
| `name` | Full app name | "Vivere con il Cane" |
| `short_name` | Display name (12 chars) | "VivereCanine" |
| `description` | What your app does | "AI-powered dog..." |
| `start_url` | Home page when launched | "/" |
| `display` | UI mode (standalone/fullscreen) | "standalone" |
| `theme_color` | Top bar color | "#8B4513" |
| `background_color` | Splash screen color | "#FFFFFF" |
| `icons` | App icons (192x192, 512x512 min) | Array of icons |
| `screenshots` | App screenshots in store | Array of 540x720+ |
| `shortcuts` | Quick launch actions | Array of 3-5 shortcuts |

### HTML Header

Add to `templates/base.html` head:

```html
<!-- PWA Meta Tags -->
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="AI-powered dog behavior analysis">
<meta name="theme-color" content="#8B4513">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Vivere con il Cane">

<!-- App Icons -->
<link rel="icon" href="/static/images/favicon.ico" type="image/x-icon">
<link rel="apple-touch-icon" href="/static/images/apple-touch-icon-180.png">
<link rel="manifest" href="/static/manifest.json">

<!-- Service Worker -->
<script>
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/static/service-worker.js')
        .then(reg => console.log('Service Worker registered'))
        .catch(err => console.log('SW registration failed:', err));
    });
  }
</script>
```

## Service Worker

**Location:** `static/service-worker.js`

Enables offline functionality and caching.

### What It Does

1. **Install** - Cache essential assets
2. **Activate** - Clean up old caches
3. **Fetch** - Serve from cache when offline
4. **Update** - Check for new versions

### Example Service Worker

```javascript
const CACHE_NAME = 'vivere-v1';
const ASSETS = [
  '/',
  '/static/css/style.css',
  '/static/js/main.js',
  '/static/images/logo.png',
  '/offline.html'
];

// Install: Cache assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(ASSETS))
      .then(() => self.skipWaiting())
  );
});

// Activate: Clean old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames =>
      Promise.all(
        cacheNames.map(name => {
          if (name !== CACHE_NAME) {
            return caches.delete(name);
          }
        })
      )
    ).then(() => self.clients.claim())
  );
});

// Fetch: Network first, fallback to cache
self.addEventListener('fetch', event => {
  // Skip non-GET requests
  if (event.request.method !== 'GET') return;

  event.respondWith(
    fetch(event.request)
      .then(response => {
        // Cache successful responses
        if (response.ok) {
          caches.open(CACHE_NAME)
            .then(cache => cache.put(event.request, response.clone()));
        }
        return response;
      })
      .catch(() => {
        // Serve from cache on error
        return caches.match(event.request)
          .then(response => response || caches.match('/offline.html'));
      })
  );
});
```

### Cache Strategies

**Network First** (default):
- Try network first
- Fall back to cache
- Good for frequently updated content

**Cache First**:
- Try cache first
- Fall back to network
- Good for static assets

**Stale While Revalidate**:
- Serve cache immediately
- Update in background
- Best of both worlds

```javascript
// Stale while revalidate
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.open(CACHE_NAME).then(cache => {
      return cache.match(event.request)
        .then(response => {
          // Return cached, fetch update in background
          const fetchPromise = fetch(event.request)
            .then(networkResponse => {
              cache.put(event.request, networkResponse.clone());
              return networkResponse;
            });
          return response || fetchPromise;
        });
    })
  );
});
```

### Create Offline Page

**Location:** `templates/offline.html`

```html
<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Non in linea</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100vh;
      background: #f5f5f5;
    }
    .container {
      text-align: center;
      padding: 2rem;
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    h1 { color: #333; }
    p { color: #666; }
    .icon { font-size: 4rem; }
  </style>
</head>
<body>
  <div class="container">
    <div class="icon">📱</div>
    <h1>Non in linea</h1>
    <p>Non sei connesso a Internet.</p>
    <p>Alcuni contenuti potrebbero non essere disponibili.</p>
  </div>
</body>
</html>
```

## Testing

### Check PWA Readiness

**Chrome DevTools:**

1. Open **DevTools** (F12)
2. Go to **Lighthouse** tab
3. Run **PWA audit**
4. Target: 90+ score

### Manual Testing

**Install app:**

1. Visit your site: `https://vivere-con-il-cane.onrender.com`
2. Click address bar icon or browser menu
3. Select "Install app" or "Add to Home Screen"
4. App appears on home screen

**Test offline:**

1. Open DevTools → Network
2. Set to "Offline"
3. Refresh page
4. App should still work

**Check service worker:**

1. Open DevTools → Application
2. Go to Service Workers
3. Should show "activated and running"

### Test in Different Browsers

| Browser | PWA Support | Install Method |
|---------|-------------|-----------------|
| Chrome | ✅ Full | Menu → "Install app" |
| Firefox | ✅ Full | Menu → "Install" |
| Safari (iOS) | ⚠️ Partial | Share → "Add to Home Screen" |
| Edge | ✅ Full | Menu → "Install" |
| Samsung | ✅ Full | Menu → "Install" |

### Performance Testing

Use **Lighthouse CLI:**

```bash
# Install
npm install -g lighthouse

# Test PWA
lighthouse https://vivere-con-il-cane.onrender.com --view

# Generate report
lighthouse https://vivere-con-il-cane.onrender.com --output=html
```

### Test Code

```python
# tests/test_pwa.py
from django.test import TestCase, Client

class PWATestCase(TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_manifest_exists(self):
        """Test manifest.json is served"""
        response = self.client.get('/static/manifest.json')
        self.assertEqual(response.status_code, 200)
    
    def test_manifest_valid_json(self):
        """Test manifest is valid JSON"""
        response = self.client.get('/static/manifest.json')
        data = response.json()
        self.assertIn('name', data)
        self.assertIn('icons', data)
        self.assertIn('start_url', data)
    
    def test_service_worker_exists(self):
        """Test service worker is served"""
        response = self.client.get('/static/service-worker.js')
        self.assertEqual(response.status_code, 200)
        self.assertIn('serviceWorker', response.content.decode())
    
    def test_offline_page_exists(self):
        """Test offline fallback page"""
        response = self.client.get('/offline.html')
        self.assertEqual(response.status_code, 200)
    
    def test_pwa_meta_tags(self):
        """Test PWA meta tags in base template"""
        response = self.client.get('/')
        content = response.content.decode()
        self.assertIn('manifest.json', content)
        self.assertIn('service-worker', content)
        self.assertIn('apple-mobile-web-app-capable', content)
```

## Deployment

### Render.com

PWA works automatically with Render since it provides HTTPS.

No additional configuration needed!

### Docker

Ensure HTTPS is enabled:

```dockerfile
# Dockerfile
FROM python:3.10-slim

# ... rest of configuration

# Collect static files
RUN python manage.py collectstatic --noinput

# Use gunicorn with https
CMD ["gunicorn", \
     "--bind", "0.0.0.0:8000", \
     "--certfile=/etc/ssl/certs/cert.pem", \
     "--keyfile=/etc/ssl/private/key.pem", \
     "config.wsgi:application"]
```

### nginx Proxy Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name vivere-con-il-cane.com;

    ssl_certificate /etc/letsencrypt/live/vivere-con-il-cane.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/vivere-con-il-cane.com/privkey.pem;

    # PWA headers
    add_header Service-Worker-Allowed "/";
    add_header Cache-Control "max-age=0, must-revalidate" always;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto https;
    }

    location /static/ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

## Troubleshooting

### ❌ "App won't install"

**Possible causes:**
1. Missing HTTPS
2. Invalid manifest.json
3. No service worker
4. Incorrect icons

**Solution:**
```bash
# Check manifest validity
curl https://vivere-con-il-cane.onrender.com/static/manifest.json | jq

# Check headers
curl -I https://vivere-con-il-cane.onrender.com/static/service-worker.js

# Must see: Content-Type: application/javascript
```

### ❌ "Offline doesn't work"

**Problem:** Service worker not installed

**Solution:**
```javascript
// Debug in console
navigator.serviceWorker.getRegistrations()
  .then(registrations => {
    registrations.forEach(r => {
      console.log('SW:', r);
      console.log('State:', r.active?.state || 'not active');
    });
  });

// Force unregister and reinstall
navigator.serviceWorker.getRegistrations()
  .then(registrations => {
    registrations.forEach(r => r.unregister());
  });

// Restart browser, revisit site
```

### ❌ "Icons not showing"

**Problem:** Icon files missing or wrong path

**Solution:**
```bash
# Check icons exist
ls static/images/icon-*.png

# Check manifest points to right path
grep "icon" static/manifest.json

# Must match exactly!
```

### ❌ "Cache stale after update"

**Problem:** Old version served after deploy

**Solution:**
```javascript
// Bump version in service worker
const CACHE_NAME = 'vivere-v2';  // Change version

// Users will get new cache on next visit
```

### ❌ "App crashes offline"

**Problem:** Page not cached or API call fails

**Solution:**
1. Add offline.html to cache
2. Handle API errors gracefully
3. Show offline message

```javascript
// In service worker
const ASSETS = [
  '/',
  '/offline.html',
  '/static/css/style.css',
];

// In fetch handler
fetch(event.request)
  .catch(() => {
    if (event.request.destination === 'document') {
      return caches.match('/offline.html');
    }
    return new Response('Offline', { status: 503 });
  });
```

---

**Questions?** Check [README.md](README.md) or open an issue on GitHub!
