const CACHE_NAME = 'vivere-cane-cache-v1';
const ASSETS_TO_CACHE = [
  '/',
  '/static/css/style.css',
  '/manifest.json',
  '/static/images/hero_dog.png'
];

const SKIP_CACHE_PATHS = [
  '/login/',
  '/accounts/',
  '/admin/',
  '/api/',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE);
    })
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.filter((name) => name !== CACHE_NAME).map((name) => caches.delete(name))
      );
    })
  );
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  
  // Skip caching for auth and admin pages - always go to network
  if (SKIP_CACHE_PATHS.some(path => url.pathname.startsWith(path))) {
    return;
  }

  if (event.request.mode === 'navigate') {
    event.respondWith(
      fetch(event.request).catch(() => {
        return caches.match('/');
      })
    );
    return;
  }

  event.respondWith(
    caches.match(event.request).then((response) => {
      if (response) {
        return response;
      }
      return fetch(event.request).catch(() => {
        if (event.request.destination === 'image') {
          return new Response('', { status: 200, statusText: 'OK' });
        }
        return new Response('', { status: 200, statusText: 'OK' });
      });
    })
  );
});
