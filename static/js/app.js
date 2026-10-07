/**
 * Master Application JavaScript for Modern E-Commerce Platform
 */

document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initLiveSearch();
  initMiniCartDrawer();
  initFormDoubleSubmitProtection();
  initVariantSwitcher();
  initCookieBanner();
  initBackToTop();
  initRevealOnScroll();
  initCountdowns();
});

/* 1. Theme Management (Dark/Light Mode) */
function initTheme() {
  const toggleBtn = document.getElementById('theme-toggle-btn');
  const qp = new URLSearchParams(window.location.search).get('theme');
  const fromQuery = (qp === 'dark' || qp === 'light');
  const savedTheme = fromQuery ? qp : (localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'));

  setTheme(savedTheme, !fromQuery);

  if (toggleBtn) {
    toggleBtn.addEventListener('click', (e) => {
      const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      if (typeof window.__emThemeToggle === 'function') {
        window.__emThemeToggle(newTheme, e);
      } else {
        setTheme(newTheme);
      }
    });
  }
}

function setTheme(theme, persist = true) {
  document.documentElement.setAttribute('data-theme', theme);
  if (persist !== false) { localStorage.setItem('theme', theme); }

  const iconSun = document.getElementById('theme-icon-sun');
  const iconMoon = document.getElementById('theme-icon-moon');
  if (iconSun && iconMoon) {
    if (theme === 'dark') {
      iconSun.style.display = 'block';
      iconMoon.style.display = 'none';
    } else {
      iconSun.style.display = 'none';
      iconMoon.style.display = 'block';
    }
  }
}

/* 2. CSRF Token Helper */
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const CSRF_TOKEN = getCookie('csrftoken') || (document.querySelector('[name=csrfmiddlewaretoken]')?.value);

/* 3. Toast Notifications */
const TOAST_ICONS = {
  success: '<svg class="icon icon-lg" style="color:var(--success)"><use href="#i-check-circle"/></svg>',
  danger: '<svg class="icon icon-lg" style="color:var(--danger)"><use href="#i-alert"/></svg>',
  info: '<svg class="icon icon-lg" style="color:var(--primary)"><use href="#i-info"/></svg>'
};
function showToast(message, type = 'info', duration = 4000) {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;

  const icon = type === 'success' ? TOAST_ICONS.success : (type === 'danger' || type === 'error') ? TOAST_ICONS.danger : TOAST_ICONS.info;
  toast.innerHTML = `
    <span style="font-weight: bold; font-size: 1.1rem;">${icon}</span>
    <div style="flex: 1; font-size: 0.92rem;">${message}</div>
    <button style="background:none;border:none;cursor:pointer;color:var(--text-muted);font-size:1rem;" onclick="this.parentElement.remove()">✕</button>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

/* 4. Live Search with Debounce */
function initLiveSearch() {
  const searchInput = document.getElementById('main-search-input');
  const dropdown = document.getElementById('search-dropdown');
  if (!searchInput || !dropdown) return;

  let debounceTimer = null;

  searchInput.addEventListener('input', (e) => {
    const query = e.target.value.trim();
    clearTimeout(debounceTimer);

    if (query.length < 1) {
      dropdown.classList.remove('active');
      dropdown.innerHTML = '';
      return;
    }

    debounceTimer = setTimeout(() => {
      dropdown.innerHTML = `
        <div style="padding: 0.75rem 1rem; display: flex; flex-direction: column; gap: 0.6rem;">
          <div class="skeleton" style="height: 44px;"></div>
          <div class="skeleton" style="height: 44px;"></div>
          <div class="skeleton" style="height: 44px;"></div>
        </div>
      `;
      dropdown.classList.add('active');
      const isEn = document.documentElement.lang === 'en' || document.documentElement.getAttribute('dir') === 'ltr';

      fetch(`/api/search/?q=${encodeURIComponent(query)}`)
        .then(res => res.json())
        .then(data => {
          if (data.results && data.results.length > 0) {
            const currencyDefault = isEn ? 'Toman' : 'تومان';
            const viewAllText = isEn ? 'View all search results →' : 'مشاهده همه نتایج جستجو ←';
            dropdown.innerHTML = data.results.map(item => `
              <a href="${item.url}" class="search-result-item">
                <img src="${item.image}" alt="${item.name}" class="search-result-img" loading="lazy">
                <div style="flex: 1;">
                  <div style="font-weight: 600; font-size: 0.9rem; color: var(--text-primary);">${item.name}</div>
                  <div style="font-size: 0.8rem; color: var(--text-muted);">${item.category}</div>
                </div>
                <div style="font-weight: 700; color: var(--primary); font-size: 0.95rem; white-space: nowrap;">${item.price} ${item.currency || currencyDefault}</div>
              </a>
            `).join('') + `
              <div style="padding: 0.5rem 1rem; text-align: center; background-color: var(--bg-subtle);">
                <a href="/shop/?q=${encodeURIComponent(query)}" style="font-size: 0.85rem; color: var(--primary); font-weight: 600;">${viewAllText}</a>
              </div>
            `;
            dropdown.classList.add('active');
          } else {
            const emptyMsg = isEn ? `No products found for "${query}".` : `کالایی با عبارت «${query}» یافت نشد.`;
            dropdown.innerHTML = `
              <div style="padding: 1.5rem; text-align: center; color: var(--text-muted); font-size: 0.9rem; direction: ${isEn ? 'ltr' : 'rtl'};">
                ${emptyMsg}
              </div>
            `;
            dropdown.classList.add('active');
          }
        })
        .catch(err => console.error('Search error:', err));
    }, 280);
  });

  document.addEventListener('click', (e) => {
    if (!searchInput.contains(e.target) && !dropdown.contains(e.target)) {
      dropdown.classList.remove('active');
    }
  });
}

/* 5. Mini-Cart Drawer */
function initMiniCartDrawer() {
  const openButtons = document.querySelectorAll('.toggle-cart-drawer');
  const overlay = document.getElementById('cart-drawer-overlay');
  const closeBtn = document.getElementById('cart-drawer-close');

  if (!overlay) return;

  const openDrawer = () => {
    overlay.classList.add('active');
    loadMiniCartItems();
  };

  const closeDrawer = () => {
    overlay.classList.remove('active');
  };

  openButtons.forEach(btn => btn.addEventListener('click', (e) => {
    e.preventDefault();
    openDrawer();
  }));

  if (closeBtn) closeBtn.addEventListener('click', closeDrawer);
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) closeDrawer();
  });
}

function getAppLanguage() {
  const htmlLang = (document.documentElement.lang || '').toLowerCase();
  if (htmlLang.startsWith('en')) return 'en';
  const cookieMatch = document.cookie.match(/(?:^|;\s*)django_language=([^;]+)/);
  if (cookieMatch && cookieMatch[1].toLowerCase().startsWith('en')) return 'en';
  if (document.documentElement.dir === 'ltr') return 'en';
  return 'fa';
}

function loadMiniCartItems() {
  const container = document.getElementById('cart-drawer-items');
  const subtotalEl = document.getElementById('cart-drawer-subtotal');
  const badgeEl = document.getElementById('cart-drawer-badge');
  const checkoutBtn = document.getElementById('cart-drawer-checkout-btn');
  if (!container) return;

  const isEn = getAppLanguage() === 'en';
  const currency = isEn ? 'Toman' : 'تومان';

  container.innerHTML = `
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 3rem 1rem; color: var(--text-muted); gap: 0.75rem;">
      <div style="width: 28px; height: 28px; border: 3px solid var(--border); border-top-color: var(--primary); border-radius: 50%; animation: spin 0.8s linear infinite;"></div>
      <span style="font-size: 0.88rem;">${isEn ? 'Loading your cart...' : 'در حال بارگذاری سبد خرید...'}</span>
    </div>
  `;

  fetch('/cart/api/mini-cart/')
    .then(res => res.json())
    .then(data => {
      const cur = data.currency || currency;
      if (data.items && data.items.length > 0) {
        container.innerHTML = data.items.map(item => `
          <div class="mini-cart-item" data-item-id="${item.id}">
            <a href="${item.url || '#'}" class="mini-cart-thumb">
              <img src="${item.image || '/static/images/placeholder.svg'}" alt="${item.name}">
            </a>
            <div class="mini-cart-details">
              <a href="${item.url || '#'}" class="mini-cart-title">${item.name}</a>
              ${item.variant ? `<div class="mini-cart-variant">${item.variant}</div>` : ''}
              <div class="mini-cart-pricing">
                <div class="mini-cart-qty-ctrl">
                  <button type="button" class="mini-cart-qty-btn" onclick="updateCartQty(${item.id}, ${item.quantity - 1})" aria-label="Decrease">−</button>
                  <span class="mini-cart-qty-num">${item.quantity}</span>
                  <button type="button" class="mini-cart-qty-btn" onclick="updateCartQty(${item.id}, ${item.quantity + 1})" aria-label="Increase">+</button>
                </div>
                <div class="mini-cart-price">${item.total_price} <span class="mini-cart-currency">${cur}</span></div>
              </div>
            </div>
            <button type="button" class="mini-cart-remove-btn" onclick="removeCartItem(${item.id})" aria-label="${isEn ? 'Remove item' : 'حذف کالا'}" title="${isEn ? 'Remove' : 'حذف'}">
              <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2.2" fill="none"><path d="M18 6L6 18M6 6l12 12"/></svg>
            </button>
          </div>
        `).join('');

        if (subtotalEl) subtotalEl.textContent = `${data.subtotal} ${cur}`;
        if (badgeEl) {
          badgeEl.textContent = `${data.item_count} ${isEn ? 'items' : 'کالا'}`;
          badgeEl.style.display = 'inline-block';
        }
        if (checkoutBtn) {
          checkoutBtn.classList.remove('disabled');
          checkoutBtn.style.pointerEvents = '';
          checkoutBtn.style.opacity = '1';
        }
      } else {
        container.innerHTML = `
          <div class="empty-cart-state">
            <div class="empty-cart-icon-wrap">
              <svg class="empty-cart-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="9" cy="21" r="1"></circle>
                <circle cx="20" cy="21" r="1"></circle>
                <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
              </svg>
            </div>
            <h4 class="empty-cart-title">${isEn ? 'Your Cart is Empty' : 'سبد خرید شما خالی است'}</h4>
            <p class="empty-cart-subtitle">${isEn ? 'Looks like you have not added anything yet. Discover our latest technology and best deals!' : 'هنوز هیچ کالایی به سبد خریدتان اضافه نکرده‌اید. جدیدترین محصولات و تخفیف‌های ویژه ما را بررسی کنید.'}</p>
            <a href="/shop/" class="btn btn-primary empty-cart-btn" onclick="const ov = document.getElementById('cart-drawer-overlay'); if (ov) ov.classList.remove('active');">
              <svg class="icon" aria-hidden="true" style="width:1.1em;height:1.1em"><use href="#i-search"/></svg>
              ${isEn ? 'Start Shopping' : 'مشاهده فروشگاه و خرید'}
            </a>
          </div>
        `;
        if (subtotalEl) subtotalEl.textContent = isEn ? '0 Toman' : '۰ تومان';
        if (badgeEl) badgeEl.style.display = 'none';
        if (checkoutBtn) {
          checkoutBtn.classList.add('disabled');
          checkoutBtn.style.pointerEvents = 'none';
          checkoutBtn.style.opacity = '0.5';
        }
      }
      updateCartBadge(data.item_count);
    })
    .catch(() => {
      container.innerHTML = `
        <div style="text-align: center; padding: 2rem 1rem; color: var(--danger);">
          ${isEn ? 'Failed to load cart items.' : 'خطا در بارگذاری اطلاعات سبد خرید.'}
        </div>
      `;
    });
}

function updateCartBadge(count) {
  document.querySelectorAll('.cart-badge-count').forEach(el => {
    el.textContent = count;
    el.style.display = count > 0 ? 'flex' : 'none';
  });
}

/* 6. Global Cart Actions */
window.updateCartQty = function(itemId, newQty) {
  const isEn = getAppLanguage() === 'en';
  if (newQty < 1) {
    window.removeCartItem(itemId);
    return;
  }
  fetch(`/cart/api/update/${itemId}/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken') || ''
    },
    body: JSON.stringify({ quantity: newQty })
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === 'success') {
      loadMiniCartItems();
      updateCartBadge(data.cart_item_count);
    } else {
      showToast(data.message || (isEn ? 'Error updating quantity' : 'خطا در به‌روزرسانی تعداد'), 'danger');
    }
  })
  .catch(() => {
    showToast(isEn ? 'Network error. Please try again.' : 'خطای ارتباط با سرور. لطفاً دوباره تلاش کنید.', 'danger');
  });
};

window.addToCart = function(productId, variantId = null, quantity = 1) {
  const isEn = getAppLanguage() === 'en';
  fetch('/cart/api/add/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken') || ''
    },
    body: JSON.stringify({ product_id: productId, variant_id: variantId, quantity: quantity })
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === 'success') {
      showToast(data.message, 'success');
      updateCartBadge(data.cart_item_count);
      const overlay = document.getElementById('cart-drawer-overlay');
      if (overlay && !overlay.classList.contains('active')) {
        overlay.classList.add('active');
        loadMiniCartItems();
      }
    } else {
      showToast(data.message || (isEn ? 'Error adding to cart' : 'خطا در افزودن به سبد خرید'), 'danger');
    }
  })
  .catch(err => {
    showToast(isEn ? 'Network error. Please check your internet connection.' : 'خطای شبکه. لطفاً اتصال اینترنت خود را بررسی کنید.', 'danger');
  });
};

window.removeCartItem = function(itemId) {
  const isEn = getAppLanguage() === 'en';
  fetch(`/cart/api/remove/${itemId}/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCookie('csrftoken') || ''
    }
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === 'success') {
      showToast(data.message, 'info');
      loadMiniCartItems();
      // If we are on full cart page, refresh or update DOM
      const row = document.getElementById(`cart-row-${itemId}`);
      if (row) row.remove();
      const subtotalEl = document.getElementById('page-cart-subtotal');
      const grandTotalEl = document.getElementById('page-cart-grandtotal');
      const cur = data.currency || (isEn ? 'Toman' : 'تومان');
      if (subtotalEl) subtotalEl.textContent = `${data.subtotal} ${cur}`;
      if (grandTotalEl) grandTotalEl.textContent = `${data.grand_total} ${cur}`;
      if (data.cart_item_count === 0 && document.getElementById('cart-table')) {
        window.location.reload();
      }
    }
  })
  .catch(() => {
    showToast(isEn ? 'Network error removing item.' : 'خطای ارتباط در حذف کالا.', 'danger');
  });
};

/* 7. Wishlist Toggle */
window.toggleWishlist = function(productId, btnEl) {
  fetch(`/accounts/wishlist/toggle/${productId}/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCookie('csrftoken') || ''
    }
  })
  .then(res => {
    if (res.status === 401 || res.redirected) {
      window.location.href = '/accounts/login/';
      return;
    }
    return res.json();
  })
  .then(data => {
    if (!data) return;
    if (data.status === 'success') {
      showToast(data.message, data.is_in_wishlist ? 'success' : 'info');
      if (btnEl) {
        btnEl.classList.toggle('active', data.is_in_wishlist);
        const icon = btnEl.querySelector('.wishlist-icon');
        if (icon) {
          icon.style.fill = data.is_in_wishlist ? '#ef4444' : 'none';
          icon.style.stroke = data.is_in_wishlist ? '#ef4444' : 'currentColor';
        }
      }
    }
  })
  .catch(err => console.error(err));
};

/* 8. Double-Submit Form Protection */
function initFormDoubleSubmitProtection() {
  document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function() {
      const submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn && !submitBtn.disabled) {
        submitBtn.dataset.originalText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = 'در حال پردازش...';
        // Re-enable safety fallback after 10s
        setTimeout(() => {
          submitBtn.disabled = false;
          submitBtn.innerHTML = submitBtn.dataset.originalText || submitBtn.innerHTML;
        }, 10000);
      }
    });
  });
}

/* 9. Product Variant Switcher on Detail Page */function initVariantSwitcher() {
  const container = document.getElementById('variant-picker');
  const priceDisplay = document.getElementById('product-price-display');
  const stockDisplay = document.getElementById('product-stock-display');
  const hiddenInput = document.getElementById('selected-variant-id');

  if (!container || !window.PRODUCT_VARIANTS) return;

  const variants = window.PRODUCT_VARIANTS;

  container.addEventListener('change', (e) => {
    if (e.target.name === 'variant_choice') {
      const selectedId = parseInt(e.target.value);
      const variant = variants.find(v => v.id === selectedId);
      if (variant) {
        if (priceDisplay) priceDisplay.textContent = `${variant.price.toLocaleString('fa-IR')} تومان`;
        if (stockDisplay) {
          if (variant.is_in_stock) {
            stockDisplay.textContent = `موجود در انبار (${variant.stock} عدد)`;
            stockDisplay.className = 'badge badge-success';
          } else {
            stockDisplay.textContent = 'ناموجود در انبار';
            stockDisplay.className = 'badge badge-danger';
          }
        }
        if (hiddenInput) hiddenInput.value = variant.id;
      }
    }
  });
}

/* 10. Cookie consent banner */
function initCookieBanner() {
  try {
    if (localStorage.getItem('cookie-consent')) return;
  } catch (e) { return; }
  const banner = document.getElementById('cookie-banner');
  if (!banner) return;
  setTimeout(() => { banner.hidden = false; }, 1200);
}

function setCookieConsent(value) {
  try { localStorage.setItem('cookie-consent', value); } catch (e) {}
  const banner = document.getElementById('cookie-banner');
  if (banner) banner.hidden = true;
}
window.acceptCookies = function() { setCookieConsent('accepted'); };
window.declineCookies = function() { setCookieConsent('declined'); };

/* 11. Back to top */
function initBackToTop() {
  const btn = document.getElementById('back-to-top');
  if (!btn) return;
  window.addEventListener('scroll', () => {
    btn.classList.toggle('visible', window.scrollY > 600);
  }, { passive: true });
  btn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
}

/* 12. Reveal on scroll */
function initRevealOnScroll() {
  const els = document.querySelectorAll('.reveal');
  if (!els.length) return;
  if (!('IntersectionObserver' in window)) {
    els.forEach(el => el.classList.add('revealed'));
    return;
  }
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('revealed');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });
  els.forEach(el => observer.observe(el));
}

/* 13. Deal countdowns (data-countdown-minutes or data-countdown-to ISO) */
function initCountdowns() {
  document.querySelectorAll('[data-countdown-minutes]').forEach(el => {
    const totalSeconds = parseInt(el.dataset.countdownMinutes, 10) * 60 || 0;
    const endAt = Date.now() + totalSeconds;
    const target = el.querySelector('[data-countdown-value]') || el;
    const tick = () => {
      let remaining = Math.max(0, Math.floor((endAt - Date.now()) / 1000));
      const h = String(Math.floor(remaining / 3600)).padStart(2, '0');
      const m = String(Math.floor((remaining % 3600) / 60)).padStart(2, '0');
      const s = String(remaining % 60).padStart(2, '0');
      target.textContent = `${h}:${m}:${s}`;
    };
    tick();
    setInterval(tick, 1000);
  });
}
