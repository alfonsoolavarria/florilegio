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
     4b. Home de app (Modo Joven): saludo, fecha y versículo del día
     ------------------------------------------------------------------ */
  var versoTexto = document.getElementById("fm-ah-verso-texto");
  if (versoTexto && document.documentElement.classList.contains("fm-joven")) {
    var saludoEl = document.getElementById("fm-ah-saludo");
    var fechaEl = document.getElementById("fm-ah-fecha");
    var refEl = document.getElementById("fm-ah-verso-ref");

    var ahora = new Date();
    var h = ahora.getHours();
    if (saludoEl) {
      saludoEl.textContent = h < 12 ? "Buenos días" : h < 20 ? "Buenas tardes" : "Buenas noches";
    }
    if (fechaEl) {
      fechaEl.textContent = ahora.toLocaleDateString("es-ES", {
        weekday: "long",
        day: "numeric",
        month: "long"
      });
    }

    var VERSOS = [
      { r: "Salmos 119:105", l: 19, c: 119, v: 105 },
      { r: "Juan 3:16", l: 43, c: 3, v: 16 },
      { r: "Filipenses 4:13", l: 50, c: 4, v: 13 },
      { r: "Jeremías 29:11", l: 24, c: 29, v: 11 },
      { r: "Romanos 8:28", l: 45, c: 8, v: 28 },
      { r: "Isaías 41:10", l: 23, c: 41, v: 10 },
      { r: "Proverbios 3:5", l: 20, c: 3, v: 5 },
      { r: "Salmos 46:1", l: 19, c: 46, v: 1 },
      { r: "Mateo 11:28", l: 40, c: 11, v: 28 },
      { r: "Josué 1:9", l: 6, c: 1, v: 9 },
      { r: "Salmos 23:1", l: 19, c: 23, v: 1 },
      { r: "2 Timoteo 1:7", l: 55, c: 1, v: 7 }
    ];
    var dia = Math.floor(Date.now() / 86400000);
    var pick = VERSOS[dia % VERSOS.length];

    fetch("/api/versiculo/?tipo=biblia&version=nbla&libro=" + pick.l + "&capitulo=" + pick.c + "&versiculo=" + pick.v)
      .then(function (r) { return r.json(); })
      .then(function (j) {
        var d = j && j.data;
        var texto = null;
        if (Array.isArray(d) && d.length) {
          var it = null;
          for (var i = 0; i < d.length; i++) {
            if (String(d[i].versiculo) === String(pick.v)) { it = d[i]; break; }
          }
          it = it || d[0];
          texto = it && it.texto;
        }
        if (texto) {
          var limpio = String(texto)
            .replace(/\/n|\bpar\b/g, " ")
            .replace(/[¶«»]/g, "")
            .replace(/\s+/g, " ")
            .trim()
            .replace(/[.\s]+$/, ".");
          versoTexto.textContent = "«" + limpio + "»";
          if (refEl) refEl.textContent = pick.r + " · NBLA";
        }
      })
      .catch(function () { /* se queda el versículo por defecto */ });
  }

  /* ------------------------------------------------------------------
     5. Interruptor de tema Clásico / Joven (persistente)
     ------------------------------------------------------------------ */
  var themeToggle = document.getElementById("fm-theme-toggle");
  var themeText = document.getElementById("fm-theme-toggle-text");

  function refreshThemeToggle() {
    if (!themeText) return;
    themeText.textContent = document.documentElement.classList.contains("fm-joven")
      ? "Volver al modo Clásico"
      : "Probar el modo Joven";
  }

  if (themeToggle) {
    refreshThemeToggle();
    themeToggle.addEventListener("click", function () {
      var cambiar = function () {
        var joven = document.documentElement.classList.toggle("fm-joven");
        try {
          localStorage.setItem("fm-theme", joven ? "joven" : "clasico");
        } catch (err) {}
        refreshThemeToggle();
      };
      if (document.startViewTransition) {
        document.startViewTransition(cambiar);
      } else {
        cambiar();
      }
    });
  }

  /* ------------------------------------------------------------------
     6. PWA: registrar el service worker (offline + instalable)
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
