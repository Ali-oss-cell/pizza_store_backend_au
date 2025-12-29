# 🌐 DNS Setup Guide - marinapizzas.com.au

## Domain Structure

- **Frontend**: `marinapizzas.com.au` and `www.marinapizzas.com.au`
- **Backend API**: `api.marinapizzas.com.au`

---

## 📋 DigitalOcean DNS Records Setup

After updating nameservers at GoDaddy, add these DNS records in DigitalOcean:

### 1. Frontend Records (Your Frontend App Platform)

| Type | Hostname | Value | TTL |
|------|----------|-------|-----|
| **A** | `@` | `your-frontend-ip-or-cname` | 3600 |
| **A** | `www` | `your-frontend-ip-or-cname` | 3600 |
| **CNAME** | `www` | `your-app-platform-domain` | 3600 |

**Note**: If using DigitalOcean App Platform, you'll get a CNAME to use instead of A record.

### 2. Backend API Records (Your Droplet)

| Type | Hostname | Value | TTL |
|------|----------|-------|-----|
| **A** | `api` | `your-droplet-ip-address` | 3600 |

**Example**: If your droplet IP is `123.45.67.89`:
- Hostname: `api`
- Type: `A`
- Value: `123.45.67.89`
- TTL: `3600`

### 3. Complete DNS Records Table

| Type | Hostname | Value | Purpose |
|------|----------|-------|---------|
| **NS** | `@` | `ns1.digitalocean.com` | Nameserver (already set) |
| **NS** | `@` | `ns2.digitalocean.com` | Nameserver (already set) |
| **NS** | `@` | `ns3.digitalocean.com` | Nameserver (already set) |
| **A** | `api` | `your-droplet-ip` | Backend API |
| **A** | `@` | `your-frontend-ip` | Frontend (or CNAME) |
| **A** | `www` | `your-frontend-ip` | Frontend www (or CNAME) |

---

## 🔧 How to Add DNS Records in DigitalOcean

### Step 1: Access DNS Management
1. Go to DigitalOcean Dashboard
2. Click **Networking** → **Domains**
3. Click on `marinapizzas.com.au`

### Step 2: Add Backend API Record
1. Click **Add Record**
2. Select **A Record**
3. Fill in:
   - **Hostname**: `api`
   - **Will direct to**: `your-droplet-ip-address`
   - **TTL**: `3600` (1 hour)
4. Click **Create Record**

### Step 3: Add Frontend Records
1. Click **Add Record**
2. Select **A Record** (or **CNAME** if using App Platform)
3. Fill in:
   - **Hostname**: `@` (for root domain) or `www`
   - **Will direct to**: `your-frontend-ip-or-cname`
   - **TTL**: `3600`
4. Click **Create Record**

---

## ⚙️ Update Environment Variables

### Backend `.env` File

Update your `.env` file on the droplet:

```bash
# Allowed Hosts
ALLOWED_HOSTS=api.marinapizzas.com.au,marinapizzas.com.au,www.marinapizzas.com.au,your.droplet.ip

# CORS - Frontend URLs
CORS_ALLOWED_ORIGINS=https://marinapizzas.com.au,https://www.marinapizzas.com.au

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS=https://marinapizzas.com.au,https://www.marinapizzas.com.au,https://api.marinapizzas.com.au
```

### Frontend Configuration

Update your frontend to use the API:

```javascript
// API endpoint
const API_URL = 'https://api.marinapizzas.com.au/graphql/';

// Or in environment variables
REACT_APP_API_URL=https://api.marinapizzas.com.au/graphql/
```

---

## 🔒 SSL Certificate Setup

### For Backend (api.marinapizzas.com.au)

```bash
# On your droplet
sudo certbot --nginx -d api.marinapizzas.com.au
```

### For Frontend (marinapizzas.com.au)

If using DigitalOcean App Platform, SSL is automatic.  
If using a droplet, run:

```bash
sudo certbot --nginx -d marinapizzas.com.au -d www.marinapizzas.com.au
```

---

## 📝 Updated Nginx Configuration

### Backend Nginx Config (`/etc/nginx/sites-available/pizza-store`)

Update `server_name`:

```nginx
server {
    listen 80;
    server_name api.marinapizzas.com.au;

    # ... rest of config ...
}
```

After SSL:

```nginx
server {
    listen 443 ssl http2;
    server_name api.marinapizzas.com.au;

    ssl_certificate /etc/letsencrypt/live/api.marinapizzas.com.au/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.marinapizzas.com.au/privkey.pem;
    
    # ... rest of config ...
}
```

---

## ✅ Testing DNS Propagation

### Check if DNS records are active:

```bash
# Check A record for API
dig api.marinapizzas.com.au +short

# Check root domain
dig marinapizzas.com.au +short

# Check www
dig www.marinapizzas.com.au +short
```

### Test API endpoint:

```bash
# Test HTTP (before SSL)
curl http://api.marinapizzas.com.au/graphql/

# Test HTTPS (after SSL)
curl https://api.marinapizzas.com.au/graphql/
```

---

## 🎯 Final URLs

After setup, your URLs will be:

- **Frontend**: `https://marinapizzas.com.au`
- **Frontend (www)**: `https://www.marinapizzas.com.au`
- **Backend API**: `https://api.marinapizzas.com.au/graphql/`
- **Admin Panel**: `https://api.marinapizzas.com.au/admin/`

---

## ⏱️ DNS Propagation Time

- **Nameserver changes**: 24-48 hours (from GoDaddy)
- **DNS records**: 5-60 minutes (after nameservers are active)
- **SSL certificates**: Immediate after DNS is active

---

## 🔄 GoDaddy Nameserver Update

### Steps to Update Nameservers at GoDaddy:

1. Log in to GoDaddy
2. Go to **My Products** → **Domains**
3. Click on `marinapizzas.com.au`
4. Scroll to **Nameservers** section
5. Click **Change**
6. Select **Custom**
7. Add these nameservers:
   - `ns1.digitalocean.com`
   - `ns2.digitalocean.com`
   - `ns3.digitalocean.com`
8. Click **Save**

**Note**: It may take 24-48 hours for nameserver changes to propagate globally.

---

## 📋 Quick Checklist

- [ ] Update nameservers at GoDaddy
- [ ] Wait for nameserver propagation (check with `dig NS marinapizzas.com.au`)
- [ ] Add `api` A record pointing to droplet IP
- [ ] Add frontend A/CNAME records
- [ ] Update `.env` file with domain names
- [ ] Update Nginx config with `api.marinapizzas.com.au`
- [ ] Restart Nginx: `sudo systemctl restart nginx`
- [ ] Get SSL certificate for API: `sudo certbot --nginx -d api.marinapizzas.com.au`
- [ ] Test API endpoint: `curl https://api.marinapizzas.com.au/graphql/`
- [ ] Update frontend to use `https://api.marinapizzas.com.au/graphql/`

---

**Last Updated**: 2024-01-15

