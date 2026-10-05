const CACHE_NAME = "mg-climate-monthly-v6";
const CORE_ASSETS = [
  "./",
  "index.html",
  "styles.css",
  "app.js",
  "i18n.js",
  "recent.js",
  "favicon.svg",
  "data/manifest.json",
  "data/update-status.json",
];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(CORE_ASSETS)));
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))))
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;
  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin) return;
  const networkFirst = url.pathname.endsWith("/manifest.json")
    || url.pathname.endsWith("/update-status.json")
    || !url.pathname.includes("/data/");
  event.respondWith((async () => {
    const cache = await caches.open(CACHE_NAME);
    const cached = await cache.match(event.request);
    if (!networkFirst && cached) return cached;
    try {
      const response = await fetch(event.request);
      if (response.ok) await cache.put(event.request, response.clone());
      if (!response.ok && cached) return cached;
      return response;
    } catch (error) {
      if (cached) return cached;
      throw error;
    }
  })());
});
