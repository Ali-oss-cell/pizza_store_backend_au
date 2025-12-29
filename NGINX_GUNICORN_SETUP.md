# 🚀 Nginx + Gunicorn Setup Guide

Complete step-by-step guide for deploying your Pizza Store backend with Nginx and Gunicorn on DigitalOcean.

---

## 📋 Prerequisites

- Ubuntu/Debian server (DigitalOcean Droplet)
- Root or sudo access
- Domain name pointed to your server IP (optional, but recommended)
- SSH access to your server

---

## Step 1: Server Preparation

### Update System
```bash
sudo apt update
sudo apt upgrade -y
```

### Install Required Packages
```bash
sudo apt install python3-pip python3-venv postgresql postgresql-contrib nginx git -y
```

---

## Step 2: Deploy Application

### Option A: Clone from Git
```bash
cd /var/www
sudo git clone <your-repo-url> pizza-store-backend
sudo chown -R $USER:$USER pizza-store-backend
cd pizza-store-backend
```

### Option B: Upload Files
```bash
# Create directory
sudo mkdir -p /var/www/pizza-store-backend
sudo chown -R $USER:$USER /var/www/pizza-store-backend

# Upload your files (using scp, rsync, or FTP)
# Then:
cd /var/www/pizza-store-backend
```

---

## Step 3: Python Environment Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Step 4: Database Setup (PostgreSQL)

### Create Database and User
```bash
sudo -u postgres psql
```

In PostgreSQL prompt:
```sql
CREATE DATABASE pizza_store;
CREATE USER pizza_user WITH PASSWORD 'your-strong-password-here';
ALTER ROLE pizza_user SET client_encoding TO 'utf8';
ALTER ROLE pizza_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE pizza_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE pizza_store TO pizza_user;
\q
```

---

## Step 5: Environment Configuration

### Create .env File
```bash
cd /var/www/pizza-store-backend
nano .env
```

Add these variables (update with your values):
```bash
# Generate secret key: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
DJANGO_SECRET_KEY=your-generated-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your.server.ip
DB_NAME=pizza_store
DB_USER=pizza_user
DB_PASSWORD=your-strong-password-here
DB_HOST=localhost
DB_PORT=5432
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

**Important**: Replace:
- `your-generated-secret-key-here` with a generated secret key
- `yourdomain.com` with your actual domain
- `your.server.ip` with your droplet IP
- `your-strong-password-here` with your database password

### Generate Secret Key
```bash
cd /var/www/pizza-store-backend
source venv/bin/activate
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
# Copy the output and paste it as DJANGO_SECRET_KEY in .env
```

---

## Step 6: Django Setup

```bash
cd /var/www/pizza-store-backend/pizza_store
source ../venv/bin/activate

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser
```

---

## Step 7: Configure Gunicorn

### Test Gunicorn Manually
```bash
cd /var/www/pizza-store-backend/pizza_store
source ../venv/bin/activate
gunicorn pizza_store.wsgi:application --bind 0.0.0.0:8000
```

Visit `http://your-server-ip:8000/graphql/` to test. Press `Ctrl+C` to stop.

### Create Systemd Service

Copy the service file:
```bash
sudo cp /var/www/pizza-store-backend/gunicorn.service /etc/systemd/system/pizza-store.service
```

**IMPORTANT**: Edit the service file to match your paths:
```bash
sudo nano /etc/systemd/system/pizza-store.service
```

Update these lines if your paths are different:
- `WorkingDirectory=/var/www/pizza-store-backend/pizza_store`
- `Environment="PATH=/var/www/pizza-store-backend/venv/bin"`
- `ExecStart=/var/www/pizza-store-backend/venv/bin/gunicorn`

### Start and Enable Service
```bash
# Reload systemd
sudo systemctl daemon-reload

# Start service
sudo systemctl start pizza-store

# Enable on boot
sudo systemctl enable pizza-store

# Check status
sudo systemctl status pizza-store
```

### View Logs
```bash
# View logs
sudo journalctl -u pizza-store -f

# View last 50 lines
sudo journalctl -u pizza-store -n 50
```

---

## Step 8: Configure Nginx

### Copy Nginx Configuration
```bash
sudo cp /var/www/pizza-store-backend/nginx-pizza-store.conf /etc/nginx/sites-available/pizza-store
```

### Edit Configuration
```bash
sudo nano /etc/nginx/sites-available/pizza-store
```

**Update**:
- `server_name yourdomain.com www.yourdomain.com;` → Your actual domain
- All paths: `/var/www/pizza-store-backend/` → Your actual path

### Enable Site
```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/pizza-store /etc/nginx/sites-enabled/

# Remove default site (optional)
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t
```

### Start Nginx
```bash
# Restart Nginx
sudo systemctl restart nginx

# Enable on boot
sudo systemctl enable nginx

# Check status
sudo systemctl status nginx
```

---

## Step 9: Set File Permissions

```bash
# Set ownership
sudo chown -R www-data:www-data /var/www/pizza-store-backend/pizza_store/staticfiles
sudo chown -R www-data:www-data /var/www/pizza-store-backend/pizza_store/media

# Set permissions
sudo chmod -R 755 /var/www/pizza-store-backend
sudo chmod -R 775 /var/www/pizza-store-backend/pizza_store/media
```

---

## Step 10: Firewall Configuration

```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP
sudo ufw allow 80/tcp

# Allow HTTPS
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

---

## Step 11: SSL Setup (Let's Encrypt)

### Install Certbot
```bash
sudo apt install certbot python3-certbot-nginx -y
```

### Get SSL Certificate
```bash
# Replace with your domain
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

Follow the prompts:
- Enter your email
- Agree to terms
- Choose whether to redirect HTTP to HTTPS (recommended: Yes)

### Auto-Renewal
Certbot sets up auto-renewal automatically. Test it:
```bash
sudo certbot renew --dry-run
```

### Update Nginx Config for HTTPS

After SSL setup, Certbot will update your Nginx config. You can also manually uncomment the HTTPS server block in `/etc/nginx/sites-available/pizza-store` and update the SSL paths.

---

## Step 12: Update .env for HTTPS

After SSL is set up, update your `.env` file:
```bash
nano /var/www/pizza-store-backend/.env
```

Ensure:
- `CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com`
- `CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com`

Then restart Gunicorn:
```bash
sudo systemctl restart pizza-store
```

---

## ✅ Testing

### Test GraphQL Endpoint
```bash
curl http://yourdomain.com/graphql/
# Or visit in browser: http://yourdomain.com/graphql/
```

### Test Admin Panel
Visit: `https://yourdomain.com/admin/`

### Test Static Files
Visit: `https://yourdomain.com/static/` (should show directory or 404, not 500)

### Test Media Files
Visit: `https://yourdomain.com/media/` (if you have media files)

---

## 🔧 Useful Commands

### Gunicorn
```bash
# Restart service
sudo systemctl restart pizza-store

# Stop service
sudo systemctl stop pizza-store

# Start service
sudo systemctl start pizza-store

# View logs
sudo journalctl -u pizza-store -f
```

### Nginx
```bash
# Restart
sudo systemctl restart nginx

# Reload (no downtime)
sudo systemctl reload nginx

# Test config
sudo nginx -t

# View error logs
sudo tail -f /var/log/nginx/error.log

# View access logs
sudo tail -f /var/log/nginx/access.log
```

### Django
```bash
cd /var/www/pizza-store-backend/pizza_store
source ../venv/bin/activate

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser

# Django shell
python manage.py shell
```

---

## 🐛 Troubleshooting

### 502 Bad Gateway
- Check Gunicorn is running: `sudo systemctl status pizza-store`
- Check Gunicorn logs: `sudo journalctl -u pizza-store -n 50`
- Verify socket file exists: `ls -la /run/pizza-store.sock`
- Check file permissions

### Static Files 404
- Run: `python manage.py collectstatic --noinput`
- Check Nginx config path: `/var/www/pizza-store-backend/pizza_store/staticfiles/`
- Check file permissions: `sudo chown -R www-data:www-data staticfiles/`

### Database Connection Error
- Check PostgreSQL is running: `sudo systemctl status postgresql`
- Verify database credentials in `.env`
- Test connection: `psql -U pizza_user -d pizza_store -h localhost`

### Permission Denied
- Check ownership: `ls -la /var/www/pizza-store-backend`
- Fix ownership: `sudo chown -R www-data:www-data /var/www/pizza-store-backend`
- Check socket permissions: `ls -la /run/pizza-store.sock`

### CORS Errors
- Verify `CORS_ALLOWED_ORIGINS` in `.env` matches frontend URL
- Restart Gunicorn: `sudo systemctl restart pizza-store`
- Check Nginx is forwarding headers correctly

---

## 📝 File Locations Summary

```
/var/www/pizza-store-backend/          # Application root
├── pizza_store/                       # Django project
│   ├── staticfiles/                   # Collected static files
│   ├── media/                         # User uploads
│   └── manage.py
├── venv/                              # Virtual environment
├── .env                               # Environment variables
└── requirements.txt

/etc/systemd/system/pizza-store.service  # Gunicorn service
/etc/nginx/sites-available/pizza-store   # Nginx config
/etc/nginx/sites-enabled/pizza-store      # Nginx enabled site
/run/pizza-store.sock                   # Gunicorn socket
```

---

## 🔄 Updating Application

When you need to update the application:

```bash
cd /var/www/pizza-store-backend

# Pull latest changes (if using git)
git pull

# Activate venv
source venv/bin/activate

# Install new dependencies
pip install -r requirements.txt

# Run migrations
cd pizza_store
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart Gunicorn
sudo systemctl restart pizza-store

# Reload Nginx (if config changed)
sudo systemctl reload nginx
```

---

## 🎉 You're Done!

Your Pizza Store backend is now running on:
- **GraphQL**: `https://yourdomain.com/graphql/`
- **Admin**: `https://yourdomain.com/admin/`

---

**Next Steps**:
1. Test all endpoints
2. Configure monitoring (optional)
3. Set up backups
4. Configure log rotation

---

**Last Updated**: 2024-01-15

