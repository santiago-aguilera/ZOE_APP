/* =============================================================================
 * ZOE — UI JavaScript compartido
 * ----------------------------------------------------------------------
 * Utilidades globales: toggle de sidebar, dropdowns, búsqueda, atajos
 * de teclado, helpers de DOM. Sin dependencias externas.
 * ============================================================================= */

(function () {
  'use strict';

  /* ===========================================================================
   *  Sidebar (colapsar / móvil)
   * ========================================================================= */
  function initSidebar() {
    const shell = document.getElementById('appShell');
    const sidebar = document.getElementById('sidebar');
    if (!shell || !sidebar) return;

    const STORAGE_KEY = 'zoe.sidebar.collapsed';

    // Restaurar estado
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved === '1') shell.classList.add('is-collapsed');
    } catch (e) { /* localStorage no disponible */ }

    // Botón de toggle (puede haber varios en la página)
    document.querySelectorAll('[data-sidebar-toggle]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        // En móvil: abrir/cerrar overlay. En desktop: colapsar.
        if (window.matchMedia('(max-width: 768px)').matches) {
          shell.classList.toggle('is-mobile-open');
          sidebar.classList.toggle('is-open');
        } else {
          shell.classList.toggle('is-collapsed');
          try {
            localStorage.setItem(
              STORAGE_KEY,
              shell.classList.contains('is-collapsed') ? '1' : '0'
            );
          } catch (e) { /* ignore */ }
        }
      });
    });

    // Cerrar sidebar móvil al hacer clic fuera
    document.addEventListener('click', function (ev) {
      if (!shell.classList.contains('is-mobile-open')) return;
      if (sidebar.contains(ev.target)) return;
      if (ev.target.closest('[data-sidebar-toggle]')) return;
      shell.classList.remove('is-mobile-open');
      sidebar.classList.remove('is-open');
    });
  }

  /* ===========================================================================
   *  Atajos de teclado globales
   * ========================================================================= */
  function initShortcuts() {
    document.addEventListener('keydown', function (ev) {
      // Ctrl/Cmd + K → enfocar búsqueda
      if ((ev.ctrlKey || ev.metaKey) && ev.key.toLowerCase() === 'k') {
        const search = document.querySelector('.topbar-search input[type="search"]');
        if (search) {
          ev.preventDefault();
          search.focus();
          search.select();
        }
      }
      // Esc → cerrar overlays móviles
      if (ev.key === 'Escape') {
        const shell = document.getElementById('appShell');
        if (shell) shell.classList.remove('is-mobile-open');
        const sidebar = document.getElementById('sidebar');
        if (sidebar) sidebar.classList.remove('is-open');
      }
    });
  }

  /* ===========================================================================
   *  Tabs (pestañas)
   * ========================================================================= */
  function initTabs() {
    document.querySelectorAll('[data-tabs]').forEach(function (group) {
      const tabs = group.querySelectorAll('[data-tab]');
      const panels = document.querySelectorAll(
        '[data-tab-panel][data-tab-group="' + group.dataset.tabs + '"]'
      );

      tabs.forEach(function (tab) {
        tab.addEventListener('click', function () {
          const target = tab.dataset.tab;
          tabs.forEach(function (t) { t.classList.toggle('is-active', t === tab); });
          panels.forEach(function (p) {
            p.classList.toggle('is-hidden', p.dataset.tabPanel !== target);
          });
        });
      });
    });
  }

  /* ===========================================================================
   *  Helpers
   * ========================================================================= */
  const ZoeUI = {
    /** Muestra una notificación tipo toast (DOM-based). */
    toast: function (message, type) {
      type = type || 'primary';
      const el = document.createElement('div');
      el.className = 'zoe-toast zoe-toast--' + type;
      el.textContent = message;
      el.style.cssText =
        'position:fixed;bottom:24px;right:24px;z-index:1000;' +
        'padding:12px 16px;border-radius:10px;font-size:14px;' +
        'background:#1E293B;color:#fff;box-shadow:0 12px 24px -8px rgba(15,23,42,.4);' +
        'opacity:0;transform:translateY(8px);transition:all .2s ease;';
      if (type === 'success') el.style.background = '#10B981';
      if (type === 'danger')  el.style.background = '#EF4444';
      document.body.appendChild(el);
      requestAnimationFrame(function () {
        el.style.opacity = '1';
        el.style.transform = 'translateY(0)';
      });
      setTimeout(function () {
        el.style.opacity = '0';
        el.style.transform = 'translateY(8px)';
        setTimeout(function () { el.remove(); }, 220);
      }, 3200);
    },
  };

  /* ===========================================================================
   *  Bootstrap
   * ========================================================================= */
  document.addEventListener('DOMContentLoaded', function () {
    initSidebar();
    initShortcuts();
    initTabs();
  });

  // Exponer para uso global
  window.ZoeUI = ZoeUI;
})();
