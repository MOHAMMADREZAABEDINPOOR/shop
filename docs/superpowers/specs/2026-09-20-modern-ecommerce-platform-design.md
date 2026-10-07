# Architectural Specification: Modern Production-Ready E-Commerce Platform

**Date:** 2026-09-20  
**Status:** Approved by User  
**Author:** Senior Full-Stack Engineer / Software Architect  

---

## 1. Executive Summary & Vision

This project specifies the design and implementation of an end-to-end, high-performance, secure, and fully responsive e-commerce marketplace platform. Inspired by the best UX standards of Amazon and Digikala, the platform features an original, custom-crafted visual identity and design system built with Django, Django Templates, and modern Vanilla CSS/JS.

Every feature is backed by database persistence and server-side validation. There are no mockups, fake buttons, or dummy endpoints. The application is production-ready, featuring full Persian (RTL) support with LTR extensibility, ergonomic Dark and Light themes, atomic inventory management with race-condition prevention, a modular payment gateway architecture with an interactive local sandbox, and an administrative dashboard with site settings CMS.

---

## 2. Technical Stack & Foundation

* **Language & Runtime:** Python 3.15 / Django 6.x
* **Database:** SQLite (local development with atomic transactions and WAL enabled) / PostgreSQL (production-ready via environment configuration)
* **Frontend:** Django Templates + Modern Vanilla CSS (Design Tokens, Flexbox/Grid, CSS Custom Properties) + Vanilla JavaScript (Fetch API, DOM manipulation, custom interactive components)
* **Styling & Theme:** Mobile-first, RTL-first (with CSS logical properties), Dark and Light mode toggle with persistent preferences (localStorage + session), zero external npm build dependency friction.
* **Architecture:** Modular Django Domain Apps (`core`, `accounts`, `catalog`, `cart`, `orders`, `payments`, `reviews`, `dashboard`)
* **Background Tasks / Workers:** Architecture ready for Celery/Redis; sync/in-memory fallback for local development.
* **Security Standards:** OWASP Top 10 compliance, CSRF protection, secure session cookies, server-side rate limiting, strict IDOR/BOLA authorization checks, parameterized queries, and security headers.

---

## 3. Modular Application Architecture

### 3.1. `core`
* **Purpose:** Foundational models, dynamic site settings, homepage CMS components (banners, hero sliders, featured sections), static pages, contact form, newsletter subscriptions, custom error handling (400, 403, 404, 500), and global template tags/context processors.
* **Key Models:**
  * `SiteSetting`: Single-instance model storing store name, phone, email, address, working hours, social links, free shipping threshold, default currency, and legal terms.
  * `Banner`: Hero slides, promotional banners (grid positions: top hero, middle dual, side banners), link URL, order, active toggle.
  * `ContactMessage`: Name, email, phone, subject, message, status (New, Read, Replied), timestamps.
  * `NewsletterSubscription`: Email, is_active, subscribed_at.

### 3.2. `accounts`
* **Purpose:** User authentication, identity, role-based authorization (Customer, Staff, Admin, Super Admin), profiles, multi-address book, wishlist, recently viewed products, session management, and email verification.
* **Key Models:**
  * `User`: Custom model extending `AbstractBaseUser` and `PermissionsMixin`. Primary identifier is `email` (or phone). Fields: `email`, `phone_number`, `first_name`, `last_name`, `role` (CUSTOMER, STAFF, ADMIN, SUPERADMIN), `is_active`, `is_verified`, `date_joined`.
  * `UserProfile`: `avatar`, `national_code`, `birth_date`, `notify_sms`, `notify_email`.
  * `Address`: Multiple addresses per user. `user`, `title` (Home, Work, etc.), `receiver_name`, `receiver_phone`, `province`, `city`, `postal_code`, `address_line`, `is_default`.
  * `Wishlist`: `user`, `product`, `created_at` (`UniqueConstraint(user, product)`).
  * `RecentlyViewed`: `user` (or session_key for guests), `product`, `viewed_at`.

### 3.3. `catalog`
* **Purpose:** Multi-level categories, brands, variable products, attributes, specifications, image galleries, live search, and multi-facet filtering.
* **Key Models:**
  * `Category`: Self-referential tree structure (`parent` foreign key). Fields: `name`, `slug` (unique), `icon`, `image`, `description`, `is_active`, `order`, `meta_title`, `meta_description`.
  * `Brand`: `name`, `slug` (unique), `logo`, `description`, `is_active`.
  * `Product`: `name`, `slug` (unique), `sku` (unique), `barcode`, `category`, `brand`, `short_description`, `description`, `base_price` (Decimal), `sale_price` (Decimal, optional), `discount_percent`, `stock`, `is_available`, `is_active`, `is_featured`, `is_bestseller`, `is_new_arrival`, `weight`, `dimensions`, `meta_title`, `meta_description`.
  * `ProductImage`: `product`, `image`, `alt_text`, `is_feature` (primary thumbnail), `order`.
  * `ProductAttribute`: `name` (e.g. Color, Storage, RAM, Material).
  * `ProductAttributeValue`: `attribute`, `value` (e.g. 128GB, Midnight Black).
  * `ProductVariant`: Supports independent pricing and stock per variant (e.g., iPhone 128GB Black vs 256GB Gold). Fields: `product`, `name`, `sku` (unique), `price_override` (Decimal, optional), `stock`, `is_active`, `attributes` (ManyToMany to `ProductAttributeValue`).

### 3.4. `cart`
* **Purpose:** Persistent shopping cart for authenticated users and cookie/session-based cart for guests. Automatic merge upon login. Server-side authoritative pricing and stock recalculations.
* **Key Models:**
  * `Cart`: `user` (nullable), `session_key` (nullable), `created_at`, `updated_at`.
  * `CartItem`: `cart`, `product`, `variant` (nullable), `quantity`, `UniqueConstraint(cart, product, variant)`.
* **Methods:**
  * `get_subtotal()`, `get_total_discount()`, `get_shipping_cost()`, `get_grand_total()`, `merge_guest_cart(user)`.

### 3.5. `orders`
* **Purpose:** Multi-step checkout pipeline, coupon engine, order lifecycle, address snapshotting, product snapshotting, and atomic stock decrement.
* **Key Models:**
  * `Coupon`: `code` (unique, uppercase), `discount_type` (PERCENTAGE, FIXED), `discount_value`, `min_order_amount`, `max_discount_amount`, `start_date`, `end_date`, `usage_limit`, `usage_per_user`, `is_active`.
  * `CouponUsage`: `coupon`, `user`, `order`, `used_at`.
  * `Order`:
    * `order_number`: Unique string (e.g. `ORD-20260920-83921`).
    * `user`: `ForeignKey(User)`.
    * Address Snapshot: `shipping_name`, `shipping_phone`, `shipping_province`, `shipping_city`, `shipping_postal_code`, `shipping_address_line`.
    * Pricing Snapshot: `subtotal`, `discount_amount`, `shipping_cost`, `tax_amount`, `grand_total`.
    * Status: `status` (PENDING, AWAITING_PAYMENT, PAID, PROCESSING, SHIPPED, DELIVERED, CANCELLED, RETURNED, REFUNDED).
    * `shipping_method`: Express, Standard, Same-Day.
    * `tracking_code`, `customer_notes`, `admin_notes`, `created_at`, `updated_at`.
  * `OrderItem`:
    * `order`: `ForeignKey(Order, related_name='items')`.
    * `product`: `ForeignKey(Product, on_delete=SET_NULL, null=True)`.
    * `variant`: `ForeignKey(ProductVariant, on_delete=SET_NULL, null=True)`.
    * Snapshot Fields: `product_name`, `variant_name`, `unit_price`, `quantity`, `total_price`.

### 3.6. `payments`
* **Purpose:** Modular payment gateway engine, transaction record keeping, interactive local sandbox bank gateway, and idempotent server-to-server verification.
* **Key Models:**
  * `Payment`: `order`, `transaction_id` (UUID), `gateway` (Sandbox, Zarinpal, etc.), `amount`, `status` (PENDING, SUCCESSFUL, FAILED, CANCELLED), `tracking_number`, `card_pan_masked`, `error_message`, `ip_address`, `idempotency_key`, `created_at`, `verified_at`.
* **Interface & Driver:**
  * `BasePaymentGateway` abstract class defining `initiate_payment(order)` and `verify_payment(request, transaction_id)`.
  * `SandboxPaymentGateway` implementing full interactive bank gateway UI with simulated card entry, CVV2, dynamic OTP timer, and callback response options (Success, Invalid Card, Insufficient Funds, Cancelled).

### 3.7. `reviews`
* **Purpose:** Product ratings, customer reviews, verified buyer badge enforcement, and administrative moderation.
* **Key Models:**
  * `Review`: `product`, `user`, `rating` (1 to 5), `title`, `comment`, `is_verified_buyer` (automatically evaluated if user has a PAID order containing the product), `is_approved`, `created_at`.

### 3.8. `dashboard`
* **Purpose:**
  1. **Customer Account Portal:** Profile management, order history, tracking status, address book CRUD, wishlist, reviews.
  2. **Admin/Staff Operations Hub:** Executive overview with revenue KPIs, order status workflow (Pending -> Paid -> Shipped), inventory stock alerts (Low Stock, Out of Stock), coupon management, and contact message management.

---

## 4. Critical Flows & Concurrency Controls

### 4.1. Concurrency & Race Condition Prevention in Checkout
* When the user submits checkout, Django executes within `transaction.atomic()`.
* Every product and variant item in the cart is locked using `select_for_update()`.
* The system checks real-time available stock against requested quantities.
* If any item is out of stock or insufficient, the transaction rolls back cleanly and returns a descriptive error toast to the customer.
* If sufficient, stock is decremented, the `Order` and `OrderItem` snapshots are created, and the `Cart` is cleared or marked processed.
* If payment fails or is cancelled, stock is restored automatically.

### 4.2. Zero-Trust Server-Side Pricing & Calculations
* Cart item prices, discounts, coupons, shipping rates, and taxes are strictly calculated in Python code from the database.
* Client-side requests cannot override, alter, or pass prices.

### 4.3. Payment Idempotency & Verification
* The payment callback verifies transaction state via `Payment.objects.select_for_update().get(transaction_id=...)`.
* If the payment is already marked `SUCCESSFUL`, subsequent callbacks do not re-execute order status changes or re-send emails.
* Payment verification relies strictly on server-side logic and gateway signatures, never purely on URL query params like `?success=true`.

---

## 5. UI/UX Design System Specifications

### 5.1. Design Tokens & Palette
* **Light Mode:**
  * `--bg-main`: `#f8fafc` (Slate 50)
  * `--bg-surface`: `#ffffff`
  * `--bg-subtle`: `#f1f5f9` (Slate 100)
  * `--border-color`: `#e2e8f0` (Slate 200)
  * `--text-primary`: `#0f172a` (Slate 900)
  * `--text-secondary`: `#64748b` (Slate 500)
  * `--primary`: `#2563eb` (Royal Blue)
  * `--primary-hover`: `#1d4ed8`
  * `--accent`: `#f97316` (Vibrant Coral / Orange)
  * `--accent-hover`: `#ea580c`
  * `--success`: `#10b981`
  * `--danger`: `#ef4444`
* **Dark Mode:**
  * `--bg-main`: `#0b0f19` (Deep slate night)
  * `--bg-surface`: `#151c2e`
  * `--bg-subtle`: `#1e293b`
  * `--border-color`: `#243048`
  * `--text-primary`: `#f8fafc`
  * `--text-secondary`: `#94a3b8`
  * `--primary`: `#3b82f6`
  * `--primary-hover`: `#60a5fa`
  * `--accent`: `#fb923c`
  * `--accent-hover`: `#f97316`
  * `--success`: `#34d399`
  * `--danger`: `#f87171`
* **Typography:**
  * Clean, highly readable typography optimized for Persian (Vazirmatn / System font fallback) with proper text-rendering, antialiasing, and tabular numerals for pricing.
* **Layout & Direction:**
  * `dir="rtl"` standard for Persian. All spacing uses CSS Logical Properties (`padding-inline`, `margin-inline`, `inset-inline-start`) for clean alignment and future LTR support.
* **Interactive UI Elements:**
  * Floating Toast Notification system for notifications (success, error, warning, info).
  * Off-canvas Mini-Cart drawer.
  * Live search with debounce and drop-down recommendations.
  * Interactive Product Variant switcher (dynamically updating stock and price).
  * Double-submit prevention on all forms with button spinner feedback.
  * Sticky mobile bottom navigation & Sticky Product CTA.

---

## 6. Security Hardening Strategy

1. **Authorization & IDOR Protection:**
   * Ownership checks on all address, order, wishlist, and profile views: `filter(user=request.user)`.
2. **Mass Assignment Prevention:**
   * Whitelisted form fields in Django `ModelForm` definitions; sensitive attributes (`role`, `is_staff`, `is_active`, `status`) strictly managed server-side.
3. **Brute Force & Rate Limiting:**
   * In-memory / cache-backed rate limiting on Login, Register, Password Reset, and Checkout endpoints.
4. **Data Sanitization & XSS Prevention:**
   * Django template auto-escaping enabled; any rich text sanitized.
5. **Secure Cookies & HTTPS Readiness:**
   * `SESSION_COOKIE_HTTPONLY = True`, `CSRF_COOKIE_HTTPONLY = False` (for secure AJAX token transmission), secure headers (`X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy`).
6. **Error Handling:**
   * Production `DEBUG = False` mode configured; custom error templates for 400, 403, 404, and 500 without leaking stack traces.

---

## 7. SEO & Performance Architecture

* **Structured Data:** JSON-LD Schema.org for `Product`, `BreadcrumbList`, and `Organization`.
* **Dynamic Meta Tags:** Unique titles, meta descriptions, canonical URLs, and Open Graph tags on every product, category, and static page.
* **Dynamic Sitemap & robots.txt:** Built-in `sitemap.xml` listing products, categories, and public static pages; `robots.txt` disallowing private routes (cart, checkout, account, admin).
* **N+1 Query Elimination:** Extensive use of `select_related()` and `prefetch_related()` across catalog, cart, and order views.
* **Pagination:** Standard 12-24 items per page on catalog, orders, and reviews.

---

## 8. Seed Data & Developer Tooling

* Command: `python manage.py seed_data`
* Populates:
  * 1 Super Admin (`admin@shop.local`), 1 Staff (`staff@shop.local`), 2 Customers (`customer1@shop.local`, `customer2@shop.local`).
  * 3 Top-level Categories with Subcategories (Digital & Electronics, Home & Kitchen, Fashion & Apparel).
  * 6 Popular Brands (Apple, Samsung, Sony, Philips, Nike, Bosch).
  * 15+ Rich Products with real specifications, multiple images, single and multi-variant combinations (colors, storage capacities), ratings, and reviews.
  * 3 Active Promotional Coupons (e.g. `WELCOME10`, `DIGI20`, `SUPER50`).
  * Hero sliders and promotional banner cards.
  * Initial Site Settings (store details, contact information, shipping policies).

---

## 9. Automated Verification & Quality Assurance

* **Account & Authentication Tests:** Registration, login, password reset request, email verification token verification, permission enforcement.
* **Catalog & Filter Tests:** Slug routing, category hierarchy, faceted filter queries, search keyword matching.
* **Cart & Merge Tests:** Adding/updating/removing items, subtotal calculation, guest session cart merging into user cart upon login.
* **Checkout & Inventory Tests:** Race condition simulation, `select_for_update()` validation, out-of-stock blocking, coupon expiration and usage limits.
* **Payment & Idempotency Tests:** Sandbox payment initiation, callback verification, duplicate callback handling, inventory deduction, and cancellation inventory rollback.
* **Security & IDOR Tests:** Unauthorized order access, cross-user address modification attempt, mass assignment injection attempt.
