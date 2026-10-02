/* Service Worker: App-Dateien offline verfügbar. Immer zuerst Netz, damit Updates sofort ankommen.
   Karten, Routing und Adresssuche (fremde Server) laufen nie über den Cache. */
const CACHE = 'laufrouten-2.2.0';
const ASSETS = ['./', './index.html', './app.js', './style.css', './manifest.webmanifest', './profiles/laufen.brf',
  './vendor/leaflet/leaflet.js', './vendor/leaflet/leaflet.css',
  './icons/icon-192.png', './icons/icon-512.png', './icons/icon-maskable-512.png', './icons/apple-touch-icon.png'];
self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(ASSETS)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== self.location.origin) return;
  e.respondWith(fetch(req).then((res) => {
    if (res.ok) { const copy = res.clone(); caches.open(CACHE).then((c) => c.put(req, copy)); }
    return res;
  }).catch(() => caches.match(req).then((m) => m || caches.match('./index.html'))));
});
