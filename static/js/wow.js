/**
 * WOW Layer — 3D tilt, cinematic transitions, compare system & micro-interactions
 */
(function () {
  'use strict';

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  document.addEventListener('DOMContentLoaded', () => {
    initScrollProgress();
    initHeaderScroll();
    initTilt3D();
    initStaggerReveal();
    initCountUp();
    initHeroParallax();
    initButtonRipples();
    initCompareSystem();
    patchAddToCartFX();
    initPageTransitions();
    initRangeSliders();
    initChipFilters();
    if (document.querySelector('.wow-celebrate')) launchConfetti();
  });

  /* ---------- Chip-style filter checkboxes (brand multi-select) ---------- */
  function initChipFilters() {
    document.querySelectorAll('[data-wow-filter-submit]').forEach(box => {
      const chip = box.nextElementSibling;
      const wrap = chip ? chip.closest('.wow-chip-group') : null;
      if (wrap) {
        wrap.addEventListener('click', (e) => {
          const target = e.target.closest('label');
          if (!target) return;
          const input = target.querySelector('input[type=checkbox]');
          if (!input) return;
          e.preventDefault();
          input.checked = !input.checked;
          target.querySelector('.wow-chip')?.classList.toggle('wow-chip-active', input.checked);
          input.closest('form')?.submit();
        });
      } else {
        box.addEventListener('change', () => box.form && box.form.submit());
      }
    });
  }

  /* ---------- Scroll progress bar ---------- */
  function initScrollProgress() {
    let bar = document.getElementById('wow-scroll-progress');
    if (!bar) {
      bar = document.createElement('div');
      bar.id = 'wow-scroll-progress';
      document.body.appendChild(bar);
    }
    const update = () => {
      const h = document.documentElement;
      const pct = (h.scrollTop / (h.scrollHeight - h.clientHeight)) * 100;
      bar.style.width = pct + '%';
    };
    window.addEventListener('scroll', update, { passive: true });
    update();
  }

  /* ---------- Frosted sticky header ---------- */
  function initHeaderScroll() {
    const header = document.querySelector('.site-header');
    if (!header) return;
    const toggle = () => header.classList.toggle('wow-header-scrolled', window.scrollY > 24);
    window.addEventListener('scroll', toggle, { passive: true });
    toggle();
  }

  /* ---------- 3D tilt with holographic cursor glow ---------- */
  function initTilt3D() {
    if (prefersReducedMotion) return;
    const MAX_DEG = 9;
    const bind = (el) => {
      if (el.dataset.wowTiltBound) return;
      el.dataset.wowTiltBound = '1';
      el.classList.add('wow-tilt');
      let raf = null;

      el.addEventListener('mousemove', (e) => {
        const rect = el.getBoundingClientRect();
        const x = (e.clientX - rect.left) / rect.width;
        const y = (e.clientY - rect.top) / rect.height;
        if (raf) cancelAnimationFrame(raf);
        raf = requestAnimationFrame(() => {
          el.style.transform =
            `perspective(750px) rotateY(${(x - 0.5) * MAX_DEG * 2}deg) rotateX(${(0.5 - y) * MAX_DEG * 2}deg) translateY(-6px) scale(1.02)`;
          el.style.setProperty('--wow-mx', `${x * 100}%`);
          el.style.setProperty('--wow-my', `${y * 100}%`);
          el.style.setProperty('--wow-angle', `${Math.atan2(y - 0.5, x - 0.5) * 57.3 + 180}deg`);
        });
      });

      el.addEventListener('mouseleave', () => {
        if (raf) cancelAnimationFrame(raf);
        el.style.transform = '';
      });
    };

    const scan = () => {
      document.querySelectorAll('.product-card, .category-card, .wow-stat-box, .wow-gallery-main').forEach(bind);
    };
    scan();
    new MutationObserver(scan).observe(document.body, { childList: true, subtree: true });
  }

  /* ---------- Staggered reveal for grids ---------- */
  function initStaggerReveal() {
    document.querySelectorAll('.grid, .wow-stats-strip, [data-wow-stagger]').forEach(grid => {
      grid.classList.add('wow-stagger');
      [...grid.children].forEach((child, i) => child.style.setProperty('--wow-i', Math.min(i, 8)));
    });
    if (!('IntersectionObserver' in window)) {
      document.querySelectorAll('.wow-stagger').forEach(g => g.classList.add('wow-stagger-in'));
      return;
    }
    const io = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('wow-stagger-in');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08 });
    document.querySelectorAll('.wow-stagger').forEach(g => io.observe(g));
  }

  /* ---------- Animated count-up stats ---------- */
  function initCountUp() {
    const els = document.querySelectorAll('[data-wow-count]');
    if (!els.length) return;
    const faDigits = s => s.replace(/\d/g, d => '۰۱۲۳۴۵۶۷۸۹'[d]);
    const animate = (el) => {
      const target = parseFloat(el.dataset.wowCount);
      const suffix = el.dataset.wowSuffix || '';
      const dur = 1600;
      const t0 = performance.now();
      const step = (now) => {
        const p = Math.min(1, (now - t0) / dur);
        const eased = 1 - Math.pow(1 - p, 4);
        const val = Math.round(target * eased).toLocaleString('en-US');
        el.textContent = faDigits(val) + suffix;
        if (p < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    };
    const io = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) { animate(e.target); io.unobserve(e.target); }
      });
    }, { threshold: 0.4 });
    els.forEach(el => io.observe(el));
  }

  /* ---------- Hero mouse parallax ---------- */
  function initHeroParallax() {
    const stage = document.querySelector('.hero-stage');
    if (!stage || prefersReducedMotion) return;
    stage.addEventListener('mousemove', (e) => {
      const rect = stage.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width - 0.5;
      const y = (e.clientY - rect.top) / rect.height - 0.5;
      stage.querySelectorAll('.hero-parallax').forEach(layer => {
        const depth = parseFloat(layer.dataset.wowDepth || 1);
        layer.style.transform =
          `translate3d(${-x * 26 * depth}px, ${-y * 18 * depth}px, 0) rotateY(${x * 7 * depth}deg) rotateX(${-y * 7 * depth}deg)`;
      });
    });
    stage.addEventListener('mouseleave', () => {
      stage.querySelectorAll('.hero-parallax').forEach(l => l.style.transform = '');
    });
  }

  /* ---------- Ripple on buttons ---------- */
  function initButtonRipples() {
    document.addEventListener('click', (e) => {
      const btn = e.target.closest('.btn');
      if (!btn) return;
      const rect = btn.getBoundingClientRect();
      btn.style.setProperty('--wow-mx', `${e.clientX - rect.left}px`);
      btn.style.setProperty('--wow-my', `${e.clientY - rect.top}px`);
      const before = getComputedStyle(btn, '::before');
      void before;
      btn.classList.remove('wow-ripple');
      void btn.offsetWidth;
      btn.classList.add('wow-ripple');
      setTimeout(() => btn.classList.remove('wow-ripple'), 650);
    });
  }

  /* ---------- Compare system (localStorage + drawer bar) ---------- */
  const COMPARE_KEY = 'wow-compare-ids';
  const COMPARE_MAX = 3;

  window.__wowCompare = {
    load() {
      try { return JSON.parse(localStorage.getItem(COMPARE_KEY)) || []; } catch (e) { return []; }
    },
    save(ids) {
      localStorage.setItem(COMPARE_KEY, JSON.stringify(ids));
      renderCompareBar();
    },
    toggle(id, name, image) {
      let ids = this.load();
      let metas = this.loadMeta();
      if (ids.includes(Number(id))) {
        ids = ids.filter(i => i !== Number(id));
        delete metas[id];
        showToast('از لیست مقایسه حذف شد', 'info');
      } else {
        if (ids.length >= COMPARE_MAX) {
          showToast(`حداکثر ${COMPARE_MAX} محصول قابل مقایسه است`, 'danger');
          return;
        }
        ids.push(Number(id));
        metas[id] = { name, image };
        showToast('به لیست مقایسه افزوده شد', 'success');
      }
      this.save(ids);
      this.saveMeta(metas);
      syncCompareButtons();
    },
    loadMeta() {
      try { return JSON.parse(localStorage.getItem(COMPARE_KEY + '-meta')) || {}; } catch (e) { return {}; }
    },
    saveMeta(m) { localStorage.setItem(COMPARE_KEY + '-meta', JSON.stringify(m)); },
    url() {
      const ids = this.load();
      return ids.length ? `/shop/compare/?ids=${ids.join(',')}` : '#';
    },
    clear() {
      localStorage.removeItem(COMPARE_KEY);
      localStorage.removeItem(COMPARE_KEY + '-meta');
      renderCompareBar();
      syncCompareButtons();
    }
  };

  function compareBtnHtml(product) {
    const ids = window.__wowCompare.load();
    const active = ids.includes(Number(product.id)) ? ' wow-compare-active' : '';
    return `<button class="product-card-action-btn wow-compare-btn${active}" title="${document.documentElement.lang === 'en' ? 'Compare' : 'مقایسه'}" data-compare-id="${product.id}" data-compare-name="${product.name}" data-compare-img="${product.img}">⚖️</button>`;
  }

  function injectCompareButtons() {
    document.querySelectorAll('.product-card').forEach(card => {
      const link = card.querySelector('a[href]');
      const img = card.querySelector('img');
      const actions = card.querySelector('.product-card-actions');
      if (!link || !actions || actions.querySelector('.wow-compare-btn')) return;
      const m = link.getAttribute('href').match(/\/products?\/([\w-]+)\/?/);
      const id = card.dataset.productId || (m ? card.dataset.productId : null) || actions.dataset.productId;
      let pid = card.dataset.productId;
      if (!pid) {
        const onclickSrc = actions.innerHTML.match(/addToCart\((\d+)\)/);
        pid = onclickSrc ? onclickSrc[1] : null;
      }
      if (!pid) return;
      const name = card.querySelector('.product-card-title')?.textContent.trim() || '';
      const tmp = document.createElement('div');
      tmp.innerHTML = compareBtnHtml({ id: pid, name, img: img ? img.src : '' });
      actions.appendChild(tmp.firstElementChild);
    });
  }

  function syncCompareButtons() {
    const ids = window.__wowCompare.load();
    document.querySelectorAll('.wow-compare-btn').forEach(btn => {
      btn.classList.toggle('wow-compare-active', ids.includes(Number(btn.dataset.compareId)));
    });
  }

  function renderCompareBar() {
    let bar = document.getElementById('compare-bar');
    const ids = window.__wowCompare.load();
    const metas = window.__wowCompare.loadMeta();

    if (!ids.length) {
      if (bar) bar.classList.remove('compare-bar-visible');
      return;
    }
    if (!bar) {
      bar = document.createElement('div');
      bar.id = 'compare-bar';
      document.body.appendChild(bar);
    }
    bar.innerHTML = `
      <span style="font-weight:800; font-size:0.85rem;">⚖️ ${document.documentElement.lang === 'en' ? 'Compare' : 'مقایسه'}</span>
      <div class="compare-bar-items">
        ${ids.map(id => `
          <div class="compare-thumb">
            <img src="${(metas[id] && metas[id].image) || ''}" alt="">
            <button onclick="wowRemoveCompare(${id})" title="${document.documentElement.lang === 'en' ? 'Remove' : 'حذف'}">✕</button>
          </div>`).join('')}
      </div>
      <a href="${window.__wowCompare.url()}" class="btn btn-primary btn-sm btn-shimmer" style="white-space:nowrap;">${document.documentElement.lang === 'en' ? `Compare ${ids.length} items` : `مقایسه ${ids.length} کالا`}</a>
      <button onclick="__wowCompare.clear()" style="background:none;border:none;color:#94a3b8;cursor:pointer;font-size:0.78rem;">${document.documentElement.lang === 'en' ? 'Clear' : 'پاک کردن'}</button>
    `;
    requestAnimationFrame(() => bar.classList.add('compare-bar-visible'));
  }

  window.wowRemoveCompare = function (id) {
    const ids = window.__wowCompare.load().filter(i => i !== Number(id));
    const metas = window.__wowCompare.loadMeta();
    delete metas[id];
    localStorage.setItem(COMPARE_KEY, JSON.stringify(ids));
    window.__wowCompare.saveMeta(metas);
    renderCompareBar();
    syncCompareButtons();
  };

  function initCompareSystem() {
    injectCompareButtons();
    renderCompareBar();
    document.addEventListener('click', (e) => {
      const btn = e.target.closest('.wow-compare-btn');
      if (!btn) return;
      e.preventDefault();
      e.stopPropagation();
      window.__wowCompare.toggle(btn.dataset.compareId, btn.dataset.compareName, btn.dataset.compareImg);
    });
    new MutationObserver(injectCompareButtons).observe(document.body, { childList: true, subtree: true });
  }

  /* ---------- Fly-to-cart + sparkles on add ---------- */
  function patchAddToCartFX() {
    const original = window.addToCart;
    if (!original) return;
    window.addToCart = function (productId, variantId, qty) {
      flyEffect(productId);
      return original.apply(this, arguments);
    };
  }

  function flyEffect(productId) {
    if (prefersReducedMotion) return;
    const card = [...document.querySelectorAll('.product-card')].find(c =>
      c.innerHTML.includes(`addToCart(${productId}`));
    const img = card ? card.querySelector('img') : null;
    const target = document.querySelector('.toggle-cart-drawer') || document.querySelector('.cart-badge-count');
    if (!img || !target) { sparkleAt(target || document.body); return; }

    const from = img.getBoundingClientRect();
    const to = target.getBoundingClientRect();
    const flyer = document.createElement('img');
    flyer.src = img.src;
    flyer.className = 'wow-fly-item';
    flyer.style.left = from.left + from.width / 2 - 28 + 'px';
    flyer.style.top = from.top + from.height / 2 - 28 + 'px';
    document.body.appendChild(flyer);

    requestAnimationFrame(() => {
      flyer.style.left = to.left + to.width / 2 - 10 + 'px';
      flyer.style.top = to.top + to.height / 2 - 10 + 'px';
      flyer.style.width = '20px';
      flyer.style.height = '20px';
      flyer.style.opacity = '0.4';
    });
    setTimeout(() => {
      flyer.remove();
      target.classList.add('wow-cart-bump');
      sparkleAt(target);
      setTimeout(() => target.classList.remove('wow-cart-bump'), 600);
    }, 760);
  }

  function sparkleAt(el) {
    const rect = el.getBoundingClientRect();
    const colors = ['#FFC24B', '#FF8A5C', '#f6c352', '#e11d48', '#FFB224'];
    for (let i = 0; i < 12; i++) {
      const s = document.createElement('span');
      s.className = 'wow-sparkle';
      const angle = (Math.PI * 2 * i) / 12;
      s.style.setProperty('--wow-sx', `${Math.cos(angle) * (50 + Math.random() * 40)}px`);
      s.style.setProperty('--wow-sy', `${Math.sin(angle) * (50 + Math.random() * 40)}px`);
      s.style.background = colors[i % colors.length];
      s.style.left = rect.left + rect.width / 2 + 'px';
      s.style.top = rect.top + rect.height / 2 + 'px';
      document.body.appendChild(s);
      setTimeout(() => s.remove(), 750);
    }
  }

  /* ---------- Cinematic page transitions (same-origin links) ---------- */
  function initPageTransitions() {
    if (window.__EM_NO_OVERLAY_TRANSITION) return;
    if (prefersReducedMotion) return;
    let overlay = document.getElementById('wow-page-transition');
    if (!overlay) {
      overlay = document.createElement('div');
      overlay.id = 'wow-page-transition';
      document.body.appendChild(overlay);
    }
    document.addEventListener('click', (e) => {
      const a = e.target.closest('a');
      if (!a) return;
      const href = a.getAttribute('href');
      if (!href || href.startsWith('#') || a.target === '_blank' || a.hasAttribute('download') ||
          a.dataset.noTransition !== undefined ||
          href.includes('.pdf') || a.classList.contains('wow-compare-btn')) return;
      const url = new URL(a.href, location.href);
      if (url.origin !== location.origin) return;
      if (url.pathname === location.pathname && url.search === location.search) return;
      // only for navigation-style links (not form submits, filters with onchange etc.)
      if (url.pathname.startsWith('/cart/api') || url.pathname.startsWith('/api/')) return;
      e.preventDefault();
      overlay.classList.add('wow-transition-active');
      setTimeout(() => { location.href = a.href; }, 260);
    });
    window.addEventListener('pageshow', (e) => {
      if (e.persisted) overlay.classList.remove('wow-transition-active');
    });
  }

  /* ---------- Dual-range price slider sync ---------- */
  function initRangeSliders() {
    document.querySelectorAll('[data-wow-range-wrap]').forEach(wrap => {
      const min = wrap.querySelector('[data-wow-range="min"]');
      const max = wrap.querySelector('[data-wow-range="max"]');
      const fill = wrap.querySelector('.wow-range-fill');
      const out = wrap.parentElement.querySelector('[data-wow-range-out]');
      const numberInputs = document.querySelectorAll(wrap.dataset.wowTargets || '[data-wow-sync-price]');
      const sync = () => {
        let lo = Math.min(+min.value, +max.value);
        let hi = Math.max(+min.value, +max.value);
        const span = +max.max - +min.min || 1;
        if (fill) {
          fill.style.insetInlineStart = ((lo - min.min) / span * 100) + '%';
          fill.style.width = ((hi - lo) / span * 100) + '%';
        }
        if (out) out.textContent = `${lo.toLocaleString('fa-IR')} – ${hi.toLocaleString('fa-IR')} تومان`;
        numberInputs.forEach(inp => {
          if (inp.name === 'min_price') inp.value = lo;
          if (inp.name === 'max_price') inp.value = hi;
        });
      };
      [min, max].forEach(r => r.addEventListener('input', sync));
      sync();
    });
  }

  /* ---------- Order success confetti ---------- */
  function launchConfetti() {
    const colors = ['#FFC24B', '#FF8A5C', '#FFB224', '#f6c352', '#E8C474', '#FFD98A'];
    for (let i = 0; i < 80; i++) {
      const c = document.createElement('span');
      c.className = 'wow-confetti';
      c.style.left = Math.random() * 100 + 'vw';
      c.style.background = colors[i % colors.length];
      c.style.animationDuration = (2.5 + Math.random() * 2.5) + 's';
      c.style.animationDelay = Math.random() * 1.2 + 's';
      c.style.borderRadius = Math.random() > 0.5 ? '50%' : '2px';
      document.body.appendChild(c);
      setTimeout(() => c.remove(), 7000);
    }
  }
})();
