# Create Admin Account - Quick Guide

## 🎯 Quick Command for Droplet

### **Simple (Interactive - will prompt for password):**

```bash
cd /var/www/pizza-store-backend/pizza_store
source ../venv/bin/activate
python manage.py create_admin
```

### **With All Options:**

```bash
cd /var/www/pizza-store-backend/pizza_store
source ../venv/bin/activate
python manage.py create_admin \
  --username admin \
  --email admin@marinapizzas.com.au \
  --password "your_secure_password" \
  --first-name "Admin" \
  --last-name "User" \
  --phone "0412345678"
```

### **Update Existing Admin:**

```bash
python manage.py create_admin \
  --username admin \
  --password "new_password" \
  --update
```

---

## 📋 Command Options

| Option | Description | Default |
|--------|-------------|---------|
| `--username` | Username for admin | `admin` |
| `--email` | Email address | `admin@marinapizzas.com.au` |
| `--password` | Password (or will prompt) | *prompt* |
| `--first-name` | First name | `Admin` |
| `--last-name` | Last name | `User` |
| `--phone` | Phone number (optional) | *empty* |
| `--update` | Update if user exists | *skip if exists* |
| `--force` | Same as --update | *skip if exists* |

---

## ✅ What This Command Does

1. **Creates/Updates Admin User** with:
   - ✅ `role = 'admin'`
   - ✅ `is_staff = True`
   - ✅ `is_superuser = True`
   - ✅ `is_active = True`
   - ✅ All permissions set to `True`

2. **Sets Password** securely (hashed)

3. **Displays Account Details** for easy reference

---

## 🚀 Step-by-Step for Droplet

### **1. SSH into your droplet:**

```bash
ssh root@your-droplet-ip
```

### **2. Navigate to project:**

```bash
cd /var/www/pizza-store-backend/pizza_store
```

### **3. Activate virtual environment:**

```bash
source ../venv/bin/activate
```

### **4. Create admin account:**

```bash
python manage.py create_admin \
  --username admin \
  --email admin@marinapizzas.com.au \
  --password "YourSecurePassword123!" \
  --first-name "Admin" \
  --last-name "User"
```

### **5. You'll see output like:**

```
✅ Admin user created/updated successfully!
============================================================

📋 Account Details:
   Username: admin
   Email: admin@marinapizzas.com.au
   Password: **************** (hidden)
   Role: Admin
   Is Admin: True
   Is Staff: True
   Is Superuser: True
   Is Active: True

🔐 You can now login with these credentials!
```

---

## 🔐 After Creating Admin

### **1. Login to Dashboard:**

Use the GraphQL endpoint:
```
https://api.marinapizzas.com.au/graphql/
```

**Login Mutation:**
```graphql
mutation {
  login(input: {
    username: "admin"
    password: "YourSecurePassword123!"
  }) {
    success
    user {
      id
      username
      role
      isAdmin
    }
  }
}
```

### **2. Create Staff Users:**

Once logged in as admin, use the `register` mutation:

```graphql
mutation {
  register(input: {
    username: "cashier1"
    email: "cashier1@store.com"
    password: "password123"
    passwordConfirm: "password123"
    firstName: "Cashier"
    lastName: "One"
    phone: "0412345678"
    role: "staff"
    canManageOrders: true
    canManageProducts: false
    canManageCategories: false
    canManagePromotions: false
    canViewReports: false
    canManageReviews: false
  }) {
    success
    user {
      id
      username
      role
    }
  }
}
```

---

## 🛠️ Troubleshooting

### **User Already Exists:**

If you see:
```
User "admin" already exists. Use --update to update it.
```

**Solution:**
```bash
python manage.py create_admin --username admin --password "new_password" --update
```

### **Permission Denied:**

Make sure you're using the correct user:
```bash
# If needed, use sudo
sudo -u www-data python manage.py create_admin --username admin --password "pass"
```

### **Virtual Environment Not Found:**

```bash
# Find venv location
ls -la /var/www/pizza-store-backend/

# Activate it
source /var/www/pizza-store-backend/venv/bin/activate
```

---

## 📝 Quick Reference

**One-liner for droplet:**
```bash
cd /var/www/pizza-store-backend/pizza_store && source ../venv/bin/activate && python manage.py create_admin --username admin --email admin@marinapizzas.com.au --password "YourPassword123!"
```

**Update existing admin:**
```bash
python manage.py create_admin --username admin --password "NewPassword123!" --update
```

---

**That's it! You now have a proper admin account with full privileges!** 🎉
