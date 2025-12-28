# 🔄 Frontend Update: Size Category Relationship

## ⚠️ **Important Change**

The Size model's `category` field has been updated from a **string** to a **ForeignKey** relationship with the Category model.

**Date:** December 28, 2025

---

## 📋 **What Changed**

### Before (Old)
- Size category was a string field with limited choices: `'pizza'`, `'drink'`, `'pasta'`, `'other'`
- Frontend sent: `category: "pizza"` (string)

### After (New)
- Size category is now a ForeignKey to Category model
- Frontend must send: `categoryId: "1"` (Category ID)

---

## 🔧 **Required Frontend Updates**

### 1. **Create Size Mutation**

#### ❌ Old Format
```graphql
mutation CreateSize($input: SizeInput!) {
  createSize(input: $input) {
    size {
      id
      name
      category
      priceModifier
    }
    success
  }
}

# Variables (OLD - Don't use):
{
  "input": {
    "name": "Large",
    "category": "pizza",  // ❌ String - no longer works
    "priceModifier": "3.00"
  }
}
```

#### ✅ New Format
```graphql
mutation CreateSize($input: SizeInput!) {
  createSize(input: $input) {
    size {
      id
      name
      category {
        id
        name
        slug
      }
      priceModifier
      displayOrder
    }
    success
    message
  }
}

# Variables (NEW - Use this):
{
  "input": {
    "name": "Large",
    "categoryId": "1",  // ✅ Category ID (required)
    "priceModifier": "3.00",
    "displayOrder": 3
  }
}
```

### 2. **Update Size Mutation**

#### ❌ Old Format
```graphql
mutation UpdateSize($id: ID!, $input: SizeInput!) {
  updateSize(id: $id, input: $input) {
    size {
      id
      name
      category
    }
    success
  }
}

# Variables (OLD):
{
  "id": "1",
  "input": {
    "category": "pizza"  // ❌ String - no longer works
  }
}
```

#### ✅ New Format
```graphql
mutation UpdateSize($id: ID!, $input: SizeInput!) {
  updateSize(id: $id, input: $input) {
    size {
      id
      name
      category {
        id
        name
        slug
      }
      priceModifier
    }
    success
    message
  }
}

# Variables (NEW):
{
  "id": "1",
  "input": {
    "categoryId": "2"  // ✅ Category ID to change category
  }
}
```

### 3. **Query Sizes**

#### ❌ Old Format
```graphql
query {
  allSizes(category: "pizza") {  // ❌ String filter - no longer works
    id
    name
    category
    priceModifier
  }
}
```

#### ✅ New Format
```graphql
# Option 1: Filter by Category ID
query {
  allSizes(categoryId: "1") {
    id
    name
    category {
      id
      name
      slug
    }
    priceModifier
  }
}

# Option 2: Filter by Category Slug
query {
  allSizes(categorySlug: "pizza") {
    id
    name
    category {
      id
      name
      slug
    }
    priceModifier
  }
}

# Option 3: Get All Sizes
query {
  allSizes {
    id
    name
    category {
      id
      name
      slug
    }
    priceModifier
  }
}
```

### 4. **Size Response Structure**

#### ❌ Old Response
```json
{
  "data": {
    "size": {
      "id": "1",
      "name": "Large",
      "category": "pizza",  // ❌ String
      "priceModifier": "3.00"
    }
  }
}
```

#### ✅ New Response
```json
{
  "data": {
    "size": {
      "id": "1",
      "name": "Large",
      "category": {  // ✅ Object
        "id": "1",
        "name": "Pizza",
        "slug": "pizza"
      },
      "priceModifier": "3.00",
      "displayOrder": 3
    }
  }
}
```

---

## 📝 **Field Mapping**

| Old Field | New Field | Type | Required | Notes |
|-----------|-----------|------|----------|-------|
| `category` (string) | `categoryId` | ID | ✅ Yes | Must be valid Category ID |
| - | `category` (object) | CategoryType | - | Returned in queries (read-only) |

---

## 🔍 **How to Get Category IDs**

### Query All Categories First
```graphql
query {
  allCategories {
    id
    name
    slug
  }
}
```

**Response:**
```json
{
  "data": {
    "allCategories": [
      {
        "id": "1",
        "name": "Pizza",
        "slug": "pizza"
      },
      {
        "id": "2",
        "name": "Pasta",
        "slug": "pasta"
      },
      {
        "id": "3",
        "name": "Drinks",
        "slug": "drinks"
      }
    ]
  }
}
```

Then use the `id` when creating/updating sizes.

---

## ✅ **Updated Input Types**

### SizeInput (Updated)
```graphql
{
  name: String! (required)
  categoryId: ID! (required)  # ✅ Changed from category: String
  priceModifier: Decimal (optional)
  displayOrder: Int (optional)
}
```

### SizeType (Updated Response)
```graphql
{
  id: ID
  name: String
  category: CategoryType {  # ✅ Now returns Category object
    id: ID
    name: String
    slug: String
  }
  priceModifier: Decimal
  displayOrder: Int
}
```

---

## 🚨 **Breaking Changes**

### 1. **Create Size Mutation**
- ❌ **BREAKING:** `category: "pizza"` no longer works
- ✅ **REQUIRED:** `categoryId: "1"` must be provided

### 2. **Update Size Mutation**
- ❌ **BREAKING:** `category: "pizza"` no longer works
- ✅ **USE:** `categoryId: "1"` to change category

### 3. **Query Sizes**
- ❌ **BREAKING:** `allSizes(category: "pizza")` no longer works
- ✅ **USE:** `allSizes(categoryId: "1")` or `allSizes(categorySlug: "pizza")`

### 4. **Response Structure**
- ❌ **BREAKING:** `category` is no longer a string
- ✅ **NEW:** `category` is now an object with `id`, `name`, `slug`

---

## 🔄 **Migration Steps for Frontend**

### Step 1: Update Size Creation Forms
- Replace `category` dropdown with Category ID selection
- Query categories first to get IDs
- Store category IDs in your form state

### Step 2: Update Size Update Forms
- Use `categoryId` instead of `category` string
- Load current size's category ID from response

### Step 3: Update Size Queries
- Change `category: "pizza"` to `categoryId: "1"` or `categorySlug: "pizza"`
- Update response handling to access `category.id`, `category.name`, etc.

### Step 4: Update Display Components
- Change from displaying `size.category` (string) to `size.category.name` (object property)
- Update any filters or sorting that used category strings

---

## 📋 **Checklist for Frontend Team**

- [ ] Update all `createSize` mutations to use `categoryId` instead of `category` string
- [ ] Update all `updateSize` mutations to use `categoryId` instead of `category` string
- [ ] Update all size queries to use `categoryId` or `categorySlug` filters
- [ ] Update response handling to access `category` as object (not string)
- [ ] Update UI components to display `category.name` instead of `category`
- [ ] Update any category filtering logic
- [ ] Test all size-related operations
- [ ] Update TypeScript/JavaScript types/interfaces if used

---

## 💡 **Benefits of This Change**

1. **Data Integrity:** Categories are validated - can't create size with invalid category
2. **Flexibility:** No limit on category types (was limited to 4)
3. **Consistency:** Both Product and Size use same Category model
4. **Better Queries:** Can filter by category ID, slug, or name
5. **Future-Proof:** Easy to add new categories without code changes

---

## 🆘 **Need Help?**

If you encounter any issues:

1. **Check Error Messages:** Backend will return clear errors if category ID is invalid
2. **Verify Category Exists:** Query categories first to ensure ID exists
3. **Test in GraphiQL:** Use `http://localhost:8000/graphql/` to test queries

---

## 📞 **Example: Complete Size Creation Flow**

```graphql
# Step 1: Get available categories
query {
  allCategories {
    id
    name
    slug
  }
}

# Step 2: Create size with category ID
mutation CreateSize($input: SizeInput!) {
  createSize(input: $input) {
    size {
      id
      name
      category {
        id
        name
        slug
      }
      priceModifier
      displayOrder
    }
    success
    message
  }
}

# Variables:
{
  "input": {
    "name": "Large",
    "categoryId": "1",  # From Step 1
    "priceModifier": "3.00",
    "displayOrder": 3
  }
}
```

---

**All size-related operations must be updated to use `categoryId` instead of `category` string!**

