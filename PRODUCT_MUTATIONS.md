# 🍕 Product GraphQL Mutations

Complete collection of all product-related GraphQL mutations for admin management.

**GraphQL Endpoint:** `http://localhost:8000/graphql/`

**⚠️ All mutations require Admin authentication!**

---

## 📦 **Product Mutations**

### Create Product
```graphql
mutation CreateProduct($input: ProductInput!) {
  createProduct(input: $input) {
    product {
      id
      name
      shortDescription
      basePrice
      imageUrl
      isAvailable
      isFeatured
      category {
        id
        name
      }
    }
    success
    message
  }
}

# Variables:
{
  "input": {
    "name": "Margherita Pizza",
    "shortDescription": "Classic Italian pizza",
    "description": "Fresh mozzarella, tomato sauce, basil",
    "basePrice": "14.99",
    "categoryId": "1",
    "tagIds": ["1", "2"],
    "ingredientIds": ["1", "2", "3"],
    "sizeIds": ["1", "2", "3"],
    "toppingIds": ["1", "2"],
    "includedItemIds": [],
    "isAvailable": true,
    "isFeatured": true,
    "isCombo": false,
    "prepTimeMin": 15,
    "prepTimeMax": 20,
    "calories": 250,
    "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
  }
}
```

### Update Product
```graphql
mutation UpdateProduct($id: ID!, $input: ProductInput!) {
  updateProduct(id: $id, input: $input) {
    product {
      id
      name
      basePrice
      imageUrl
      isAvailable
    }
    success
    message
  }
}

# Variables:
{
  "id": "1",
  "input": {
    "name": "Updated Margherita Pizza",
    "basePrice": "15.99",
    "isFeatured": false,
    "tagIds": ["1"]
  }
}
```

### Delete Product
```graphql
mutation DeleteProduct($id: ID!) {
  deleteProduct(id: $id) {
    success
    message
  }
}

# Variables:
{
  "id": "1"
}
```

---

## 📁 **Category Mutations**

### Create Category
```graphql
mutation CreateCategory($input: CategoryInput!) {
  createCategory(input: $input) {
    category {
      id
      name
      slug
      description
    }
    success
    message
  }
}

# Variables:
{
  "input": {
    "name": "Pizza",
    "slug": "pizza",
    "description": "All pizza varieties"
  }
}
```

### Update Category
```graphql
mutation UpdateCategory($id: ID!, $input: CategoryInput!) {
  updateCategory(id: $id, input: $input) {
    category {
      id
      name
      slug
      description
    }
    success
    message
  }
}

# Variables:
{
  "id": "1",
  "input": {
    "name": "Pizzas",
    "description": "Updated description"
  }
}
```

### Delete Category
```graphql
mutation DeleteCategory($id: ID!) {
  deleteCategory(id: $id) {
    success
    message
  }
}

# Variables:
{
  "id": "1"
}
```

---

## 🏷️ **Tag Mutations**

### Create Tag
```graphql
mutation CreateTag($input: TagInput!) {
  createTag(input: $input) {
    tag {
      id
      name
      slug
      color
    }
    success
    message
  }
}

# Variables:
{
  "input": {
    "name": "Vegetarian",
    "slug": "vegetarian",
    "color": "#4CAF50"
  }
}
```

### Update Tag
```graphql
mutation UpdateTag($id: ID!, $input: TagInput!) {
  updateTag(id: $id, input: $input) {
    tag {
      id
      name
      slug
      color
    }
    success
    message
  }
}

# Variables:
{
  "id": "1",
  "input": {
    "name": "Veggie",
    "color": "#66BB6A"
  }
}
```

### Delete Tag
```graphql
mutation DeleteTag($id: ID!) {
  deleteTag(id: $id) {
    success
    message
  }
}

# Variables:
{
  "id": "1"
}
```

---

## 📏 **Size Mutations**

### Create Size
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

# Variables:
{
  "input": {
    "name": "Large",
    "categoryId": "1",
    "priceModifier": "3.00",
    "displayOrder": 3
  }
}
```

**Note:** `categoryId` must be a valid Category ID (ForeignKey to Category model)

### Update Size
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

# Variables:
{
  "id": "1",
  "input": {
    "name": "Extra Large",
    "priceModifier": "5.00"
  }
}
```

### Delete Size
```graphql
mutation DeleteSize($id: ID!) {
  deleteSize(id: $id) {
    success
    message
  }
}

# Variables:
{
  "id": "1"
}
```

---

## 🧀 **Topping Mutations**

### Create Topping
```graphql
mutation CreateTopping($input: ToppingInput!) {
  createTopping(input: $input) {
    topping {
      id
      name
      price
    }
    success
    message
  }
}

# Variables:
{
  "input": {
    "name": "Extra Cheese",
    "price": "2.00"
  }
}
```

### Update Topping
```graphql
mutation UpdateTopping($id: ID!, $input: ToppingInput!) {
  updateTopping(id: $id, input: $input) {
    topping {
      id
      name
      price
    }
    success
    message
  }
}

# Variables:
{
  "id": "1",
  "input": {
    "name": "Double Cheese",
    "price": "3.00"
  }
}
```

### Delete Topping
```graphql
mutation DeleteTopping($id: ID!) {
  deleteTopping(id: $id) {
    success
    message
  }
}

# Variables:
{
  "id": "1"
}
```

---

## 🥬 **Ingredient Mutations**

### Create Ingredient
```graphql
mutation CreateIngredient($input: IngredientInput!) {
  createIngredient(input: $input) {
    ingredient {
      id
      name
      icon
    }
    success
    message
  }
}

# Variables:
{
  "input": {
    "name": "Mushrooms",
    "icon": "🍄"
  }
}
```

### Update Ingredient
```graphql
mutation UpdateIngredient($id: ID!, $input: IngredientInput!) {
  updateIngredient(id: $id, input: $input) {
    ingredient {
      id
      name
      icon
    }
    success
    message
  }
}

# Variables:
{
  "id": "1",
  "input": {
    "name": "Fresh Mushrooms",
    "icon": "🍄"
  }
}
```

### Delete Ingredient
```graphql
mutation DeleteIngredient($id: ID!) {
  deleteIngredient(id: $id) {
    success
    message
  }
}

# Variables:
{
  "id": "1"
}
```

---

## 🍟 **Included Item Mutations**

### Create Included Item
```graphql
mutation CreateIncludedItem($input: IncludedItemInput!) {
  createIncludedItem(input: $input) {
    includedItem {
      id
      name
    }
    success
    message
  }
}

# Variables:
{
  "input": {
    "name": "Chips"
  }
}
```

### Update Included Item
```graphql
mutation UpdateIncludedItem($id: ID!, $input: IncludedItemInput!) {
  updateIncludedItem(id: $id, input: $input) {
    includedItem {
      id
      name
    }
    success
    message
  }
}

# Variables:
{
  "id": "1",
  "input": {
    "name": "French Fries"
  }
}
```

### Delete Included Item
```graphql
mutation DeleteIncludedItem($id: ID!) {
  deleteIncludedItem(id: $id) {
    success
    message
  }
}

# Variables:
{
  "id": "1"
}
```

---

## ⭐ **Product Review Mutations**

### Submit Review (Public - No Auth Required)
```graphql
mutation SubmitReview($input: ProductReviewInput!) {
  submitReview(input: $input) {
    review {
      id
      customerName
      rating
      comment
      isApproved
    }
    success
    message
  }
}

# Variables:
{
  "input": {
    "productId": "1",
    "customerName": "Jane Doe",
    "customerEmail": "jane@example.com",
    "rating": 5,
    "comment": "Amazing pizza! Best I've ever had."
  }
}
```

**Note:** Reviews require admin approval before being visible.

### Approve Review (Admin Only)
```graphql
mutation ApproveReview($id: ID!, $approve: Boolean!) {
  approveReview(id: $id, approve: $approve) {
    review {
      id
      customerName
      rating
      comment
      isApproved
    }
    success
    message
  }
}

# Variables:
{
  "id": "1",
  "approve": true
}
```

### Delete Review (Admin Only)
```graphql
mutation DeleteReview($id: ID!) {
  deleteReview(id: $id) {
    success
    message
  }
}

# Variables:
{
  "id": "1"
}
```

---

## 📝 **Input Type Reference**

### ProductInput
```graphql
{
  name: String! (required)
  shortDescription: String
  description: String
  basePrice: Decimal! (required)
  categoryId: ID! (required)
  tagIds: [ID]
  ingredientIds: [ID]
  sizeIds: [ID]
  toppingIds: [ID]
  includedItemIds: [ID]
  isAvailable: Boolean
  isFeatured: Boolean
  isCombo: Boolean
  prepTimeMin: Int
  prepTimeMax: Int
  calories: Int
  image: String (base64 encoded: "data:image/jpeg;base64,...")
}
```

### CategoryInput
```graphql
{
  name: String! (required)
  slug: String (auto-generated if not provided)
  description: String
}
```

### TagInput
```graphql
{
  name: String! (required)
  slug: String
  color: String (hex color, default: "#000000")
}
```

### SizeInput
```graphql
{
  name: String! (required)
  categoryId: ID! (required) - ForeignKey to Category
  priceModifier: Decimal (can be negative)
  displayOrder: Int
}
```

### ToppingInput
```graphql
{
  name: String! (required)
  price: Decimal! (required)
}
```

### IngredientInput
```graphql
{
  name: String! (required)
  icon: String (emoji or icon name)
}
```

### IncludedItemInput
```graphql
{
  name: String! (required)
}
```

### ProductReviewInput
```graphql
{
  productId: ID! (required)
  customerName: String! (required)
  customerEmail: String! (required)
  rating: Int! (required, 1-5)
  comment: String
}
```

---

## 🔐 **Authentication**

All mutations (except `submitReview`) require:
1. **User must be logged in** (session-based authentication)
2. **User must have Admin role**

### Login First
```graphql
mutation Login($input: LoginInput!) {
  login(input: $input) {
    user {
      id
      username
      role
      isAdmin
    }
    success
    message
  }
}

# Variables:
{
  "input": {
    "username": "admin",
    "password": "admin123"
  }
}
```

---

## 💡 **Usage Examples**

### Example 1: Create a Complete Product
```graphql
mutation CreateCompleteProduct($input: ProductInput!) {
  createProduct(input: $input) {
    product {
      id
      name
      basePrice
      imageUrl
      category {
        id
        name
      }
      tags {
        id
        name
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
    }
    success
    message
  }
}

# Variables:
{
  "input": {
    "name": "Supreme Pizza",
    "shortDescription": "Loaded with toppings",
    "description": "Pepperoni, sausage, mushrooms, peppers, onions, olives",
    "basePrice": "18.99",
    "categoryId": "1",
    "tagIds": ["1", "2"],
    "ingredientIds": ["1", "2", "3", "4"],
    "sizeIds": ["1", "2", "3"],
    "toppingIds": ["1", "2", "3"],
    "isAvailable": true,
    "isFeatured": true,
    "prepTimeMin": 20,
    "prepTimeMax": 25,
    "calories": 350
  }
}
```

### Example 2: Update Product Price and Availability
```graphql
mutation UpdateProductPrice($id: ID!, $input: ProductInput!) {
  updateProduct(id: $id, input: $input) {
    product {
      id
      name
      basePrice
      isAvailable
    }
    success
    message
  }
}

# Variables:
{
  "id": "1",
  "input": {
    "basePrice": "16.99",
    "isAvailable": false
  }
}
```

### Example 3: Bulk Update Product Tags
```graphql
mutation UpdateProductTags($id: ID!, $input: ProductInput!) {
  updateProduct(id: $id, input: $input) {
    product {
      id
      name
      tags {
        id
        name
        color
      }
    }
    success
    message
  }
}

# Variables:
{
  "id": "1",
  "input": {
    "tagIds": ["1", "3", "5"]
  }
}
```

### Example 4: Create Category with Products
```graphql
# Step 1: Create Category
mutation CreateCategory($input: CategoryInput!) {
  createCategory(input: $input) {
    category {
      id
      name
      slug
    }
    success
    message
  }
}

# Step 2: Create Products in that Category
mutation CreateProducts($input1: ProductInput!, $input2: ProductInput!) {
  product1: createProduct(input: $input1) {
    product {
      id
      name
      category {
        id
        name
      }
    }
    success
  }
  product2: createProduct(input: $input2) {
    product {
      id
      name
      category {
        id
        name
      }
    }
    success
  }
}
```

---

## ⚠️ **Important Notes**

### 1. **Price Format**
- All prices must be **strings** in mutations: `"14.99"` not `14.99`
- GraphQL Decimal type expects string input

### 2. **Image Upload**
- Use base64 encoding: `"data:image/jpeg;base64,/9j/4AAQSkZJRg..."`
- Supported formats: PNG, JPEG, GIF, WebP
- Image is optional in ProductInput

### 3. **Array Fields**
- `tagIds`, `ingredientIds`, `sizeIds`, `toppingIds`, `includedItemIds` are arrays
- Use empty array `[]` to clear all relationships
- Use `null` to keep existing relationships unchanged (update only)

### 4. **Update Behavior**
- In `updateProduct`, only provide fields you want to change
- Array fields: `null` = keep existing, `[]` = clear all, `["1", "2"]` = replace with these

### 5. **Error Handling**
- Always check `success` field in response
- Check `message` for error details
- GraphQL errors will be in `errors` array

### 6. **Review Approval**
- Reviews are submitted with `isApproved: false`
- Admin must approve before they appear in product reviews
- Product rating is automatically updated when review is approved/rejected/deleted

---

## 🚀 **Quick Reference**

| Mutation | Auth Required | Description |
|----------|---------------|-------------|
| `createProduct` | Admin | Create new product |
| `updateProduct` | Admin | Update existing product |
| `deleteProduct` | Admin | Delete product |
| `createCategory` | Admin | Create category |
| `updateCategory` | Admin | Update category |
| `deleteCategory` | Admin | Delete category |
| `createTag` | Admin | Create tag |
| `updateTag` | Admin | Update tag |
| `deleteTag` | Admin | Delete tag |
| `createSize` | Admin | Create size |
| `updateSize` | Admin | Update size |
| `deleteSize` | Admin | Delete size |
| `createTopping` | Admin | Create topping |
| `updateTopping` | Admin | Update topping |
| `deleteTopping` | Admin | Delete topping |
| `createIngredient` | Admin | Create ingredient |
| `updateIngredient` | Admin | Update ingredient |
| `deleteIngredient` | Admin | Delete ingredient |
| `createIncludedItem` | Admin | Create included item |
| `updateIncludedItem` | Admin | Update included item |
| `deleteIncludedItem` | Admin | Delete included item |
| `submitReview` | Public | Submit review (requires approval) |
| `approveReview` | Admin | Approve/reject review |
| `deleteReview` | Admin | Delete review |

---

**All mutations are ready to use! Remember to authenticate as admin first.**

