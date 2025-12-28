# 🧪 First Things to Test

## ✅ Test 1: GraphQL Endpoint & Basic Query

**Step 1:** Open GraphiQL
- Go to: `http://localhost:8000/graphql/`

**Step 2:** Run this query in the left panel:

```graphql
query {
  allCategories {
    id
    name
    slug
    description
  }
}
```

**Expected Result:** You should see all categories (Pizza, Pasta, Drinks, etc.)

---

## ✅ Test 2: Get Products

**Query:**
```graphql
query {
  allProducts {
    id
    name
    basePrice
    isAvailable
    category {
      name
    }
  }
}
```

**Expected Result:** List of all products with prices

---

## ✅ Test 3: Test Cart (Session-Based)

**Step 1:** Add item to cart
```graphql
mutation {
  addToCart(input: {
    productId: "1"
    quantity: 2
  }) {
    success
    message
    cart {
      total
      itemCount
    }
    cartItem {
      id
      product {
        name
      }
      quantity
      subtotal
    }
  }
}
```

**Step 2:** View cart
```graphql
query {
  cart {
    total
    itemCount
    items {
      id
      product {
        name
        basePrice
      }
      quantity
      subtotal
    }
  }
}
```

**Expected Result:** Cart should persist using session (no login needed!)

---

## ✅ Test 4: Admin Login

**Query:**
```graphql
mutation {
  login(input: {
    username: "admin"
    password: "admin"
  }) {
    success
    message
    user {
      id
      username
      email
      role
      isAdmin
    }
  }
}
```

**Expected Result:** Login successful, returns user info

---

## ✅ Test 5: Get Current User (After Login)

**Query:**
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

**Expected Result:** Returns your logged-in user info

---

## 🎯 **START HERE: Test 1**

The simplest test is **Test 1** - just check if GraphQL is working and you can fetch categories!

