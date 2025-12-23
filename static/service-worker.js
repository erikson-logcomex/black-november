// Service Worker para PWA
const CACHE_NAME = 'black-november-v2';
const urlsToCache = [
  '/',
  '/static/css/funnel.css',
  '/static/css/deal_celebration.css',
  '/static/javascript/funnel.js',
  '/static/javascript/deal_celebration.js'
];

// Instalação do Service Worker
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Cache aberto');
        return cache.addAll(urlsToCache);
      })
  );
});

// Ativação do Service Worker
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('Removendo cache antigo:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Interceptar requisições
self.addEventListener('fetch', event => {
  // Não cachear chamadas à API (sempre buscar dados frescos)
  if (event.request.url.includes('/api/')) {
    return;
  }
  
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Retorna do cache se encontrar, senão busca da rede
        return response || fetch(event.request);
      })
  );
});
