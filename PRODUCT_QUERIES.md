# 🍕 Product GraphQL Queries

Complete collection of all product-related GraphQL queries ready to use.

**GraphQL Endpoint:** `http://localhost:8000/graphql/`

---

## 📦 **Product Queries**

### Get All Products
```graphql
query {
  allProducts {
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
      slug
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
      category
      priceModifier
      displayOrder
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

### Get Single Product
```graphql
query GetProduct($id: ID!) {
  product(id: $id) {
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
      description
    }
    tags {
      id
      name
      slug
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
      category
      priceModifier
      displayOrder
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
    reviews {
      id
      customerName
      rating
      comment
      createdAt
      isApproved
    }
  }
}

# Variables:
{
  "id": "1"
}
```

### Get Products by Category (by ID)
```graphql
query ProductsByCategoryId($categoryId: ID!) {
  productsByCategory(categoryId: $categoryId) {
    id
    name
    shortDescription
    basePrice
    imageUrl
    isAvailable
    isFeatured
    averageRating
    category {
      id
      name
      slug
    }
  }
}

# Variables:
{
  "categoryId": "1"
}
```

### Get Products by Category (by Name)
```graphql
query ProductsByCategoryName($categoryName: String!) {
  productsByCategory(categoryName: $categoryName) {
    id
    name
    basePrice
    imageUrl
    isAvailable
  }
}

# Variables:
{
  "categoryName": "Pizza"
}
```

### Get Products by Category (by Slug)
```graphql
query ProductsByCategorySlug($categorySlug: String!) {
  productsByCategory(categorySlug: $categorySlug) {
    id
    name
    basePrice
    imageUrl
    isAvailable
  }
}

# Variables:
{
  "categorySlug": "pizza"
}
```

### Get Products by Tag (by ID)
```graphql
query ProductsByTagId($tagId: ID!) {
  productsByTag(tagId: $tagId) {
    id
    name
    basePrice
    imageUrl
    isAvailable
    tags {
      id
      name
      color
    }
  }
}

# Variables:
{
  "tagId": "1"
}
```

### Get Products by Tag (by Name)
```graphql
query ProductsByTagName($tagName: String!) {
  productsByTag(tagName: $tagName) {
    id
    name
    basePrice
    imageUrl
  }
}

# Variables:
{
  "tagName": "Vegetarian"
}
```

### Get Products by Tag (by Slug)
```graphql
query ProductsByTagSlug($tagSlug: String!) {
  productsByTag(tagSlug: $tagSlug) {
    id
    name
    basePrice
    imageUrl
  }
}

# Variables:
{
  "tagSlug": "vegetarian"
}
```

### Search Products
```graphql
query SearchProducts($search: String!) {
  searchProducts(search: $search) {
    id
    name
    shortDescription
    description
    basePrice
    imageUrl
    isAvailable
    category {
      id
      name
    }
  }
}

# Variables:
{
  "search": "margherita"
}
```

### Get Available Products Only
```graphql
query {
  availableProducts {
    id
    name
    shortDescription
    basePrice
    imageUrl
    isAvailable
    category {
      id
      name
    }
  }
}
```

### Get Featured Products
```graphql
query FeaturedProducts($limit: Int) {
  featuredProducts(limit: $limit) {
    id
    name
    shortDescription
    basePrice
    imageUrl
    isFeatured
    averageRating
    ratingCount
    category {
      id
      name
    }
  }
}

# Variables (optional):
{
  "limit": 10
}
```

### Get Top Rated Products
```graphql
query TopRatedProducts($limit: Int) {
  topRatedProducts(limit: $limit) {
    id
    name
    shortDescription
    basePrice
    imageUrl
    averageRating
    ratingCount
    category {
      id
      name
    }
  }
}

# Variables (optional):
{
  "limit": 10
}
```

---

## 📁 **Category Queries**

### Get All Categories
```graphql
query {
  allCategories {
    id
    name
    slug
    description
    createdAt
    updatedAt
  }
}
```

### Get Single Category (by ID)
```graphql
query GetCategoryById($id: ID!) {
  category(id: $id) {
    id
    name
    slug
    description
    createdAt
  }
}

# Variables:
{
  "id": "1"
}
```

### Get Single Category (by Slug)
```graphql
query GetCategoryBySlug($slug: String!) {
  category(slug: $slug) {
    id
    name
    slug
    description
  }
}

# Variables:
{
  "slug": "pizza"
}
```

---

## 🏷️ **Tag Queries**

### Get All Tags
```graphql
query {
  allTags {
    id
    name
    slug
    color
  }
}
```

### Get Single Tag
```graphql
query GetTag($id: ID!) {
  tag(id: $id) {
    id
    name
    slug
    color
  }
}

# Variables:
{
  "id": "1"
}
```

---

## 📏 **Size Queries**

### Get All Sizes
```graphql
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
    displayOrder
  }
}
```

### Get Sizes by Category ID
```graphql
query SizesByCategoryId($categoryId: ID!) {
  allSizes(categoryId: $categoryId) {
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
}

# Variables:
{
  "categoryId": "1"
}
```

### Get Sizes by Category Slug
```graphql
query SizesByCategorySlug($categorySlug: String!) {
  allSizes(categorySlug: $categorySlug) {
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
}

# Variables:
{
  "categorySlug": "pizza"
}
```

### Get Single Size
```graphql
query GetSize($id: ID!) {
  size(id: $id) {
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
}

# Variables:
{
  "id": "1"
}
```

---

## 🧀 **Topping Queries**

### Get All Toppings
```graphql
query {
  allToppings {
    id
    name
    price
    createdAt
    updatedAt
  }
}
```

### Get Single Topping
```graphql
query GetTopping($id: ID!) {
  topping(id: $id) {
    id
    name
    price
  }
}

# Variables:
{
  "id": "1"
}
```

---

## 🥬 **Ingredient Queries**

### Get All Ingredients
```graphql
query {
  allIngredients {
    id
    name
    icon
  }
}
```

### Get Single Ingredient
```graphql
query GetIngredient($id: ID!) {
  ingredient(id: $id) {
    id
    name
    icon
  }
}

# Variables:
{
  "id": "1"
}
```

---

## 🍟 **Included Item Queries**

### Get All Included Items
```graphql
query {
  allIncludedItems {
    id
    name
  }
}
```

### Get Single Included Item
```graphql
query GetIncludedItem($id: ID!) {
  includedItem(id: $id) {
    id
    name
  }
}

# Variables:
{
  "id": "1"
}
```

---

## ⭐ **Product Review Queries**

### Get Product Reviews
```graphql
query ProductReviews($productId: ID!) {
  productReviews(productId: $productId) {
    id
    customerName
    customerEmail
    rating
    comment
    isApproved
    createdAt
    updatedAt
  }
}

# Variables:
{
  "productId": "1"
}
```

---

## 🔍 **Combined Queries Examples**

### Get Menu with Categories and Products
```graphql
query GetMenu {
  allCategories {
    id
    name
    slug
    description
  }
  allProducts {
    id
    name
    basePrice
    imageUrl
    category {
      id
      name
    }
  }
}
```

### Get Product with All Related Data
```graphql
query GetProductFull($id: ID!) {
  product(id: $id) {
    id
    name
    shortDescription
    description
    basePrice
    imageUrl
    isAvailable
    isFeatured
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
      category
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
    reviews {
      id
      customerName
      rating
      comment
      createdAt
    }
  }
  allSizes {
    id
    name
    category
    priceModifier
  }
  allToppings {
    id
    name
    price
  }
}

# Variables:
{
  "id": "1"
}
```

### Get Featured Products with Categories
```graphql
query GetFeaturedMenu {
  featuredProducts(limit: 10) {
    id
    name
    shortDescription
    basePrice
    imageUrl
    averageRating
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
  }
  allCategories {
    id
    name
    slug
  }
}
```

### Search with Filters
```graphql
query SearchWithFilters($search: String!, $categoryId: ID) {
  searchProducts(search: $search) {
    id
    name
    basePrice
    imageUrl
    category {
      id
      name
    }
  }
  productsByCategory(categoryId: $categoryId) {
    id
    name
    basePrice
  }
}

# Variables:
{
  "search": "pizza",
  "categoryId": "1"
}
```

---

## 📝 **Usage Tips**

1. **Minimal Queries**: Only request fields you need to reduce payload size
   ```graphql
   query {
     allProducts {
       id
       name
       basePrice
     }
   }
   ```

2. **Nested Queries**: Request related data in one query
   ```graphql
   query {
     allProducts {
       id
       name
       category {
         id
         name
       }
     }
   }
   ```

3. **Variables**: Use variables for dynamic queries
   ```graphql
   query GetProduct($id: ID!) {
     product(id: $id) {
       name
     }
   }
   ```

4. **Error Handling**: Always check for errors in responses
   ```json
   {
     "data": { ... },
     "errors": [ ... ]
   }
   ```

---

## 🚀 **Quick Start Examples**

### Example 1: Get All Pizza Products
```graphql
query {
  category(slug: "pizza") {
    id
    name
  }
  productsByCategory(categorySlug: "pizza") {
    id
    name
    basePrice
    imageUrl
  }
}
```

### Example 2: Get Product Details for Cart
```graphql
query GetProductForCart($id: ID!) {
  product(id: $id) {
    id
    name
    basePrice
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
  }
}

# Variables:
{
  "id": "1"
}
```

### Example 3: Get Menu Structure
```graphql
query GetMenuStructure {
  allCategories {
    id
    name
    slug
  }
  allTags {
    id
    name
    color
  }
  allSizes {
    id
    name
    category
    priceModifier
  }
  allToppings {
    id
    name
    price
  }
}
```

---

**All queries are ready to use! Copy and paste into your GraphQL client.**

