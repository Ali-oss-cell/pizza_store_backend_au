# 🌐 Frontend Domain Setup - marinapizzas.com.au

## Frontend Domains

✅ **Primary**: `marinapizzas.com.au` (root domain)  
✅ **WWW**: `www.marinapizzas.com.au`

Both domains will point to your frontend application.

---

## 📋 DNS Records for Frontend

### In DigitalOcean DNS, add these records:

#### Option 1: If using DigitalOcean App Platform (Recommended)

| Type | Hostname | Value | TTL |
|------|----------|-------|-----|
| **CNAME** | `@` | `your-app-platform-domain.ondigitalocean.app` | 3600 |
| **CNAME** | `www` | `your-app-platform-domain.ondigitalocean.app` | 3600 |

**Example**:
- If your App Platform domain is `pizza-frontend-abc123.ondigitalocean.app`
- Add CNAME `@` → `pizza-frontend-abc123.ondigitalocean.app`
- Add CNAME `www` → `pizza-frontend-abc123.ondigitalocean.app`

#### Option 2: If using a Droplet for Frontend

| Type | Hostname | Value | TTL |
|------|----------|-------|-----|
| **A** | `@` | `your-frontend-droplet-ip` | 3600 |
| **A** | `www` | `your-frontend-droplet-ip` | 3600 |

---

## 🔧 How to Add Records in DigitalOcean

### Step 1: Access DNS
1. Go to DigitalOcean Dashboard
2. Click **Networking** → **Domains**
3. Click on `marinapizzas.com.au`

### Step 2: Add Root Domain Record
1. Click **Add Record**
2. Select **CNAME** (if App Platform) or **A** (if Droplet)
3. Fill in:
   - **Hostname**: `@` (represents root domain)
   - **Will direct to**: Your frontend IP or CNAME
   - **TTL**: `3600`
4. Click **Create Record**

### Step 3: Add WWW Record
1. Click **Add Record**
2. Select **CNAME** (if App Platform) or **A** (if Droplet)
3. Fill in:
   - **Hostname**: `www`
   - **Will direct to**: Same as root domain
   - **TTL**: `3600`
4. Click **Create Record**

---

## ✅ Complete DNS Records Summary

Your complete DNS setup will be:

| Type | Hostname | Value | Purpose |
|------|----------|-------|---------|
| **NS** | `@` | `ns1.digitalocean.com` | Nameserver |
| **NS** | `@` | `ns2.digitalocean.com` | Nameserver |
| **NS** | `@` | `ns3.digitalocean.com` | Nameserver |
| **A** | `api` | `your-backend-droplet-ip` | Backend API |
| **CNAME** | `@` | `your-app-platform-domain` | Frontend (root) |
| **CNAME** | `www` | `your-app-platform-domain` | Frontend (www) |

---

## 🔒 SSL Certificates

### For Frontend (App Platform)
- ✅ **Automatic**: DigitalOcean App Platform provides free SSL automatically
- ✅ **Both domains**: Covers both `marinapizzas.com.au` and `www.marinapizzas.com.au`
- ✅ **Auto-renewal**: Handled automatically

### For Backend (Droplet)
```bash
sudo certbot --nginx -d api.marinapizzas.com.au
```

---

## 🎯 Final URLs

After setup:

- **Frontend**: `https://marinapizzas.com.au`
- **Frontend (www)**: `https://www.marinapizzas.com.au`
- **Backend API**: `https://api.marinapizzas.com.au/graphql/`
- **Admin Panel**: `https://api.marinapizzas.com.au/admin/`

Both frontend URLs will work and redirect to the same application.

---

## 🔄 Redirect Strategy (Optional)

You can configure redirects in your frontend app:

### Redirect www to non-www (or vice versa)

**Option 1: Redirect www → root** (Recommended)
```javascript
// In your frontend app
if (window.location.hostname === 'www.marinapizzas.com.au') {
  window.location.href = 'https://marinapizzas.com.au' + window.location.pathname;
}
```

**Option 2: Redirect root → www**
```javascript
if (window.location.hostname === 'marinapizzas.com.au') {
  window.location.href = 'https://www.marinapizzas.com.au' + window.location.pathname;
}
```

**Option 3: Keep both** (Current setup)
- Both domains work independently
- No redirect needed
- Users can access either URL

---

## 📝 Frontend Configuration

### Update API Endpoint

In your frontend application, set the API URL:

```javascript
// .env or config file
REACT_APP_API_URL=https://api.marinapizzas.com.au/graphql/

// Or in code
const API_URL = 'https://api.marinapizzas.com.au/graphql/';
```

### CORS Configuration

The backend is already configured to accept requests from:
- `https://marinapizzas.com.au`
- `https://www.marinapizzas.com.au`

No additional CORS setup needed! ✅

---

## ✅ Quick Checklist

- [x] Nameservers updated at GoDaddy
- [ ] Wait for DNS propagation (24-48 hours)
- [ ] Add `api` A record → Backend droplet IP
- [ ] Add `@` CNAME/A record → Frontend
- [ ] Add `www` CNAME/A record → Frontend
- [ ] Test: `curl https://marinapizzas.com.au`
- [ ] Test: `curl https://www.marinapizzas.com.au`
- [ ] Test: `curl https://api.marinapizzas.com.au/graphql/`
- [ ] Update frontend API URL to `https://api.marinapizzas.com.au/graphql/`

---

## 🧪 Testing DNS

### Check DNS Records

```bash
# Check root domain
dig marinapizzas.com.au +short

# Check www
dig www.marinapizzas.com.au +short

# Check API
dig api.marinapizzas.com.au +short
```

### Test URLs

```bash
# Frontend (root)
curl -I https://marinapizzas.com.au

# Frontend (www)
curl -I https://www.marinapizzas.com.au

# Backend API
curl https://api.marinapizzas.com.au/graphql/
```

---

## 📊 Domain Structure Summary

```
marinapizzas.com.au
├── Root (marinapizzas.com.au) → Frontend App
├── WWW (www.marinapizzas.com.au) → Frontend App
└── API (api.marinapizzas.com.au) → Backend Droplet
```

---

**Last Updated**: 2024-01-15

