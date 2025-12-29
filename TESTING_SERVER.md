# 🧪 Server Testing Guide

Complete guide to test if your Pizza Store backend server is working correctly.

---

## ✅ Quick Health Check

### 1. Service Status

```bash
# Check Gunicorn service
sudo systemctl status pizza-store

# Check Nginx service
sudo systemctl status nginx

# Both should show "active (running)"
```

### 2. Socket File

```bash
# Check if socket exists
ls -la /run/pizza-store/pizza-store.sock

# Should show: srwxrwxrwx (socket file)
```

### 3. Health Endpoint

```bash
# Test health endpoint
curl http://localhost/health/

# Expected output: OK
```

---

## 🔍 Detailed Testing

### Test 1: Health Endpoint

```bash
curl http://localhost/health/
```

**Expected**: `OK`

**If fails**: Check Nginx and Gunicorn services

---

### Test 2: GraphQL Endpoint (Basic)

```bash
# Simple introspection query
curl -X POST http://localhost/graphql/ \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __typename }"}'
```

**Expected**: JSON response with `{"data":{"__typename":"Query"}}`

**If fails**: Check Django logs and database connection

---

### Test 3: GraphQL Endpoint (Products Query)

```bash
# Query products
curl -X POST http://localhost/graphql/ \
  -H "Content-Type: application/json" \
  -d '{"query": "{ products { id name price } }"}'
```

**Expected**: JSON with products array (may be empty if no products)

---

### Test 4: Admin Panel

```bash
# Test admin panel (should return login page)
curl -I http://localhost/admin/

# Expected: HTTP/1.1 200 OK or 302 (redirect to login)
```

**Or open in browser**: `http://your-droplet-ip/admin/`

---

### Test 5: Static Files

```bash
# Check if static files are served
curl -I http://localhost/static/admin/css/base.css

# Expected: HTTP/1.1 200 OK
```

---

### Test 6: Database Connection

```bash
cd /var/www/pizza-store-backend/pizza_store
source ../venv/bin/activate

# Test database connection
python manage.py dbshell

# If connects, you'll see PostgreSQL prompt
# Type: \q to exit
```

**Expected**: PostgreSQL prompt (psql)

---

### Test 7: Django Check

```bash
cd /var/www/pizza-store-backend/pizza_store
source ../venv/bin/activate

# Run Django system check
python manage.py check

# Expected: System check identified no issues (0 silenced).
```

---

## 🌐 External Testing (After DNS is Ready)

### Test from Your Computer

```bash
# Health check
curl http://api.marinapizzas.com.au/health/

# GraphQL
curl -X POST http://api.marinapizzas.com.au/graphql/ \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __typename }"}'

# Admin (in browser)
# http://api.marinapizzas.com.au/admin/
```

---

## 📊 Complete Test Script

Save this as `test_server.sh` and run it:

```bash
#!/bin/bash

echo "=== Pizza Store Backend Server Tests ==="
echo ""

echo "1. Checking Services..."
systemctl is-active --quiet pizza-store && echo "✓ Gunicorn: Running" || echo "✗ Gunicorn: Not Running"
systemctl is-active --quiet nginx && echo "✓ Nginx: Running" || echo "✗ Nginx: Not Running"
echo ""

echo "2. Checking Socket..."
[ -S /run/pizza-store/pizza-store.sock ] && echo "✓ Socket exists" || echo "✗ Socket missing"
echo ""

echo "3. Testing Health Endpoint..."
HEALTH=$(curl -s http://localhost/health/)
[ "$HEALTH" = "OK" ] && echo "✓ Health: OK" || echo "✗ Health: Failed ($HEALTH)"
echo ""

echo "4. Testing GraphQL..."
GRAPHQL=$(curl -s -X POST http://localhost/graphql/ \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __typename }"}')
if echo "$GRAPHQL" | grep -q "__typename"; then
  echo "✓ GraphQL: Working"
else
  echo "✗ GraphQL: Failed"
  echo "Response: $GRAPHQL"
fi
echo ""

echo "5. Testing Admin Panel..."
ADMIN=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/admin/)
[ "$ADMIN" = "200" ] || [ "$ADMIN" = "302" ] && echo "✓ Admin: Accessible ($ADMIN)" || echo "✗ Admin: Failed ($ADMIN)"
echo ""

echo "6. Testing Static Files..."
STATIC=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/static/admin/css/base.css)
[ "$STATIC" = "200" ] && echo "✓ Static Files: Working" || echo "✗ Static Files: Failed ($STATIC)"
echo ""

echo "=== Test Complete ==="
```

**Make it executable and run**:
```bash
chmod +x test_server.sh
./test_server.sh
```

---

## 🔧 Troubleshooting Tests

### If Health Endpoint Fails

```bash
# Check Nginx error log
sudo tail -20 /var/log/nginx/pizza-store-error.log

# Check Gunicorn logs
sudo tail -20 /var/www/pizza-store-backend/logs/gunicorn-error.log

# Check service status
sudo systemctl status pizza-store
```

### If GraphQL Returns 400

**This is normal!** GraphQL expects POST with JSON. Test with:
```bash
curl -X POST http://localhost/graphql/ \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __typename }"}'
```

### If GraphQL Returns 500

```bash
# Check Django logs
sudo tail -50 /var/www/pizza-store-backend/logs/gunicorn-error.log

# Check database connection
cd /var/www/pizza-store-backend/pizza_store
source ../venv/bin/activate
python manage.py check
```

---

## ✅ Success Indicators

Your server is working correctly if:

- ✅ `systemctl status pizza-store` shows "active (running)"
- ✅ `systemctl status nginx` shows "active (running)"
- ✅ Socket file exists: `/run/pizza-store/pizza-store.sock`
- ✅ Health endpoint returns: `OK`
- ✅ GraphQL returns JSON (not HTML error page)
- ✅ Admin panel is accessible (login page or redirect)
- ✅ Static files return 200 status
- ✅ Database connection works

---

## 🎯 Quick Test Commands

```bash
# One-liner health check
curl http://localhost/health/ && echo " ✓ Server is running!"

# One-liner GraphQL test
curl -X POST http://localhost/graphql/ -H "Content-Type: application/json" -d '{"query":"{__typename}"}' | grep -q "__typename" && echo "✓ GraphQL working" || echo "✗ GraphQL failed"

# Check all services
systemctl is-active pizza-store nginx && echo "✓ All services running" || echo "✗ Some services down"
```

---

## 📝 Test Checklist

- [ ] Gunicorn service running
- [ ] Nginx service running
- [ ] Socket file exists
- [ ] Health endpoint returns OK
- [ ] GraphQL endpoint responds
- [ ] Admin panel accessible
- [ ] Static files loading
- [ ] Database connection works
- [ ] No errors in logs
- [ ] External access works (if DNS ready)

---

**Last Updated**: 2024-01-15

