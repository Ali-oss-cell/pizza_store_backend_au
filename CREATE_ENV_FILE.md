# 🔐 How to Create .env File on Droplet

## Method 1: Copy from Template (Recommended)

After cloning the repository, copy the template and edit it:

```bash
# On your droplet
cd /var/www/pizza-store-backend

# Copy the template (if it exists locally, or create manually)
# Since template is not in repo, we'll create it manually - see Method 2
```

---

## Method 2: Create .env File Manually (Use This)

### Step 1: Create the .env file

```bash
# On your droplet
cd /var/www/pizza-store-backend

# Create .env file
nano .env
```

### Step 2: Paste this content and update values

Copy and paste this into the nano editor:

```bash
# Django Production Environment Variables
# DO NOT commit this file to git!

# ============================================
# SECURITY SETTINGS
# ============================================

# Secret Key - Generate a new one for production!
DJANGO_SECRET_KEY=your-generated-secret-key-here-CHANGE-THIS

# Debug Mode - MUST be False in production
DEBUG=False

# Allowed Hosts - Comma-separated list of domains/IPs
# Add your droplet IP address here
ALLOWED_HOSTS=api.marinapizzas.com.au,marinapizzas.com.au,www.marinapizzas.com.au,170.64.219.198

# ============================================
# DATABASE CONFIGURATION (DigitalOcean Managed PostgreSQL)
# ============================================

DB_NAME=defaultdb
DB_USER=doadmin
DB_PASSWORD=your-database-password-here
DB_HOST=private-db-postgresql-syd1-42296-do-user-26523274-0.e.db.ondigitalocean.com
DB_PORT=25060

# SSL Mode for PostgreSQL (required for DigitalOcean managed databases)
DB_SSLMODE=require

# ============================================
# CORS CONFIGURATION
# ============================================

# CORS Allowed Origins - Comma-separated list of frontend URLs
CORS_ALLOWED_ORIGINS=https://marinapizzas.com.au,https://www.marinapizzas.com.au

# CSRF Trusted Origins - Comma-separated list of trusted domains
CSRF_TRUSTED_ORIGINS=https://marinapizzas.com.au,https://www.marinapizzas.com.au,https://api.marinapizzas.com.au

# ============================================
# SSL/SECURITY SETTINGS (only used when DEBUG=False)
# ============================================

# Redirect HTTP to HTTPS
SECURE_SSL_REDIRECT=True

# HSTS (HTTP Strict Transport Security) - 1 year
SECURE_HSTS_SECONDS=31536000
```

### Step 3: Generate Secret Key

**While still in nano**, you need to generate a secret key. Open a **new terminal** (keep nano open):

```bash
# In a NEW terminal window (SSH again)
ssh root@170.64.219.198
cd /var/www/pizza-store-backend
source venv/bin/activate  # If venv exists, or skip this
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Copy the output** (it will be a long string like `django-insecure-...`)

**Go back to nano** and replace `your-generated-secret-key-here-CHANGE-THIS` with the generated key.

### Step 4: Save and Exit

In nano:
- Press `Ctrl + O` to save
- Press `Enter` to confirm
- Press `Ctrl + X` to exit

---

## Method 3: Create Using echo (Quick Method)

If you prefer command line, you can create it step by step:

```bash
cd /var/www/pizza-store-backend

# Generate secret key first
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

# Create .env file
cat > .env << EOF
# Django Production Environment Variables
DJANGO_SECRET_KEY=${SECRET_KEY}
DEBUG=False
ALLOWED_HOSTS=api.marinapizzas.com.au,marinapizzas.com.au,www.marinapizzas.com.au,170.64.219.198

# Database Configuration
DB_NAME=defaultdb
DB_USER=doadmin
DB_PASSWORD=your-database-password-here
DB_HOST=private-db-postgresql-syd1-42296-do-user-26523274-0.e.db.ondigitalocean.com
DB_PORT=25060
DB_SSLMODE=require

# CORS Configuration
CORS_ALLOWED_ORIGINS=https://marinapizzas.com.au,https://www.marinapizzas.com.au
CSRF_TRUSTED_ORIGINS=https://marinapizzas.com.au,https://www.marinapizzas.com.au,https://api.marinapizzas.com.au

# SSL Settings
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
EOF

# Protect the file
chmod 600 .env
```

---

## Method 4: Upload from Local Machine

If you have the template on your local machine:

```bash
# On your LOCAL machine
scp env.production.template root@170.64.219.198:/var/www/pizza-store-backend/.env

# Then on droplet, edit it
ssh root@170.64.219.198
cd /var/www/pizza-store-backend
nano .env
# Update DJANGO_SECRET_KEY and ALLOWED_HOSTS
```

---

## ✅ Verify .env File

After creating, verify it:

```bash
# Check file exists
ls -la /var/www/pizza-store-backend/.env

# Check permissions (should be 600)
ls -l /var/www/pizza-store-backend/.env

# View content (be careful, contains sensitive data)
cat /var/www/pizza-store-backend/.env
```

---

## 🔒 Security Checklist

- [ ] `.env` file created
- [ ] `DJANGO_SECRET_KEY` generated and set
- [ ] `DEBUG=False` set
- [ ] `ALLOWED_HOSTS` includes your droplet IP
- [ ] Database credentials are correct
- [ ] File permissions set to 600 (read/write for owner only)
- [ ] File is NOT in git (check `.gitignore`)

---

## 📝 Quick Reference: What to Update

| Variable | What to Set |
|----------|-------------|
| `DJANGO_SECRET_KEY` | Generate new one (see Method 3) |
| `ALLOWED_HOSTS` | Add your droplet IP: `170.64.219.198` |
| `DB_PASSWORD` | Your database password: `AVNS_1GHB72K7lqTFT0MS372` |
| `DEBUG` | Must be `False` |

All other values are already correct! ✅

---

**Recommended**: Use **Method 3** (echo method) - it's the fastest and generates the secret key automatically!

