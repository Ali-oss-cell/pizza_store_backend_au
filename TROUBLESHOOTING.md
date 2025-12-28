# 🔧 Troubleshooting Guide

## Common GraphQL Errors and Solutions

---

## ❌ **Error 400: Bad Request**

### Possible Causes:

1. **Field Name Mismatch**
   - GraphQL field names are case-sensitive
   - Use exact field names from schema

2. **Missing Required Arguments**
   - Check if query requires variables
   - Ensure all required fields are provided

3. **Invalid Query Syntax**
   - Check for typos in field names
   - Verify proper GraphQL syntax

4. **Type Mismatch**
   - Variables must match expected types
   - IDs must be strings, not numbers

---

## 🔍 **Debugging Steps**

### Step 1: Check the Actual Error Message

The 400 error should include details. Check:
- Browser console (Network tab → Response)
- Django server logs
- GraphiQL interface at `http://localhost:8000/graphql/`

### Step 2: Test in GraphiQL

Use GraphiQL to test queries directly:

1. Go to `http://localhost:8000/graphql/`
2. Try a simple query first:

```graphql
query {
  allProducts {
    id
    name
  }
}
```

### Step 3: Verify Field Names

**Important:** GraphQL field names use **camelCase** in queries, but the schema defines them in **snake_case**.

| Schema Definition | Query Usage |
|------------------|-------------|
| `all_products` | `allProducts` |
| `product` | `product` |
| `products_by_category` | `productsByCategory` |
| `base_price` | `basePrice` |
| `image_url` | `imageUrl` |
| `is_available` | `isAvailable` |
| `is_featured` | `isFeatured` |
| `is_combo` | `isCombo` |
| `short_description` | `shortDescription` |
| `prep_time_display` | `prepTimeDisplay` |
| `average_rating` | `averageRating` |
| `rating_count` | `ratingCount` |
| `available_sizes` | `availableSizes` |
| `available_toppings` | `availableToppings` |
| `included_items` | `includedItems` |
| `created_at` | `createdAt` |
| `updated_at` | `updatedAt` |

---

## ✅ **Correct Query Examples**

### Simple Product Query
```graphql
query {
  allProducts {
    id
    name
    basePrice
  }
}
```

### Single Product Query
```graphql
query GetProduct($id: ID!) {
  product(id: $id) {
    id
    name
    basePrice
    imageUrl
  }
}

# Variables (must be JSON):
{
  "id": "1"
}
```

### Product with All Fields
```graphql
query {
  product(id: "1") {
    id
    name
    shortDescription
    description
    basePrice
    imageUrl
    isAvailable
    isFeatured
    isCombo
    prepTimeDisplay
    averageRating
    ratingCount
    calories
    category {
      id
      name
      slug
    }
    tags {
      id
      name
      color
    }
    ingredients {
      id
      name
      icon
    }
    availableSizes {
      id
      name
      priceModifier
    }
    availableToppings {
      id
      name
      price
    }
    includedItems {
      id
      name
    }
  }
}
```

---

## 🐛 **Common Issues**

### Issue 1: Product Not Found (Returns null)

**Problem:** Query returns `null` for product

**Cause:** Product might be `is_available=False` or doesn't exist

**Solution:**
```graphql
# Use allProducts to see all products (including unavailable)
query {
  allProducts {
    id
    name
    isAvailable
  }
}
```

### Issue 2: Field Does Not Exist Error

**Problem:** `Cannot query field "X" on type "Y"`

**Cause:** Field name typo or field doesn't exist

**Solution:** Check exact field names (use camelCase)

### Issue 3: Variable Type Mismatch

**Problem:** `Variable "$id" got invalid value`

**Cause:** ID passed as number instead of string

**Solution:**
```json
// ❌ Wrong
{
  "id": 1
}

// ✅ Correct
{
  "id": "1"
}
```

### Issue 4: Missing Required Argument

**Problem:** `Field "product" argument "id" of type "ID!" is required`

**Cause:** Missing required `id` argument

**Solution:**
```graphql
# ❌ Wrong
query {
  product {
    name
  }
}

# ✅ Correct
query {
  product(id: "1") {
    name
  }
}
```

---

## 🔐 **Authentication Issues**

### Issue: "Authentication required" or "Only admins can..."

**Solution:** Login first:
```graphql
mutation {
  login(input: {
    username: "admin"
    password: "admin123"
  }) {
    user {
      id
      role
    }
    success
  }
}
```

---

## 📝 **Testing Checklist**

- [ ] Server is running (`python manage.py runserver`)
- [ ] GraphQL endpoint accessible (`http://localhost:8000/graphql/`)
- [ ] Query syntax is correct
- [ ] Field names use camelCase
- [ ] Variables are provided (if required)
- [ ] Variable types match (IDs as strings)
- [ ] Product exists in database
- [ ] Product is available (if using `product` query)
- [ ] Authentication is set (for mutations)

---

## 🧪 **Quick Test Queries**

### Test 1: Basic Query
```graphql
query {
  allCategories {
    id
    name
  }
}
```

### Test 2: Product Query
```graphql
query {
  allProducts {
    id
    name
  }
}
```

### Test 3: Single Product
```graphql
query {
  product(id: "1") {
    id
    name
    basePrice
  }
}
```

### Test 4: With Variables
```graphql
query GetProduct($id: ID!) {
  product(id: $id) {
    id
    name
  }
}
```
Variables:
```json
{
  "id": "1"
}
```

---

## 🔍 **How to See Full Error Details**

### Method 1: GraphiQL Interface
1. Open `http://localhost:8000/graphql/`
2. Enter your query
3. Click "Execute Query"
4. Check the error panel at the bottom

### Method 2: Browser DevTools
1. Open Network tab
2. Find the GraphQL request
3. Click on it
4. Check "Response" tab for error details

### Method 3: Django Server Logs
Check the terminal where `runserver` is running for detailed error messages.

---

## 💡 **Best Practices**

1. **Start Simple**: Test with minimal fields first
2. **Use GraphiQL**: Test queries in GraphiQL before using in frontend
3. **Check Field Names**: Always use camelCase in queries
4. **Validate Variables**: Ensure types match (IDs as strings)
5. **Handle Errors**: Always check for errors in response

---

## 📞 **Still Having Issues?**

1. Check Django server logs for detailed error
2. Test query in GraphiQL interface
3. Verify database has data
4. Check if product exists and is available
5. Ensure correct field names (camelCase)

---

**Most Common Fix:** Use camelCase field names and ensure IDs are strings!

