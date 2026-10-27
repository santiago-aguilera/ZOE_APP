/* ZOE — comportamiento móvil: etiquetas de tablas, buscador desplegable, gestos */
(function () {
  'use strict';

  /* 1) data-label en cada celda según su encabezado (tablas → tarjetas) */
  function etiquetarTablas() {
    document.querySelectorAll('table.table').forEach(function (tabla) {
      if (tabla.classList.contains('permisos-table') || tabla.classList.contains('table-keep')) return;
      var ths = tabla.querySelectorAll('thead th');
      if (!ths.length) return;
      var textos = Array.prototype.map.call(ths, function (th) { return th.textContent.trim(); });
      tabla.querySelectorAll('tbody tr').forEach(function (fila) {
        var col = 0;
        Array.prototype.forEach.call(fila.children, function (celda) {
          var span = parseInt(celda.getAttribute('colspan') || '1', 10);
          if (span === 1 && textos[col] && !celda.hasAttribute('data-label')) {
            celda.setAttribute('data-label', textos[col]);
          }
          col += span;
        });
      });
    });
  }

  /* 2) Buscador desplegable en móvil */
  function initBuscadorMovil() {
    var btn = document.getElementById('topbarSearchBtn');
    var caja = document.querySelector('.topbar-search');
    if (!btn || !caja) return;
    btn.addEventListener('click', function (ev) {
      ev.stopPropagation();
      var abierto = caja.classList.toggle('is-open');
      btn.setAttribute('aria-expanded', abierto ? 'true' : 'false');
      if (abierto) { var i = caja.querySelector('input'); if (i) i.focus(); }
    });
    document.addEventListener('click', function (ev) {
      if (!caja.classList.contains('is-open')) return;
      if (caja.contains(ev.target) || btn.contains(ev.target)) return;
      caja.classList.remove('is-open');
      btn.setAttribute('aria-expanded', 'false');
    });
  }

  /* 3) Menú lateral: aria, cerrar con gesto de deslizar a la izquierda */
  function initDrawer() {
    var shell = document.getElementById('appShell');
    var sidebar = document.getElementById('sidebar');
    var menuBtn = document.getElementById('topbarMenuBtn');
    if (!shell || !sidebar) return;

    function sincronizar() {
      if (menuBtn) menuBtn.setAttribute('aria-expanded', shell.classList.contains('is-mobile-open') ? 'true' : 'false');
    }
    new MutationObserver(sincronizar).observe(shell, { attributes: true, attributeFilter: ['class'] });

    var x0 = null;
    sidebar.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    sidebar.addEventListener('touchend', function (e) {
      if (x0 === null) return;
      var dx = e.changedTouches[0].clientX - x0;
      x0 = null;
      if (dx < -60) { shell.classList.remove('is-mobile-open'); sidebar.classList.remove('is-open'); }
    }, { passive: true });

    /* Si se agranda la ventana, limpiar el estado del drawer */
    window.addEventListener('resize', function () {
      if (window.innerWidth > 768) { shell.classList.remove('is-mobile-open'); sidebar.classList.remove('is-open'); }
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    etiquetarTablas();
    initBuscadorMovil();
    initDrawer();
  });
})();
