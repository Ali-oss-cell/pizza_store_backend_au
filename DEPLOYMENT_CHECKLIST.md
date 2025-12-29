# 🚀 Production Deployment Checklist - DigitalOcean Droplet

## ✅ Pre-Deployment Checks

### 1. Security Settings ⚠️ **CRITICAL**

- [ ] **SECRET_KEY**: Must be changed from default insecure key
  - Generate new key: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
  - Store in environment variable: `DJANGO_SECRET_KEY`
  
- [ ] **DEBUG**: Must be `False` in production
  - Set via environment variable: `DEBUG=False`
  
- [ ] **ALLOWED_HOSTS**: Add your domain/IP
  - Example: `ALLOWED_HOSTS=['yourdomain.com', 'www.yourdomain.com', 'your.droplet.ip']`
  
- [ ] **Security Headers** (Add to settings):
  - `SECURE_SSL_REDIRECT = True` (if using HTTPS)
  - `SESSION_COOKIE_SECURE = True` (if using HTTPS)
  - `CSRF_COOKIE_SECURE = True` (if using HTTPS)
  - `SECURE_HSTS_SECONDS = 31536000` (if using HTTPS)
  - `SECURE_HSTS_INCLUDE_SUBDOMAINS = True`
  - `SECURE_HSTS_PRELOAD = True`

### 2. Database Configuration

- [ ] **Current**: Using SQLite (not recommended for production)
- [ ] **Recommended**: PostgreSQL for production
  - Install: `sudo apt-get install postgresql postgresql-contrib`
  - Create database and user
  - Update `DATABASES` in settings.py
  - Install: `pip install psycopg2-binary` (add to requirements.txt)

### 3. Static Files & Media

- [ ] **STATIC_ROOT**: Set to collect static files
  - Add: `STATIC_ROOT = BASE_DIR / 'staticfiles'`
  
- [ ] **Collect Static Files**:
  ```bash
  python manage.py collectstatic --noinput
  ```
  
- [ ] **Media Files**: Configure for production
  - Use cloud storage (AWS S3, DigitalOcean Spaces) OR
  - Serve via nginx/apache

### 4. Environment Variables

- [ ] Create `.env` file (DO NOT commit to git)
- [ ] Set required variables:
  ```
  DJANGO_SECRET_KEY=your-secret-key-here
  DEBUG=False
  ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
  DATABASE_URL=postgresql://user:pass@localhost/dbname
  ```

### 5. CORS Configuration

- [ ] Update `CORS_ALLOWED_ORIGINS` with production frontend URL
- [ ] Remove localhost origins (or keep for admin access)
- [ ] Update `CSRF_TRUSTED_ORIGINS` with production URLs

### 6. Web Server Configuration

- [ ] **Choose Web Server**:
  - Option 1: Gunicorn + Nginx (Recommended)
  - Option 2: Gunicorn + Apache
  - Option 3: uWSGI + Nginx

- [ ] **Install Gunicorn**:
  ```bash
  pip install gunicorn
  ```
  Add to `requirements.txt`

- [ ] **Create Gunicorn Service**:
  - Create systemd service file
  - Configure auto-restart

### 7. SSL/HTTPS Setup

- [ ] **Install Certbot** (Let's Encrypt):
  ```bash
  sudo apt-get install certbot python3-certbot-nginx
  ```

- [ ] **Get SSL Certificate**:
  ```bash
  sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
  ```

### 8. Firewall Configuration

- [ ] **Configure UFW**:
  ```bash
  sudo ufw allow 22    # SSH
  sudo ufw allow 80     # HTTP
  sudo ufw allow 443    # HTTPS
  sudo ufw enable
  ```

### 9. Database Migrations

- [ ] **Run Migrations**:
  ```bash
  python manage.py migrate
  ```

- [ ] **Create Superuser**:
  ```bash
  python manage.py createsuperuser
  ```

### 10. Dependencies

- [ ] **Update requirements.txt** (if needed):
  - Add `gunicorn`
  - Add `psycopg2-binary` (if using PostgreSQL)
  - Add `python-dotenv` (for .env support)

- [ ] **Install Dependencies**:
  ```bash
  pip install -r requirements.txt
  ```

### 11. Logging Configuration

- [ ] **Configure Logging** in settings.py
- [ ] Set up log rotation
- [ ] Configure error email notifications (optional)

### 12. Backup Strategy

- [ ] **Database Backups**:
  - Set up automated daily backups
  - Store backups off-server

- [ ] **Media Files Backups**:
  - Backup uploaded images regularly

### 13. Monitoring

- [ ] **Set up monitoring** (optional):
  - Server monitoring (CPU, RAM, Disk)
  - Application monitoring (Sentry, etc.)
  - Uptime monitoring

### 14. Testing

- [ ] **Test Production Setup**:
  - Test GraphQL endpoint
  - Test admin panel
  - Test cart functionality
  - Test order creation
  - Test file uploads

---

## 📋 Quick Deployment Steps

### 1. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3-pip python3-venv postgresql postgresql-contrib nginx -y

# Install Certbot (for SSL)
sudo apt install certbot python3-certbot-nginx -y
```

### 2. Application Setup
```bash
# Clone repository
git clone <your-repo-url>
cd pizza-store-backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn psycopg2-binary python-dotenv

# Create .env file
nano .env
# Add: DJANGO_SECRET_KEY, DEBUG=False, ALLOWED_HOSTS, DATABASE_URL

# Run migrations
cd pizza_store
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 3. Gunicorn Setup
```bash
# Test Gunicorn
gunicorn pizza_store.wsgi:application --bind 0.0.0.0:8000

# Create systemd service
sudo nano /etc/systemd/system/pizza-store.service
```

### 4. Nginx Configuration
```bash
# Create nginx config
sudo nano /etc/nginx/sites-available/pizza-store

# Enable site
sudo ln -s /etc/nginx/sites-available/pizza-store /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5. SSL Setup
```bash
# Get SSL certificate
sudo certbot --nginx -d yourdomain.com
```

---

## 🔧 Required Settings Updates

### Update `settings.py` to use environment variables:

```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Security
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'fallback-key-change-in-production')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')

# Database (PostgreSQL example)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'pizza_store'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Security settings (if using HTTPS)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# CORS - Update with production frontend URL
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]

CSRF_TRUSTED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]
```

---

## 📝 Files to Create

### 1. `.env` file (DO NOT COMMIT)
```
DJANGO_SECRET_KEY=your-generated-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your.droplet.ip
DB_NAME=pizza_store
DB_USER=pizza_user
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432
```

### 2. Gunicorn Systemd Service (`/etc/systemd/system/pizza-store.service`)
```ini
[Unit]
Description=Pizza Store Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/pizza-store-backend/pizza_store
ExecStart=/path/to/pizza-store-backend/venv/bin/gunicorn \
    --access-logfile - \
    --workers 3 \
    --bind unix:/run/pizza-store.sock \
    pizza_store.wsgi:application

[Install]
WantedBy=multi-user.target
```

### 3. Nginx Configuration (`/etc/nginx/sites-available/pizza-store`)
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://unix:/run/pizza-store.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/pizza-store-backend/pizza_store/staticfiles/;
    }

    location /media/ {
        alias /path/to/pizza-store-backend/pizza_store/media/;
    }
}
```

---

## ⚠️ Security Checklist

- [ ] SECRET_KEY is strong and unique
- [ ] DEBUG = False
- [ ] ALLOWED_HOSTS configured correctly
- [ ] Database password is strong
- [ ] SSH keys configured (disable password auth)
- [ ] Firewall configured (UFW)
- [ ] SSL/HTTPS enabled
- [ ] Security headers configured
- [ ] .env file not in git
- [ ] db.sqlite3 not in git
- [ ] Admin panel protected (change default admin URL if needed)

---

## 🧪 Post-Deployment Testing

- [ ] GraphQL endpoint accessible
- [ ] Admin panel accessible
- [ ] Static files loading
- [ ] Media files loading
- [ ] Cart functionality works
- [ ] Order creation works
- [ ] File uploads work
- [ ] SSL certificate valid
- [ ] CORS working with frontend
- [ ] Database connections stable

---

## 📞 Troubleshooting

### Common Issues:

1. **502 Bad Gateway**: Check Gunicorn service status
2. **Static files 404**: Run `collectstatic` and check nginx config
3. **Database connection error**: Check database credentials and PostgreSQL status
4. **CORS errors**: Verify CORS_ALLOWED_ORIGINS matches frontend URL
5. **CSRF errors**: Check CSRF_TRUSTED_ORIGINS

### Useful Commands:

```bash
# Check Gunicorn status
sudo systemctl status pizza-store

# Check Nginx status
sudo systemctl status nginx

# View Gunicorn logs
sudo journalctl -u pizza-store -f

# View Nginx logs
sudo tail -f /var/log/nginx/error.log

# Test Nginx config
sudo nginx -t

# Restart services
sudo systemctl restart pizza-store
sudo systemctl restart nginx
```

---

## 📅 Maintenance Tasks

- [ ] Set up automated database backups
- [ ] Monitor disk space
- [ ] Update dependencies regularly
- [ ] Review logs weekly
- [ ] Test backups monthly
- [ ] Update SSL certificate (auto-renewal with certbot)

---

**Last Updated**: 2024-01-15  
**Status**: Ready for deployment after completing checklist

