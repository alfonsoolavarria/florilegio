/* Florilegio de la Fe — Service Worker (PWA)
   Estrategia: red primero con respaldo de caché (siempre fresco online,
   funcional offline con lo ya visitado). */

var CACHE = "florilegio-v2";

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
          if (req.mode === "navigate") {
            return caches.match("/").then(function (home) {
              if (home) return home;
              return new Response(
                "<!doctype html><html lang='es'><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><body style='font-family:sans-serif;background:#f7f3ed;display:flex;min-height:100vh;align-items:center;justify-content:center;text-align:center;padding:2rem'><div><h2 style='color:#800020'>Sin conexión</h2><p>Vuelve a intentarlo cuando tengas internet.</p></div></body></html>",
                { headers: { "Content-Type": "text/html; charset=utf-8" } }
              );
            });
          }
          return Response.error();
        });
      })
  );
});
