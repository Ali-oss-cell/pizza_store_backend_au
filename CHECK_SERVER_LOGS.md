# Check Server Logs - Find Exact Errors

Guide to check server logs and find the exact error causing the 400 Bad Request.

---

## 🚀 Quick Commands

### **1. Check Gunicorn Error Logs (Most Important)**

```bash
# Real-time log monitoring (follow logs)
tail -f /var/www/pizza-store-backend/logs/gunicorn-error.log

# Or view last 50 lines
tail -n 50 /var/www/pizza-store-backend/logs/gunicorn-error.log

# View all errors
cat /var/www/pizza-store-backend/logs/gunicorn-error.log

# Search for specific errors
grep -i "error\|exception\|traceback" /var/www/pizza-store-backend/logs/gunicorn-error.log
```

### **2. Check Gunicorn Access Logs**

```bash
# View recent requests
tail -n 100 /var/www/pizza-store-backend/logs/gunicorn-access.log

# Search for GraphQL requests
grep "graphql" /var/www/pizza-store-backend/logs/gunicorn-access.log
```

### **3. Check Systemd Service Logs**

```bash
# View gunicorn service logs
journalctl -u gunicorn -n 100 --no-pager

# Follow logs in real-time
journalctl -u gunicorn -f

# View logs with timestamps
journalctl -u gunicorn --since "1 hour ago"

# View only errors
journalctl -u gunicorn -p err
```

### **4. Check Nginx Error Logs**

```bash
# View nginx error logs
tail -f /var/log/nginx/error.log

# Or
tail -n 50 /var/log/nginx/error.log
```

### **5. Check Nginx Access Logs**

```bash
# View recent requests
tail -n 100 /var/log/nginx/access.log

# Search for GraphQL requests
grep "graphql" /var/log/nginx/access.log
```

---

## 🔍 Step-by-Step: Find the Exact Error

### **Step 1: SSH into Your Droplet**

```bash
ssh root@your-droplet-ip
```

### **Step 2: Navigate to Project Directory**

```bash
cd /var/www/pizza-store-backend
```

### **Step 3: Check Gunicorn Error Logs (Most Important)**

```bash
# View last 100 lines of error log
tail -n 100 logs/gunicorn-error.log
```

**Look for:**
- GraphQL errors
- Permission errors
- Authentication errors
- Python tracebacks
- Django errors

### **Step 4: Monitor Logs in Real-Time**

While the frontend makes a request, watch the logs:

```bash
# In one terminal, watch logs
tail -f logs/gunicorn-error.log

# In another terminal or browser, make the POS request
# You'll see the error appear in real-time
```

### **Step 5: Search for Specific Errors**

```bash
# Search for GraphQL errors
grep -i "graphql\|pos\|permission\|authentication" logs/gunicorn-error.log

# Search for Python exceptions
grep -A 10 "Traceback\|Exception\|Error" logs/gunicorn-error.log

# Search for recent errors (last hour)
grep "$(date +%Y-%m-%d)" logs/gunicorn-error.log | tail -n 50
```

---

## 📋 Common Log Locations

### **Gunicorn Logs**
```bash
/var/www/pizza-store-backend/logs/gunicorn-error.log
/var/www/pizza-store-backend/logs/gunicorn-access.log
```

### **Systemd Logs**
```bash
journalctl -u gunicorn
```

### **Nginx Logs**
```bash
/var/log/nginx/error.log
/var/log/nginx/access.log
```

### **Django Logs (if configured)**
```bash
/var/www/pizza-store-backend/logs/django.log
```

---

## 🎯 What to Look For

### **1. Authentication Errors**

Look for:
```
Permission denied. Staff access required for POS.
Authentication required
User is not authenticated
```

### **2. GraphQL Errors**

Look for:
```
GraphQLError
Cannot query field
Expected value of type
Variable "$variable" is never used
```

### **3. Python Exceptions**

Look for:
```
Traceback (most recent call last):
AttributeError
TypeError
ValueError
```

### **4. Request Details**

Look for:
- Request path: `/graphql/`
- Request method: `POST`
- Status code: `400`
- Error message

---

## 🔧 Useful Commands

### **View Last 50 Errors**

```bash
tail -n 50 /var/www/pizza-store-backend/logs/gunicorn-error.log | grep -i error
```

### **Find Errors from Last Hour**

```bash
grep "$(date +%Y-%m-%d)" /var/www/pizza-store-backend/logs/gunicorn-error.log | grep -i error
```

### **Count Errors**

```bash
grep -c "ERROR\|Exception\|Traceback" /var/www/pizza-store-backend/logs/gunicorn-error.log
```

### **View Errors with Context (10 lines before/after)**

```bash
grep -B 10 -A 10 "ERROR\|Exception" /var/www/pizza-store-backend/logs/gunicorn-error.log | tail -n 50
```

### **Search for Specific Query**

```bash
grep -i "posProducts\|pos_products" /var/www/pizza-store-backend/logs/gunicorn-error.log
```

---

## 📊 Example Log Output

### **What a GraphQL Error Looks Like:**

```
[2024-01-15 10:30:45] ERROR: GraphQLError: Permission denied. Staff access required for POS.
Traceback (most recent call last):
  File "/var/www/pizza-store-backend/pizza_store/inventory/pos_schema.py", line 175, in resolve_pos_products
    raise GraphQLError("Permission denied. Staff access required for POS.")
graphql.error.base.GraphQLError: Permission denied. Staff access required for POS.
```

### **What an Authentication Error Looks Like:**

```
[2024-01-15 10:30:45] ERROR: User is not authenticated
Traceback (most recent call last):
  File "/var/www/pizza-store-backend/pizza_store/inventory/pos_schema.py", line 172, in resolve_pos_products
    user = info.context.user if info.context.user.is_authenticated else None
AttributeError: 'AnonymousUser' object has no attribute 'is_staff'
```

---

## 🚀 Quick One-Liner to Check Logs

```bash
# Check last 20 errors
tail -n 100 /var/www/pizza-store-backend/logs/gunicorn-error.log | grep -i "error\|exception" | tail -n 20
```

---

## 💡 Pro Tips

### **1. Clear Old Logs (if too large)**

```bash
# Backup first
cp /var/www/pizza-store-backend/logs/gunicorn-error.log /var/www/pizza-store-backend/logs/gunicorn-error.log.backup

# Clear log (keep last 1000 lines)
tail -n 1000 /var/www/pizza-store-backend/logs/gunicorn-error.log > /var/www/pizza-store-backend/logs/gunicorn-error.log.tmp
mv /var/www/pizza-store-backend/logs/gunicorn-error.log.tmp /var/www/pizza-store-backend/logs/gunicorn-error.log
```

### **2. Watch Logs While Testing**

```bash
# Terminal 1: Watch logs
tail -f /var/www/pizza-store-backend/logs/gunicorn-error.log

# Terminal 2 or Browser: Make request
# You'll see error appear immediately
```

### **3. Save Error to File**

```bash
# Save last 100 errors to file
tail -n 100 /var/www/pizza-store-backend/logs/gunicorn-error.log > /tmp/errors.txt
cat /tmp/errors.txt
```

---

## 🔍 Debugging Workflow

1. **SSH into server**
   ```bash
   ssh root@your-droplet-ip
   ```

2. **Check recent errors**
   ```bash
   tail -n 50 /var/www/pizza-store-backend/logs/gunicorn-error.log
   ```

3. **Watch logs in real-time**
   ```bash
   tail -f /var/www/pizza-store-backend/logs/gunicorn-error.log
   ```

4. **Make request from frontend** (in browser)

5. **See error appear in terminal**

6. **Copy error message** and share it

---

## 📞 After Finding the Error

Once you find the exact error:

1. **Copy the full error message** (including traceback)
2. **Note the timestamp**
3. **Check what query was being made**
4. **Share the error** so we can fix it

**Example:**
```
[2024-01-15 10:30:45] ERROR: GraphQLError: Permission denied. Staff access required for POS.
```

This tells us exactly what's wrong!

---

**Run these commands on your droplet to find the exact error!** 🎯
