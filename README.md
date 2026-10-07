<div align="center">

<img src="assets/readme/hero.gif" width="1200" alt="COMMERCE · DJANGO: a shopping cart with products and a checkout receipt" />

**[English](README.md) · [فارسی](README.fa.md)**

</div>

# 🛒 COMMERCE · DJANGO

A Django ecommerce application with product variants, guest/customer carts, inventory-aware order creation, a local payment sandbox and an operations dashboard.

[GitHub](https://github.com/MOHAMMADREZAABEDINPOOR/shop) · [PIMX / Profile](https://github.com/MOHAMMADREZAABEDINPOOR) · [Static artwork](assets/readme/hero.png)

| At a glance | Details |
|:---|:---|
| 🛒 Experience | Web application / browser experience |
| 🧰 Built with | `Django>=5.1,<6.2` · `Pillow>=10.0.0` · `cryptography>=42.0.0` |
| 🌐 Documentation | [English](README.md) · [فارسی](README.fa.md) |

[✨ Features](#features) · [🚀 Getting started](#getting-started) · [⚙️ Configuration](#configuration) · [🌍 Deployment](#deployment)

---

<a id="features"></a>

## ✨ Features

| Area | Included capability |
|:---|:---|
| 🛍️ Commerce | Catalog filtering, live search and product variants |
| 🛍️ Commerce | Guest cart merge, addresses and multi-step checkout |
| 🛍️ Commerce | Transactional order/payment handling and inventory locks |
| 🌐 Experience | Reviews, dashboard and Persian storefront styling |

<a id="stack"></a>

## 🧰 Stack

| Tool | Version / source |
|---|---|
| Django>=5.1,<6.2 | `requirements.txt` |
| Pillow>=10.0.0 | `requirements.txt` |
| cryptography>=42.0.0 | `requirements.txt` |

<a id="getting-started"></a>

## 🚀 Getting started

Python 3; a desktop/Tk installation for Tkinter or turtle examples. Tkinter is provided by the Python installation, not pip. Legacy dependencies may need a compatible Python version.

```bash
git clone https://github.com/MOHAMMADREZAABEDINPOOR/shop.git
cd shop

python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1; macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
# Copy .env.example to .env
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

<a id="configuration"></a>

## ⚙️ Configuration

These names are found in the example configuration or source; not all are required. Check their defaults/usage in those files and supply secrets only in your local or hosting environment.

| Name | Role |
|---|---|
| `ALLOWED_HOSTS` | Application setting; inspect its definition |
| `ANALYTICS_ID` | Application setting; inspect its definition |
| `DATABASE_URL` | Credential/connection setting; keep private |
| `DATA_ENCRYPTION_KEY` | Credential/connection setting; keep private |
| `DEBUG` | Application setting; inspect its definition |
| `DEFAULT_FROM_EMAIL` | Application setting; inspect its definition |
| `EMAIL_BACKEND` | Application setting; inspect its definition |
| `EMAIL_HOST` | Application setting; inspect its definition |
| `EMAIL_HOST_PASSWORD` | Credential/connection setting; keep private |
| `EMAIL_HOST_USER` | Application setting; inspect its definition |
| `EMAIL_PORT` | Application setting; inspect its definition |
| `EMAIL_USE_TLS` | Application setting; inspect its definition |
| `PAYMENT_GATEWAY_DEFAULT` | Application setting; inspect its definition |
| `PAYMENT_PUBLIC_KEY` | Credential/connection setting; keep private |
| `PAYMENT_SECRET` | Credential/connection setting; keep private |
| `REDIS_URL` | Application setting; inspect its definition |
| `SECRET_KEY` | Credential/connection setting; keep private |
| `ZARINPAL_MERCHANT_ID` | Application setting; inspect its definition |
| `ZARINPAL_SANDBOX` | Application setting; inspect its definition |

<a id="usage"></a>

## 🎯 Usage

Copy .env.example to .env, run migrations and seed_data on a fresh development database. Open /shop/, add a product and complete /orders/checkout/. Use /dashboard/ for operations and /admin/ for Django administration.

<a id="project-structure"></a>

## 🗂️ Project structure

| Path | Role |
|---|---|
| [`accounts/`](accounts/) | Account application |
| [`assets/`](assets/) | Brand/media/README assets |
| [`cart/`](cart/) | Cart workflows |
| [`catalog/`](catalog/) | Product catalog |
| [`dashboard/`](dashboard/) | Operations dashboard |
| [`docs/`](docs/) | Supporting documentation |
| [`orders/`](orders/) | Order workflows |
| [`payments/`](payments/) | Payment workflows |
| [`static/`](static/) | Static web assets |
| [`templates/`](templates/) | Server-rendered templates |
| [`manage.py`](manage.py) | Project entry/configuration file |
| [`populate_reviews_variants.py`](populate_reviews_variants.py) | Project entry/configuration file |
| [`setup_visuals.py`](setup_visuals.py) | Project entry/configuration file |
| [`test_dashboard_e2e.py`](test_dashboard_e2e.py) | Project entry/configuration file |
| [`upgrade_visuals.py`](upgrade_visuals.py) | Project entry/configuration file |

<a id="commands-and-checks"></a>

## 🧪 Commands and checks

```bash
python manage.py check
python manage.py test
```

<a id="deployment"></a>

## 🌍 Deployment

Configure production secrets, HTTPS, an independent database and allowed hosts. PHP hosting must use public/ as document root; Django needs static-file and WSGI/ASGI configuration. Development servers are for local use.

<a id="limitations"></a>

## 📌 Limitations

The payment gateway is a local sandbox, not a live banking integration. SQLite does not reproduce PostgreSQL row-lock behavior. Seeded accounts are development-only; local databases and media uploads are excluded.

<a id="troubleshooting"></a>

## 🛠️ Troubleshooting

- Missing packages: install dependencies using the project’s package manager.
- API/network failure: check the configured origin, provider and hosting bindings.
- Old assets: rebuild when a build script exists, then clear the browser cache.

<a id="contributing"></a>

## 🤝 Contributing

Create a focused branch, verify the affected behavior and explain the change clearly. Keep private data, build outputs and local databases out of commits.

Supporting guides:

- [DEPLOYMENT.md](DEPLOYMENT.md)
- [SECURITY.md](SECURITY.md)

<a id="license"></a>

## 📄 License

No repository-level license file is included in this snapshot. Public visibility alone does not grant reuse rights; contact the repository owner for terms.

---

Part of **PIMX** · Documentation in English and Persian.

---

<div align="center">

🛒 **COMMERCE · DJANGO** · [English](README.md) · [فارسی](README.fa.md)

</div>
