// 讓戰神看盤可以「安裝成 App」：外殼檔案離線可開，資料一律即時抓
const CACHE = 'zhanshen-v46';
const SHELL = ['./', './index.html', './holders.html', './insider.html', './autoreload.js', './manifest.webmanifest', './icon-192.png', './icon-512.png'];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith('zhanshen-') && k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  const u = new URL(e.request.url);
  if (e.request.method !== 'GET' || u.hostname.includes('finmindtrade') || u.pathname.includes('/data/')) return;
  const mine = u.origin === location.origin && u.pathname.startsWith(new URL('./', location.href).pathname);
  e.respondWith(fetch(e.request, mine ? { cache:'no-cache' } : {}).then(r => {
    if (r.ok && (mine || /jsdelivr|unpkg|gstatic|googleapis/.test(u.hostname))){ const cp = r.clone(); caches.open(CACHE).then(c => c.put(e.request, cp)); }
    return r; }).catch(() => caches.match(e.request)));
});
