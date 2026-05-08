const CACHE_NAME = 'liderlog-v2';
const CACHE_API = 'liderlog-api-v1';

const ASSETS = [
  '/',
  '/LiderLog.html',
  '/manifest.json',
  '/sw.js',
  // Fontes locais (serão adicionadas após self-host)
  // '/fonts/plus-jakarta-sans.woff2',
  // '/fonts/syne.woff2',
];

// Install: pré-cache assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(ASSETS))
      .then(() => self.skipWaiting())
  );
});

// Activate: limpar caches antigos
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(
      keys.filter((key) => key !== CACHE_NAME && key !== CACHE_API)
        .map((key) => caches.delete(key))
    ))
  );
  self.clients.claim();
});

// Fetch strategy helper
async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) return cached;
  const network = await fetch(request);
  return network;
}

async function networkFirst(request) {
  try {
    const network = await fetch(request);
    // Cache.put só se for GET e response ok
    if (request.method === 'GET' && network.ok) {
      const cache = await caches.open(CACHE_API);
      cache.put(request, network.clone());
    }
    return network;
  } catch (err) {
    const cached = await caches.match(request);
    if (cached) return cached;
    throw err;
  }
}

async function staleWhileRevalidate(request) {
  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(request);
  const fetchPromise = fetch(request).then(network => {
    cache.put(request, network.clone());
    return network;
  });
  return cached || fetchPromise;
}

self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // 1) API: Network-First com fallback para cache
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirst(request));
    return;
  }

  // 2) Uploads: Stale-While-Revalidate (imagens de canhoto)
  if (url.pathname.startsWith('/uploads/')) {
    event.respondWith(staleWhileRevalidate(request));
    return;
  }

  // 3) Assets estáticos (HTML, manifest, fonts, icons): Cache-First
  if (url.pathname.match(/\.(html|json|js|css|woff2?|png|jpg|jpeg|svg)$/) || 
      ASSETS.includes(url.pathname)) {
    event.respondWith(cacheFirst(request));
    return;
  }

  // Default: Network-First
  event.respondWith(networkFirst(request));
});
