# راهنمای استقرار در محیط واقعی (Production Deployment Guide)

این راهنما مراحل گام‌به‌گام استقرار پروژه روی یک سرور مجازی (Ubuntu 22.04 / 24.04 LTS) با وب‌سرور **Nginx**، سرور برنامه‌کاربردی **Gunicorn**، پایگاه داده **PostgreSQL** و پروتکل امن **HTTPS (Let's Encrypt)** را شرح می‌دهد.

---

## ۱. آماده‌سازی سرور و بسته‌های سیستمی

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib nginx curl git certbot python3-certbot-nginx
```

---

## ۲. راه‌اندازی پایگاه داده PostgreSQL

```bash
sudo -u postgres psql
```

دستورات زیر را در کنسول PostgreSQL اجرا نمایید:

```sql
CREATE DATABASE shop_db;
CREATE USER shop_user WITH PASSWORD 'StrongDatabasePasswordHere!';
ALTER ROLE shop_user SET client_encoding TO 'utf8';
ALTER ROLE shop_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE shop_user SET timezone TO 'Asia/Tehran';
GRANT ALL PRIVILEGES ON DATABASE shop_db TO shop_user;
\q
```

---

## ۳. کلون مخزن و تنظیم محیط پایتون

```bash
cd /var/www
sudo git clone <repository_url> shop
sudo chown -R www-data:www-data /var/www/shop
cd /var/www/shop

# ایجاد محیط مجازی
sudo -u www-data python3 -m venv .venv
sudo -u www-data .venv/bin/pip install --upgrade pip
sudo -u www-data .venv/bin/pip install -r requirements.txt
sudo -u www-data .venv/bin/pip install gunicorn psycopg[binary]
```

---

## ۴. پیکربندی متغیرهای محیطی (.env)

فایل `/var/www/shop/.env` را بسازید:

```ini
SECRET_KEY=generate-a-super-long-secure-random-key-here-min-50-characters
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

DATABASE_URL=postgres://shop_user:StrongDatabasePasswordHere!@localhost:5432/shop_db

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.yourprovider.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=support@yourdomain.com
EMAIL_HOST_PASSWORD=YourSmtpPassword
DEFAULT_FROM_EMAIL=Shop Support <support@yourdomain.com>

PAYMENT_GATEWAY_DEFAULT=zarinpal
ZARINPAL_MERCHANT_ID=your-actual-zarinpal-merchant-id
ZARINPAL_SANDBOX=False
```

دسترسی فایل را امن نمایید:
```bash
sudo chmod 600 /var/www/shop/.env
sudo chown www-data:www-data /var/www/shop/.env
```

---

## ۵. اجرای مایگریشن‌ها و جمع‌آوری فایل‌های استاتیک

```bash
sudo -u www-data .venv/bin/python manage.py migrate
sudo -u www-data .venv/bin/python manage.py collectstatic --noinput
sudo -u www-data .venv/bin/python manage.py createsuperuser
```

---

## ۶. تنظیم سرویس Systemd برای Gunicorn

فایل سرویس `/etc/systemd/system/shop.service` را ایجاد کنید:

```ini
[Unit]
Description=Gunicorn daemon for Modern E-Commerce Platform
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/shop
ExecStart=/var/www/shop/.venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/shop.sock \
          shop_project.wsgi:application

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

فعال‌سازی سرویس:
```bash
sudo systemctl daemon-reload
sudo systemctl start shop
sudo systemctl enable shop
sudo systemctl status shop
```

---

## ۷. پیکربندی وب‌سرور Nginx

فایل `/etc/nginx/sites-available/shop` را ایجاد کنید:

```nginx
server {
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 20M;

    # Static files caching
    location /static/ {
        alias /var/www/shop/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    # Uploaded media files
    location /media/ {
        alias /var/www/shop/media/;
        expires 7d;
        add_header Cache-Control "public";
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/shop.sock;
    }
}
```

فعال‌سازی کانفیگ:
```bash
sudo ln -s /etc/nginx/sites-available/shop /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## ۸. فعال‌سازی گواهی امنیتی SSL (HTTPS)

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

تست تمدید خودکار گواهی:
```bash
sudo certbot renew --dry-run
```

پروژه اکنون به صورت کامل، امن و با پروتکل HTTPS روی سرور پروداکشن عملیاتی است.
