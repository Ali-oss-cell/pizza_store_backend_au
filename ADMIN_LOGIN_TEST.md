# 🔐 Admin Login Test

## ✅ Your Admin Credentials:

```
Username: admin
Email: admin@admin.com
Password: admin123
Role: Admin
```

---

## 🧪 Test Admin Login via GraphQL

**Step 1:** Open GraphiQL
- Go to: `http://localhost:8000/graphql/`

**Step 2:** Run this login mutation:

```graphql
mutation {
  login(input: {
    username: "admin"
    password: "admin123"
  }) {
    success
    message
    user {
      id
      username
      email
      role
      isAdmin
      isStaffMember
    }
  }
}
```

**Expected Result:**
```json
{
  "data": {
    "login": {
      "success": true,
      "message": "Login successful",
      "user": {
        "id": "1",
        "username": "admin",
        "email": "admin@admin.com",
        "role": "ADMIN",
        "isAdmin": true,
        "isStaffMember": false
      }
    }
  }
}
```

---

## ✅ Test 2: Get Current User (After Login)

After logging in, test the `me` query:

```graphql
query {
  me {
    id
    username
    email
    role
    isAdmin
    isStaffMember
  }
}
```

**Expected Result:** Should return your admin user info

---

## ✅ Test 3: Admin-Only Operations

Once logged in, try admin-only mutations like creating a product:

```graphql
mutation {
  createProduct(input: {
    name: "Test Pizza"
    description: "A test pizza"
    basePrice: "12.99"
    categoryId: "1"
    isAvailable: true
  }) {
    product {
      id
      name
      basePrice
    }
    success
    message
  }
}
```

---

## 🎯 Next Steps:

1. ✅ Test login (above)
2. ✅ Test `me` query
3. ✅ Test creating a product
4. ✅ Test viewing orders
5. ✅ Test updating order status

Your admin account is ready to use! 🚀

