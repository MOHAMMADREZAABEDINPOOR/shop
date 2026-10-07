/* ==========================================================================
   AVANGARD PREMIUM JS — micro-interactions layer (runs after app.js & wow.js)
   PDP 3D gallery • cursor aura • magnetic CTAs • spotlight zoom • lift parallax
   ========================================================================== */
(function () {
  'use strict';

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine = window.matchMedia('(pointer: fine)').matches;

  /* ---------- 1. Cursor aura ---------- */
  if (false) { /* EMBER: custom cursor disabled */
    var cur = document.createElement('div');
    cur.className = 'ag-cursor';
    document.body.appendChild(cur);
    var shown = false;
    document.addEventListener('mousemove', function (e) {
      cur.style.left = e.clientX + 'px';
      cur.style.top = e.clientY + 'px';
      if (!shown) { cur.classList.add('ag-cursor-active'); shown = true; }
    });
    document.addEventListener('mouseover', function (e) {
      var hot = e.target.closest('a, button, .product-card, input, select, textarea');
      cur.classList.toggle('ag-cursor-hot', !!hot);
    });
    document.addEventListener('mouseleave', function () { cur.classList.remove('ag-cursor-active'); shown = false; });
  }

  /* ---------- 2. Magnetic CTA buttons ---------- */
  if (fine && !reduced) {
    var magnets = document.querySelectorAll('.btn-primary.btn-lg, .btn-shimmer, .hero-cta, .wow-stats-strip, .btn-accent.btn-lg');
    document.addEventListener('mousemove', function (e) {
      magnets.forEach(function (el) {
        if (el._agMagnetMove === undefined) { el._agMagnetMove = 0; }
        var r = el.getBoundingClientRect();
        var dx = e.clientX - (r.left + r.width / 2);
        var dy = e.clientY - (r.top + r.height / 2);
        var dist = Math.hypot(dx, dy);
        var range = 110;
        if (dist < range && !el.matches(':active')) {
          var pull = (1 - dist / range) * 7;
          el.style.transform = 'translate(' + (dx / dist * pull) + 'px,' + (dy / dist * pull) + 'px)';
        } else if (dist >= range + 40) {
          el.style.transform = '';
        }
      });
    }, { passive: true });
  }

  /* ---------- 3. PDP premium gallery: thumbs + spotlight zoom ---------- */
  var stage = document.querySelector('.pdp-stage');
  var mainImg = document.getElementById('main-product-img');

  function bindThumbActive() {
    document.querySelectorAll('.pdp-thumb').forEach(function (btn) {
      if (btn.dataset.agBound) return;
      btn.dataset.agBound = '1';
      btn.addEventListener('click', function () {
        var url = btn.dataset.full;
        if (!url || !mainImg) return;
        document.querySelectorAll('.pdp-thumb').forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');
        mainImg.classList.add('pdp-swapping');
        setTimeout(function () {
          mainImg.src = url;
          mainImg.classList.remove('pdp-swapping');
        }, 220);
      });
    });
  }
  bindThumbActive();
  new MutationObserver(bindThumbActive).observe(document.body, { childList: true, subtree: true });

  if (stage && mainImg && fine && !reduced) {
    stage.addEventListener('mousemove', function (e) {
      var r = stage.getBoundingClientRect();
      var px = (e.clientX - r.left) / r.width;
      var py = (e.clientY - r.top) / r.height;
      // gentle 3D perspective follow
      var rx = (0.5 - py) * 10;
      var ry = (px - 0.5) * 14;
      mainImg.style.transform = 'perspective(900px) rotateX(' + rx + 'deg) rotateY(' + ry + 'deg) scale(' + (stage.classList.contains('pdp-zoomed') ? 1.9 : 1.04) + ')';
    });
    stage.addEventListener('mouseleave', function () {
      if (!stage.classList.contains('pdp-zoomed')) mainImg.style.transform = '';
    });
    stage.addEventListener('click', function (e) {
      if (e.target.closest('button')) return;
      stage.classList.toggle('pdp-zoomed');
      if (!stage.classList.contains('pdp-zoomed')) mainImg.style.transform = '';
    });
  }

  /* ---------- 4. Card lift parallax on mouse (whole-grid subtle) ---------- */
  if (false) { /* EMBER: lift disabled, wow tilt owns transform */
    document.querySelectorAll('.product-card').forEach(function (card) {
      card.addEventListener('mousemove', function (e) {
        var r = card.getBoundingClientRect();
        var px = (e.clientX - r.left) / r.width - 0.5;
        var py = (e.clientY - r.top) / r.height - 0.5;
        card.style.transform = 'translateY(-10px) scale(1.015) perspective(800px) rotateX(' + (-py * 5) + 'deg) rotateY(' + (px * 7) + 'deg)';
      });
      card.addEventListener('mouseleave', function () { card.style.transform = ''; });
    });
  }

  /* ---------- 4b. نور نقطه‌ای دنبال‌کننده ماوس روی کارت‌ها ---------- */
  if (fine && !reduced) {
    var agRaf = null;
    document.addEventListener('mousemove', function (e) {
      if (agRaf) return;
      agRaf = requestAnimationFrame(function () {
        agRaf = null;
        var card = e.target.closest && e.target.closest('.card, .kpi-card, .trust-item');
        document.querySelectorAll('.ag-card-lit').forEach(function (c) {
          if (c !== card) c.classList.remove('ag-card-lit');
        });
        if (!card) return;
        var r = card.getBoundingClientRect();
        card.style.setProperty('--ag-mx', ((e.clientX - r.left) / r.width * 100) + '%');
        card.style.setProperty('--ag-my', ((e.clientY - r.top) / r.height * 100) + '%');
        card.classList.add('ag-card-lit');
      });
    }, { passive: true });
  }

  /* ---------- 5. Reveal-on-scroll for any .card outside wow-stagger ---------- */
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          en.target.style.opacity = '1';
          en.target.style.transform = 'none';
          io.unobserve(en.target);
        }
      });
    }, { threshold: 0.08 });
    document.querySelectorAll('main .container > .card, main .container > section').forEach(function (el, i) {
      if (reduced) return;
      if (el.style.opacity === '1' || el.classList.contains('wow-stagger')) return;
      el.style.opacity = '0';
      el.style.transform = 'translateY(26px)';
      el.style.transition = 'opacity 0.7s cubic-bezier(0.16,1,0.3,1) ' + (i % 3) * 0.08 + 's, transform 0.7s cubic-bezier(0.16,1,0.3,1) ' + (i % 3) * 0.08 + 's';
      io.observe(el);
    });
  }

  /* ---------- 6. Announcement bar: rotate messages ---------- */
  var announce = document.querySelector('.site-announce [data-ag-rotate]');
  if (announce) {
    var msgs = JSON.parse(announce.dataset.agRotate);
    var idx = 0;
    setInterval(function () {
      idx = (idx + 1) % msgs.length;
      announce.style.opacity = 0;
      setTimeout(function () {
        announce.textContent = msgs[idx];
        announce.style.opacity = 1;
      }, 300);
    }, 4200);
    announce.style.transition = 'opacity 0.3s ease';
  }
})();
