/* Florilegio de la Fe — Service Worker (PWA)
   Estrategia: red primero con respaldo de caché (siempre fresco online,
   funcional offline con lo ya visitado). */

var CACHE = "florilegio-v1";

self.addEventListener("install", function (e) {
  self.skipWaiting();
});

self.addEventListener("activate", function (e) {
  e.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(
        keys.filter(function (k) { return k !== CACHE; }).map(function (k) { return caches.delete(k); })
      );
    }).then(function () {
      return self.clients.claim();
    })
  );
});

self.addEventListener("fetch", function (e) {
  var req = e.request;
  if (req.method !== "GET") return;

  var url = new URL(req.url);
  if (url.origin !== self.location.origin) return;
  if (url.pathname.indexOf("/admin") === 0 || url.pathname.indexOf("/api/") === 0 || url.pathname === "/sw.js") return;

  e.respondWith(
    fetch(req)
      .then(function (resp) {
        if (resp && resp.ok && (resp.type === "basic" || resp.type === "default")) {
          var copia = resp.clone();
          caches.open(CACHE).then(function (c) {
            c.put(req, copia);
          });
        }
        return resp;
      })
      .catch(function () {
        return caches.match(req).then(function (hit) {
          if (hit) return hit;
          if (req.mode === "navigate") return caches.match("/");
          return Response.error();
        });
      })
  );
});
