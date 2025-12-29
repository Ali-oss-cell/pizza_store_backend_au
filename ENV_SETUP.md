# 🔐 Environment Variables Setup Guide

## Quick Setup

### On Your DigitalOcean Droplet:

```bash
# 1. Navigate to project directory
cd /var/www/pizza-store-backend

# 2. Copy the template
cp env.production.template .env

# 3. Edit the .env file
nano .env

# 4. Update these values:
#    - DJANGO_SECRET_KEY (generate new one)
#    - ALLOWED_HOSTS (your domain and IP)
#    - CORS_ALLOWED_ORIGINS (your frontend URL)
#    - CSRF_TRUSTED_ORIGINS (your domain)
```

---

## 📋 Environment Variables Reference

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DJANGO_SECRET_KEY` | Django secret key (generate new) | `django-insecure-...` |
| `DEBUG` | Debug mode (False in production) | `False` |
| `ALLOWED_HOSTS` | Comma-separated domains/IPs | `example.com,www.example.com,123.45.67.89` |
| `DB_NAME` | PostgreSQL database name | `defaultdb` |
| `DB_USER` | PostgreSQL username | `doadmin` |
| `DB_PASSWORD` | PostgreSQL password | `your-password` |
| `DB_HOST` | PostgreSQL host | `private-db-...ondigitalocean.com` |
| `DB_PORT` | PostgreSQL port | `25060` |
| `DB_SSLMODE` | SSL mode (require for DO) | `require` |
| `CORS_ALLOWED_ORIGINS` | Frontend URLs (comma-separated) | `https://example.com` |
| `CSRF_TRUSTED_ORIGINS` | Trusted domains (comma-separated) | `https://example.com` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECURE_SSL_REDIRECT` | Redirect HTTP to HTTPS | `True` |
| `SECURE_HSTS_SECONDS` | HSTS duration | `31536000` |

---

## 🔑 Generate Secret Key

```bash
cd /var/www/pizza-store-backend
source venv/bin/activate
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and paste it as `DJANGO_SECRET_KEY` in your `.env` file.

---

## ✅ Your Current Database Configuration

Your DigitalOcean managed PostgreSQL is already configured in the template:

```
DB_NAME=defaultdb
DB_USER=doadmin
DB_PASSWORD=AVNS_1GHB72K7lqTFT0MS372
DB_HOST=private-db-postgresql-syd1-42296-do-user-26523274-0.e.db.ondigitalocean.com
DB_PORT=25060
DB_SSLMODE=require
```

**Note**: These credentials are already in the template. Just copy `env.production.template` to `.env` and update the other values.

---

## 🔒 Security Notes

1. **Never commit `.env` to git** - It's already in `.gitignore`
2. **Generate a new SECRET_KEY** - Don't use the default
3. **Keep credentials secure** - Only accessible on server
4. **Use strong passwords** - For database and admin accounts

---

## 🧪 Test Database Connection

After setting up `.env`, test the connection:

```bash
cd /var/www/pizza-store-backend/pizza_store
source ../venv/bin/activate
python manage.py dbshell
```

If it connects successfully, you'll see the PostgreSQL prompt. Type `\q` to exit.

---

## 📝 Example .env File

```bash
# Security
DJANGO_SECRET_KEY=django-insecure-your-actual-secret-key-here
DEBUG=False
ALLOWED_HOSTS=pizzastore.com,www.pizzastore.com,123.45.67.89

# Database (DigitalOcean Managed PostgreSQL)
DB_NAME=defaultdb
DB_USER=doadmin
DB_PASSWORD=AVNS_1GHB72K7lqTFT0MS372
DB_HOST=private-db-postgresql-syd1-42296-do-user-26523274-0.e.db.ondigitalocean.com
DB_PORT=25060
DB_SSLMODE=require

# CORS
CORS_ALLOWED_ORIGINS=https://pizzastore.com,https://www.pizzastore.com
CSRF_TRUSTED_ORIGINS=https://pizzastore.com,https://www.pizzastore.com

# SSL
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
```

---

## 🚀 After Setup

1. **Test connection**: `python manage.py dbshell`
2. **Run migrations**: `python manage.py migrate`
3. **Collect static**: `python manage.py collectstatic --noinput`
4. **Create superuser**: `python manage.py createsuperuser`
5. **Restart Gunicorn**: `sudo systemctl restart pizza-store`

---

**Last Updated**: 2024-01-15

