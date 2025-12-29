# 🌐 Domain Setup Summary - marinapizzas.com.au

## Domain Structure

✅ **Frontend**: `marinapizzas.com.au` (and `www.marinapizzas.com.au`)  
✅ **Backend API**: `api.marinapizzas.com.au`

---

## 🎯 What You Need to Do

### 1. Update Nameservers at GoDaddy ✅ (Already Done)
- Nameservers are set to DigitalOcean
- Wait 24-48 hours for propagation

### 2. Add DNS Records in DigitalOcean

#### Backend API Record (Required)
```
Type: A
Hostname: api
Value: your-droplet-ip-address
TTL: 3600
```

#### Frontend Records (If using Droplet)
```
Type: A (or CNAME if using App Platform)
Hostname: @ (for root) and www
Value: your-frontend-ip-or-cname
TTL: 3600
```

### 3. Update Backend Configuration

#### On Your Droplet - Update `.env`:
```bash
ALLOWED_HOSTS=api.marinapizzas.com.au,marinapizzas.com.au,www.marinapizzas.com.au,your.droplet.ip
CORS_ALLOWED_ORIGINS=https://marinapizzas.com.au,https://www.marinapizzas.com.au
CSRF_TRUSTED_ORIGINS=https://marinapizzas.com.au,https://www.marinapizzas.com.au,https://api.marinapizzas.com.au
```

#### Update Nginx Config:
```bash
sudo nano /etc/nginx/sites-available/pizza-store
# Change server_name to: api.marinapizzas.com.au
sudo systemctl restart nginx
```

### 4. Get SSL Certificate

```bash
# For backend API
sudo certbot --nginx -d api.marinapizzas.com.au
```

---

## 🔗 Final URLs

After setup:

- **Frontend**: `https://marinapizzas.com.au`
- **Backend API**: `https://api.marinapizzas.com.au/graphql/`
- **Admin Panel**: `https://api.marinapizzas.com.au/admin/`

---

## 📝 Frontend Configuration

Update your frontend to use:

```javascript
const API_URL = 'https://api.marinapizzas.com.au/graphql/';
```

---

## ✅ Quick Checklist

- [x] Nameservers updated at GoDaddy
- [ ] Wait for DNS propagation (24-48 hours)
- [ ] Add `api` A record in DigitalOcean DNS
- [ ] Add frontend A/CNAME records
- [ ] Update `.env` file on droplet
- [ ] Update Nginx `server_name` to `api.marinapizzas.com.au`
- [ ] Restart Nginx
- [ ] Get SSL certificate: `sudo certbot --nginx -d api.marinapizzas.com.au`
- [ ] Test: `curl https://api.marinapizzas.com.au/graphql/`
- [ ] Update frontend API URL

---

**See `DNS_SETUP_GUIDE.md` for detailed instructions.**

