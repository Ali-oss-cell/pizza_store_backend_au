# Create POS User (Team Member) - Complete Guide

Quick guide for creating team members who will work with the POS system.

---

## 🎯 Quick Answer: Create POS Cashier

### **Via GraphQL (From Dashboard):**

```graphql
mutation CreatePOSCashier {
  register(input: {
    username: "cashier1"
    email: "cashier1@marinapizzas.com.au"
    password: "password123"
    passwordConfirm: "password123"
    firstName: "John"
    lastName: "Doe"
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
    message
    user {
      id
      username
      email
      role
      isStaffMember
      permissions
    }
  }
}
```

---

## 📋 POS User Requirements

### **What a POS User Needs:**

| Permission | Value | Why |
|------------|-------|-----|
| `role` | `"staff"` | Must be staff (not admin) |
| `canManageOrders` | `true` | ✅ **Required** - To create orders in POS |
| `canManageProducts` | `false` | ❌ Cannot modify products |
| `canManageCategories` | `false` | ❌ Cannot modify categories |
| `canManagePromotions` | `false` | ❌ Cannot modify promotions |
| `canViewReports` | `false` | ❌ Cannot view reports (optional: can be true) |
| `canManageReviews` | `false` | ❌ Cannot manage reviews |

---

## 🚀 Step-by-Step: Create POS User

### **Step 1: Login as Admin**

First, make sure you're logged in as admin:

```graphql
mutation AdminLogin {
  login(input: {
    username: "admin"
    password: "YourAdminPassword"
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

### **Step 2: Create POS User**

Use the `register` mutation:

```graphql
mutation CreatePOSUser {
  register(input: {
    username: "cashier1"
    email: "cashier1@marinapizzas.com.au"
    password: "secure_password_123"
    passwordConfirm: "secure_password_123"
    firstName: "John"
    lastName: "Doe"
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
    message
    user {
      id
      username
      email
      role
      isStaffMember
      permissions
    }
  }
}
```

### **Step 3: Verify User Created**

Check the response:
```json
{
  "data": {
    "register": {
      "success": true,
      "message": "Staff user created successfully",
      "user": {
        "id": "5",
        "username": "cashier1",
        "email": "cashier1@marinapizzas.com.au",
        "role": "staff",
        "isStaffMember": true,
        "permissions": ["orders"]
      }
    }
  }
}
```

---

## 💡 Different POS User Types

### **1. Basic Cashier (POS Only)**

**Can:** Create orders, scan barcodes, print receipts  
**Cannot:** Modify products, inventory, settings

```graphql
mutation CreateBasicCashier {
  register(input: {
    username: "cashier1"
    email: "cashier1@store.com"
    password: "password123"
    passwordConfirm: "password123"
    firstName: "John"
    lastName: "Doe"
    role: "staff"
    canManageOrders: true
    canManageProducts: false
    canManageCategories: false
    canManagePromotions: false
    canViewReports: false
    canManageReviews: false
  }) {
    success
    user { id username permissions }
  }
}
```

### **2. Shift Manager (POS + Reports)**

**Can:** Create orders, view reports, manage reviews  
**Cannot:** Modify products, categories, promotions

```graphql
mutation CreateShiftManager {
  register(input: {
    username: "manager1"
    email: "manager1@store.com"
    password: "password123"
    passwordConfirm: "password123"
    firstName: "Jane"
    lastName: "Smith"
    role: "staff"
    canManageOrders: true
    canManageProducts: false
    canManageCategories: false
    canManagePromotions: false
    canViewReports: true
    canManageReviews: true
  }) {
    success
    user { id username permissions }
  }
}
```

### **3. Store Manager (Full Access)**

**Can:** Everything except user management  
**Cannot:** Create/delete users (admin only)

```graphql
mutation CreateStoreManager {
  register(input: {
    username: "store_manager1"
    email: "store_manager1@store.com"
    password: "password123"
    passwordConfirm: "password123"
    firstName: "Mike"
    lastName: "Johnson"
    role: "staff"
    canManageOrders: true
    canManageProducts: true
    canManageCategories: true
    canManagePromotions: true
    canViewReports: true
    canManageReviews: true
  }) {
    success
    user { id username permissions }
  }
}
```

---

## 🔐 POS User Login

After creating the user, they can login to POS:

```graphql
mutation POSLogin {
  login(input: {
    username: "cashier1"
    password: "password123"
  }) {
    success
    user {
      id
      username
      role
      isStaffMember
      isAdmin
      permissions
    }
  }
}
```

**POS Access Check:**
- ✅ `isStaffMember: true` → Can access POS
- ✅ `isAdmin: true` → Can access POS
- ❌ Neither → Cannot access POS

---

## 📱 Using POS After Login

### **1. Get Products for POS:**

```graphql
query POSProducts {
  posProducts {
    id
    name
    description
    basePrice
    sizes {
      id
      name
      price
    }
    category {
      id
      name
    }
    barcode
    sku
    stockQuantity
    isInStock
  }
}
```

### **2. Scan Barcode:**

```graphql
query ScanBarcode($barcode: String!) {
  productByBarcode(barcode: $barcode) {
    id
    name
    basePrice
    sizes {
      id
      name
      price
    }
  }
}
```

### **3. Create Order:**

```graphql
mutation CreatePOSOrder($input: CreatePOSOrderInput!) {
  createPOSOrder(input: $input) {
    success
    order {
      id
      orderNumber
      total
      status
      items {
        product { name }
        size { name }
        quantity
        price
      }
    }
  }
}
```

---

## 🛠️ View All POS Users

### **Query All Staff:**

```graphql
query AllPOSUsers {
  allUsers(role: "staff") {
    id
    username
    email
    firstName
    lastName
    phone
    role
    isActive
    isStaffMember
    permissions
    canManageOrders
    canViewReports
  }
}
```

---

## ✏️ Update POS User Permissions

### **Update User:**

```graphql
mutation UpdatePOSUser($id: ID!, $input: TeamMemberInput!) {
  updateTeamMember(id: $id, input: $input) {
    success
    user {
      id
      username
      permissions
    }
  }
}
```

**Variables:**
```json
{
  "id": "5",
  "input": {
    "canViewReports": true,
    "canManageReviews": true
  }
}
```

---

## 🗑️ Deactivate POS User

### **Deactivate (Don't Delete):**

```graphql
mutation DeactivateUser($id: ID!) {
  updateTeamMember(id: $id, input: { isActive: false }) {
    success
    user {
      id
      username
      isActive
    }
  }
}
```

---

## 📊 Quick Reference Table

| User Type | Orders | Products | Categories | Promotions | Reports | Reviews |
|-----------|--------|----------|------------|------------|---------|---------|
| **Cashier** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Shift Manager** | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Store Manager** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Admin** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## ⚠️ Important Notes

1. **Only Admins Can Create Users:** You must be logged in as admin to use the `register` mutation.

2. **Password Requirements:** Minimum 8 characters (enforced by Django).

3. **Unique Username/Email:** Username and email must be unique.

4. **POS Access:** Any user with `role: "staff"` or `role: "admin"` can access POS.

5. **Session-Based Auth:** Uses Django sessions, so cookies must be enabled.

---

## 🎯 Quick Copy-Paste Examples

### **Create Cashier:**
```graphql
mutation {
  register(input: {
    username: "cashier1"
    email: "cashier1@store.com"
    password: "password123"
    passwordConfirm: "password123"
    firstName: "John"
    lastName: "Doe"
    role: "staff"
    canManageOrders: true
  }) {
    success
    user { id username }
  }
}
```

### **Create Manager:**
```graphql
mutation {
  register(input: {
    username: "manager1"
    email: "manager1@store.com"
    password: "password123"
    passwordConfirm: "password123"
    firstName: "Jane"
    lastName: "Smith"
    role: "staff"
    canManageOrders: true
    canViewReports: true
    canManageReviews: true
  }) {
    success
    user { id username permissions }
  }
}
```

---

**That's it! Your POS users are ready to work!** 🎉
