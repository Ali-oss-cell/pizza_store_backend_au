# 💻 DigitalOcean Droplet Sizing Guide

## Recommended Configuration

### For Your Pizza Store Backend

**Starting Option (Recommended):**
- **Droplet**: Shared CPU Premium AMD
- **RAM**: 2 GB
- **CPU**: 1 vCPU
- **Storage**: 50 GB NVMe SSD
- **Transfer**: 2 TB
- **Price**: $14/month ($0.021/hour)

**Why This Works:**
- ✅ Sufficient for small to medium traffic (100-500 concurrent users)
- ✅ 3 Gunicorn workers fit comfortably in 2 GB RAM
- ✅ 50 GB storage is plenty for media files (product images)
- ✅ 2 TB transfer is generous for API traffic
- ✅ Can scale up easily if needed

---

## Resource Breakdown

### Memory Usage (2 GB Droplet)

| Component | Memory Usage |
|-----------|--------------|
| **Gunicorn (3 workers)** | ~150-300 MB |
| **Django Application** | ~100-200 MB |
| **Nginx** | ~10-20 MB |
| **System/OS** | ~300-400 MB |
| **Buffer/Headroom** | ~200-300 MB |
| **Total Used** | ~760-1220 MB |
| **Available** | ~780-1240 MB |

**Verdict**: 2 GB is **sufficient** with comfortable headroom.

### CPU Usage

- **1 vCPU** is adequate for:
  - API requests (GraphQL)
  - Image processing (Pillow)
  - Database queries (PostgreSQL is separate)
  - Background tasks (if any)

**Verdict**: 1 vCPU is **sufficient** for moderate traffic.

### Storage (50 GB)

- **Application**: ~500 MB
- **Static files**: ~50-200 MB
- **Media files (images)**: ~5-20 GB (depends on products)
- **Logs**: ~1-5 GB
- **System**: ~10 GB
- **Total**: ~17-36 GB

**Verdict**: 50 GB is **plenty** for starting out.

### Network Transfer (2 TB)

- **API requests**: ~10-50 GB/month (depends on traffic)
- **Static files**: ~50-200 GB/month
- **Media files**: ~100-500 GB/month (depends on images)
- **Total**: ~160-750 GB/month

**Verdict**: 2 TB is **more than enough**.

---

## Traffic Capacity Estimates

### 2 GB / 1 vCPU Droplet Can Handle:

| Traffic Level | Concurrent Users | Requests/Second | Status |
|---------------|------------------|-----------------|--------|
| **Light** | 10-50 | 5-20 | ✅ Excellent |
| **Moderate** | 50-200 | 20-50 | ✅ Good |
| **Heavy** | 200-500 | 50-100 | ⚠️ May need upgrade |
| **Very Heavy** | 500+ | 100+ | ❌ Upgrade needed |

**Recommendation**: Start with 2 GB, monitor, and scale up if needed.

---

## When to Upgrade

### Upgrade to 4 GB / 2 vCPU ($24/month) if:

- ✅ Traffic consistently > 200 concurrent users
- ✅ Memory usage > 80% consistently
- ✅ CPU usage > 70% consistently
- ✅ Response times slowing down
- ✅ Planning for high traffic events

### Upgrade to 8 GB / 4 vCPU ($48/month) if:

- ✅ High traffic (500+ concurrent users)
- ✅ Multiple applications on same server
- ✅ Heavy image processing
- ✅ Complex GraphQL queries with high load

---

## Separate Database (Excellent Choice!)

Since you're using **separate managed PostgreSQL**, this is great because:

✅ **Droplet resources** are dedicated to application only  
✅ **Database** has its own resources (managed by DigitalOcean)  
✅ **Better performance** - no resource competition  
✅ **Easier scaling** - scale app and DB independently  
✅ **Better reliability** - database backups handled automatically  

**Recommended Database Plan:**
- **Basic**: $15/month (1 GB RAM, 1 vCPU, 10 GB storage)
- **Professional**: $60/month (2 GB RAM, 1 vCPU, 25 GB storage)

Start with **Basic** ($15/month) and upgrade if needed.

---

## Cost Breakdown

### Option 1: Basic Setup (Recommended Start)
- **Droplet**: $14/month (2 GB / 1 vCPU)
- **Managed PostgreSQL**: $15/month (Basic)
- **Total**: **$29/month**

### Option 2: Moderate Traffic
- **Droplet**: $24/month (4 GB / 2 vCPU)
- **Managed PostgreSQL**: $15/month (Basic)
- **Total**: **$39/month**

### Option 3: High Traffic
- **Droplet**: $48/month (8 GB / 4 vCPU)
- **Managed PostgreSQL**: $60/month (Professional)
- **Total**: **$108/month**

---

## Optimization Tips

### 1. Gunicorn Workers
Your current config has **3 workers**, which is perfect for 2 GB RAM:
```ini
--workers 3
```

**Formula**: `(2 × CPU cores) + 1 = workers`
- For 1 vCPU: `(2 × 1) + 1 = 3 workers` ✅ Perfect!

### 2. Database Connection Pooling
Use connection pooling to reduce database load:
```python
DATABASES = {
    'default': {
        # ... your config ...
        'CONN_MAX_AGE': 600,  # Reuse connections
    }
}
```

### 3. Static Files Caching
Nginx is already configured with caching (30 days for static, 7 days for media).

### 4. Enable Gzip Compression
Add to Nginx config:
```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
```

### 5. Monitor Resources
```bash
# Install monitoring
sudo apt install htop

# Check memory
free -h

# Check disk
df -h

# Check CPU
top
```

---

## Monitoring Recommendations

### 1. DigitalOcean Monitoring
- Enable in DigitalOcean dashboard
- Free basic monitoring included
- Alerts for CPU, memory, disk

### 2. Application Monitoring
- Monitor response times
- Track error rates
- Monitor database query times

### 3. Key Metrics to Watch
- **Memory usage** < 80%
- **CPU usage** < 70%
- **Disk usage** < 80%
- **Response time** < 500ms (p95)

---

## Scaling Strategy

### Vertical Scaling (Upgrade Droplet)
- **Easy**: Just resize droplet in DigitalOcean
- **Downtime**: ~1-2 minutes
- **When**: Consistent high resource usage

### Horizontal Scaling (Multiple Droplets)
- **Complex**: Requires load balancer
- **Cost**: More expensive
- **When**: Very high traffic, need redundancy

**Recommendation**: Start vertical, scale horizontal later if needed.

---

## Final Recommendation

### ✅ Start With: 2 GB / 1 vCPU ($14/month)

**Why:**
1. ✅ Sufficient for starting out
2. ✅ Can handle moderate traffic
3. ✅ Easy to upgrade later (just resize)
4. ✅ Cost-effective
5. ✅ Your separate database is smart choice

### 📊 Expected Performance:
- **Concurrent Users**: 50-200 comfortably
- **Requests/Second**: 20-50
- **Response Time**: < 300ms (p95)
- **Uptime**: 99.9%+

### 🔄 Upgrade Path:
1. **Month 1-3**: Monitor usage
2. **If needed**: Upgrade to 4 GB ($24/month)
3. **Scale database**: Upgrade PostgreSQL if needed
4. **Optimize**: Before scaling, optimize code/queries

---

## Quick Start Checklist

- [ ] Create 2 GB / 1 vCPU droplet
- [ ] Create managed PostgreSQL database (Basic)
- [ ] Deploy application following NGINX_GUNICORN_SETUP.md
- [ ] Monitor for first week
- [ ] Adjust Gunicorn workers if needed
- [ ] Set up monitoring/alerts
- [ ] Plan upgrade if traffic grows

---

## Cost Summary

| Component | Monthly Cost |
|-----------|--------------|
| Droplet (2 GB) | $14 |
| Managed PostgreSQL (Basic) | $15 |
| **Total** | **$29/month** |

**Annual**: ~$348/year

---

**Conclusion**: Your $14/month droplet choice is **perfect** for starting out! With a separate managed database, you have a solid, scalable foundation. 🚀

