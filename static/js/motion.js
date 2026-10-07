/* ==========================================================================
   EMBER · motion.js — depth & transitions layer
   Loaded FIRST so it can set feature flags before wow.js/app.js initialize.
   - Cross-document View Transitions awareness (falls back to the legacy overlay)
   - Theme toggle with a circular wipe (View Transitions API)
   - Home hero 3D stage: entrance choreography + pointer depth parallax
   - Mobile menu, overlay a11y (Esc / focus), bottom-nav state, press feedback
   All effects are progressive: with no JS or reduced-motion the site is fully
   usable and static.
   ========================================================================== */
(function () {
  'use strict';

  var reduced = false;
  var fine = false;
  try {
    reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    fine = window.matchMedia('(pointer: fine)').matches;
  } catch (e) {}
  window.__EM_REDUCED = reduced;

  /* If the browser supports View Transitions, CSS handles page transitions and
     we ask the legacy overlay transition (wow.js) to stand down. */
  var vtCss = false;
  try {
    vtCss = !!(window.CSS && CSS.supports && CSS.supports('selector(::view-transition-new(root))'));
  } catch (e2) {}
  window.__EM_VT = vtCss && !reduced;
  window.__EM_NO_OVERLAY_TRANSITION = window.__EM_VT;

  /* ---------- Theme toggle with circular wipe ---------- */
  window.__emThemeToggle = function (next, evt) {
    var root = document.documentElement;
    var apply = function () {
      if (typeof window.setTheme === 'function') {
        window.setTheme(next);
      } else {
        root.setAttribute('data-theme', next);
      }
    };
    var canVT = !reduced && typeof document.startViewTransition === 'function';
    if (!canVT) { apply(); return; }

    var x = '92%', y = '8%';
    if (evt && evt.currentTarget && evt.currentTarget.getBoundingClientRect) {
      var r = evt.currentTarget.getBoundingClientRect();
      x = ((r.left + r.width / 2) / window.innerWidth * 100).toFixed(2) + '%';
      y = ((r.top + r.height / 2) / window.innerHeight * 100).toFixed(2) + '%';
    }
    root.style.setProperty('--em-vtx', x);
    root.style.setProperty('--em-vty', y);
    root.classList.add('em-theme-anim');

    var transition = null;
    try { transition = document.startViewTransition(apply); } catch (e3) { apply(); root.classList.remove('em-theme-anim'); return; }
    var done = function () { root.classList.remove('em-theme-anim'); };
    if (transition && transition.finished && transition.finished.finally) {
      transition.finished.finally(done);
    } else {
      setTimeout(done, 800);
    }
  };

  /* ---------- Home hero stage ---------- */
  function initHero() {
    var hero = document.querySelector('.em-hero');
    if (!hero) return;

    /* one orchestrated entrance */
    requestAnimationFrame(function () {
      setTimeout(function () { hero.classList.add('is-live'); }, 50);
    });

    if (reduced || !fine || window.innerWidth < 900) return;

    var layers = hero.querySelectorAll('[data-depth]');
    if (!layers.length) return;

    var raf = null;
    var tx = 0, ty = 0;

    var render = function () {
      raf = null;
      for (var i = 0; i < layers.length; i++) {
        var el = layers[i];
        var d = parseFloat(el.getAttribute('data-depth')) || 1;
        el.style.transform = 'translate3d(' + (tx * d * -26).toFixed(2) + 'px,' + (ty * d * -16).toFixed(2) + 'px,0)';
      }
    };

    hero.addEventListener('mousemove', function (e) {
      var r = hero.getBoundingClientRect();
      tx = (e.clientX - r.left) / r.width - 0.5;
      ty = (e.clientY - r.top) / r.height - 0.5;
      if (!raf) raf = requestAnimationFrame(render);
    }, { passive: true });

    hero.addEventListener('mouseleave', function () {
      tx = 0; ty = 0;
      if (!raf) raf = requestAnimationFrame(render);
    });
  }

  /* ---------- Mobile menu ---------- */
  function initMobileMenu() {
    var burger = document.getElementById('em-burger');
    var menu = document.getElementById('em-mobile-menu');
    if (!burger || !menu) return;

    var close = function () {
      menu.classList.remove('open');
      burger.setAttribute('aria-expanded', 'false');
    };
    var open = function () {
      menu.classList.add('open');
      burger.setAttribute('aria-expanded', 'true');
      var c = menu.querySelector('[data-emm-close]');
      if (c) c.focus();
    };

    burger.addEventListener('click', function () {
      if (menu.classList.contains('open')) { close(); } else { open(); }
    });
    menu.addEventListener('click', function (e) {
      if (e.target.closest('[data-emm-close]') || e.target.classList.contains('emm-backdrop')) { close(); }
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && menu.classList.contains('open')) { close(); }
    });
  }

  /* ---------- Cart drawer: Esc to close + focus handling ---------- */
  function initOverlayA11y() {
    var overlay = document.getElementById('cart-drawer-overlay');
    document.addEventListener('keydown', function (e) {
      if (e.key !== 'Escape' || !overlay) return;
      if (overlay.classList.contains('active')) {
        overlay.classList.remove('active');
      }
    });
    document.addEventListener('click', function (e) {
      var trigger = e.target.closest && e.target.closest('.toggle-cart-drawer');
      if (!trigger) return;
      setTimeout(function () {
        var btn = document.getElementById('cart-drawer-close');
        if (btn) btn.focus();
      }, 140);
    });
  }

  /* ---------- Bottom nav current state ---------- */
  function initBottomNav() {
    var links = document.querySelectorAll('.mobile-bottom-nav a[href]');
    var path = window.location.pathname;
    for (var i = 0; i < links.length; i++) {
      var href = (links[i].getAttribute('href') || '').split('?')[0];
      if (href && href !== '/' && path.indexOf(href) === 0) {
        links[i].classList.add('is-active');
      } else if (href === '/' && path === '/') {
        links[i].classList.add('is-active');
      }
    }
  }

  /* ---------- Tactile press feedback on quick actions ---------- */
  function initPressFeedback() {
    document.addEventListener('pointerdown', function (e) {
      var btn = e.target.closest && e.target.closest('.product-card-action-btn, .btn');
      if (!btn) return;
      btn.classList.add('em-pressed');
      setTimeout(function () { btn.classList.remove('em-pressed'); }, 220);
    }, { passive: true });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initHero();
    initMobileMenu();
    initOverlayA11y();
    initBottomNav();
    initPressFeedback();
  });
})();
