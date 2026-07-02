/* ==========================================================================
   Florilegio — Navegación instantánea e interactividad móvil
   - Speculation Rules: prerender/prefetch de enlaces internos (Chrome/Edge)
   - Barra de progreso superior en navegaciones lentas
   - Efecto ripple táctil en botones y dock
   - Vibración háptica sutil en el dock (Android)
   ========================================================================== */
(function () {
  "use strict";

  /* ------------------------------------------------------------------
     1. Prerender / prefetch especulativo.
        Al tocar o pasar el dedo por un enlace, el navegador renderiza
        la página destino en segundo plano: la navegación es instantánea.
        Se excluyen rutas con efectos secundarios o privadas.
     ------------------------------------------------------------------ */
  var EXCLUDED = [
    "/cerrar-sesion/*",
    "/admin/*",
    "/accounts/*",
    "/api/*",
    "/autores/*",
    "/buscar/*"
  ];

  if (
    window.HTMLScriptElement &&
    HTMLScriptElement.supports &&
    HTMLScriptElement.supports("speculationrules")
  ) {
    var rules = {
      prerender: [
        {
          where: {
            and: [
              { href_matches: "/*" },
              { not: { href_matches: EXCLUDED } }
            ]
          },
          eagerness: "moderate"
        }
      ],
      prefetch: [
        {
          where: {
            and: [
              { href_matches: "/*" },
              { not: { href_matches: EXCLUDED } }
            ]
          },
          eagerness: "conservative"
        }
      ]
    };
    var spec = document.createElement("script");
    spec.type = "speculationrules";
    spec.textContent = JSON.stringify(rules);
    document.head.appendChild(spec);
  }

  /* ------------------------------------------------------------------
     2. Barra de progreso superior.
        Solo aparece si la navegación tarda más de 180 ms (las
        navegaciones prerenderizadas nunca la muestran).
     ------------------------------------------------------------------ */
  var bar = document.createElement("div");
  bar.id = "fm-progress";
  bar.setAttribute("aria-hidden", "true");
  document.documentElement.appendChild(bar);

  var progressTimer = null;

  function startProgress() {
    clearTimeout(progressTimer);
    progressTimer = setTimeout(function () {
      bar.classList.add("running");
    }, 180);
  }

  function stopProgress() {
    clearTimeout(progressTimer);
    bar.classList.remove("running");
  }

  document.addEventListener("click", function (e) {
    var a = e.target && e.target.closest ? e.target.closest("a[href]") : null;
    if (!a) return;
    if (e.defaultPrevented || e.metaKey || e.ctrlKey || e.shiftKey || a.target === "_blank") return;
    var href = a.getAttribute("href") || "";
    if (href.charAt(0) === "#" || a.origin !== location.origin) return;
    startProgress();
  });

  window.addEventListener("pageshow", stopProgress);
  window.addEventListener("pagehide", stopProgress);

  /* ------------------------------------------------------------------
     3. Ripple táctil (botones, dock y tarjetas de navegación)
     ------------------------------------------------------------------ */
  var RIPPLE_SEL = ".btn, .fm-nav-item, .pagination-btn, .pagination-num";

  document.addEventListener(
    "pointerdown",
    function (e) {
      var host = e.target && e.target.closest ? e.target.closest(RIPPLE_SEL) : null;
      if (!host) return;
      var rect = host.getBoundingClientRect();
      var size = Math.max(rect.width, rect.height) * 2;
      var ripple = document.createElement("span");
      ripple.className = "fm-ripple";
      ripple.style.width = ripple.style.height = size + "px";
      ripple.style.left = e.clientX - rect.left - size / 2 + "px";
      ripple.style.top = e.clientY - rect.top - size / 2 + "px";
      host.appendChild(ripple);
      ripple.addEventListener("animationend", function () {
        ripple.remove();
      });
    },
    { passive: true }
  );

  /* ------------------------------------------------------------------
     4. Estudios (móvil): al pulsar Leer/Estudiar, desplazar
        automáticamente hasta el contenido cuando termine de cargar
     ------------------------------------------------------------------ */
  function autoScrollOnLoad(btnId, targetId) {
    var btn = document.getElementById(btnId);
    var target = document.getElementById(targetId);
    if (!btn || !target) return;
    if (!window.matchMedia("(max-width: 991.98px)").matches) return;
    btn.addEventListener("click", function () {
      var initial = target.textContent.trim().length;
      var tries = 0;
      var iv = setInterval(function () {
        tries++;
        var len = target.textContent.trim().length;
        if (len > initial + 200 || (len > 400 && len !== initial)) {
          clearInterval(iv);
          setTimeout(function () {
            var y = target.getBoundingClientRect().top + window.pageYOffset - 80;
            window.scrollTo({ top: y, behavior: "smooth" });
          }, 300);
        } else if (tries > 40) {
          clearInterval(iv);
        }
      }, 250);
    });
  }
  autoScrollOnLoad("btn-leer", "leer-container");
  autoScrollOnLoad("btn-estudio", "interlinear-container");

  /* ------------------------------------------------------------------
     5. PWA: registrar el service worker (offline + instalable)
     ------------------------------------------------------------------ */
  if (
    "serviceWorker" in navigator &&
    (location.protocol === "https:" ||
      location.hostname === "localhost" ||
      location.hostname === "127.0.0.1")
  ) {
    window.addEventListener("load", function () {
      navigator.serviceWorker.register("/sw.js").catch(function () {
        /* sin SW: la web sigue funcionando igual */
      });
    });
  }

  /* ------------------------------------------------------------------
     6. Háptica sutil en el dock (solo Android/Chrome)
     ------------------------------------------------------------------ */
  if ("vibrate" in navigator) {
    document.addEventListener(
      "pointerdown",
      function (e) {
        if (e.target && e.target.closest && e.target.closest(".fm-nav-item")) {
          try {
            navigator.vibrate(8);
          } catch (err) {
            /* sin permiso: ignorar */
          }
        }
      },
      { passive: true }
    );
  }
})();
