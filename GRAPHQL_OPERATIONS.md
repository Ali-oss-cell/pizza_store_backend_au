# 📋 Complete GraphQL Operations for Frontend

**GraphQL Endpoint:** `http://localhost:8000/graphql/`

---

## 🔐 **AUTHENTICATION**

### Login
```graphql
mutation Login($input: LoginInput!) {
  login(input: $input) {
    user {
      id
      username
      email
      role
      isAdmin
      isStaffMember
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

### Logout
```graphql
mutation {
  logout {
    success
    message
  }
}
```

### Get Current User
```graphql
query {
  me {
    id
    username
    email
    role
    isAdmin
    isStaffMember
    firstName
    lastName
    isActive
    dateJoined
  }
}
```

### Register (Admin Only)
```graphql
mutation Register($input: RegisterInput!) {
  register(input: $input) {
    user {
      id
      username
      email
      role
    }
    success
    message
  }
}

# Variables:
{
  "input": {
    "username": "staff1",
    "email": "staff1@example.com",
    "password": "password123",
    "passwordConfirm": "password123",
    "firstName": "John",
    "lastName": "Doe",
    "role": "staff"
  }
}
```

### Change Password
```graphql
mutation ChangePassword($oldPassword: String!, $newPassword: String!, $newPasswordConfirm: String!) {
  changePassword(
    oldPassword: $oldPassword
    newPassword: $newPassword
    newPasswordConfirm: $newPasswordConfirm
  ) {
    success
    message
  }
}
```

### Update User
```graphql
mutation UpdateUser($userId: ID, $email: String, $firstName: String, $lastName: String, $role: String, $isActive: Boolean) {
  updateUser(
    userId: $userId
    email: $email
    first_name: $firstName
    last_name: $lastName
    role: $role
    isActive: $isActive
  ) {
    user {
      id
      username
      email
      role
      isActive
    }
    success
    message
  }
}
```

---

## 🍕 **PRODUCTS**

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
    }
  }
}
```

### Get Products by Category
```graphql
query ProductsByCategory($categoryId: ID, $categoryName: String, $categorySlug: String) {
  productsByCategory(categoryId: $categoryId, categoryName: $categoryName, categorySlug: $categorySlug) {
    id
    name
    basePrice
    imageUrl
    isAvailable
  }
}
```

### Get Products by Tag
```graphql
query ProductsByTag($tagId: ID, $tagName: String, $tagSlug: String) {
  productsByTag(tagId: $tagId, tagName: $tagName, tagSlug: $tagSlug) {
    id
    name
    basePrice
    imageUrl
  }
}
```

### Search Products
```graphql
query SearchProducts($search: String!) {
  searchProducts(search: $search) {
    id
    name
    basePrice
    imageUrl
    shortDescription
  }
}
```

### Get Available Products Only
```graphql
query {
  availableProducts {
    id
    name
    basePrice
    imageUrl
  }
}
```

### Get Featured Products
```graphql
query FeaturedProducts($limit: Int) {
  featuredProducts(limit: $limit) {
    id
    name
    basePrice
    imageUrl
    averageRating
    shortDescription
  }
}
```

### Get Top Rated Products
```graphql
query TopRatedProducts($limit: Int) {
  topRatedProducts(limit: $limit) {
    id
    name
    basePrice
    imageUrl
    averageRating
    ratingCount
  }
}
```

### Create Product (Admin Only)
```graphql
mutation CreateProduct($input: ProductInput!) {
  createProduct(input: $input) {
    product {
      id
      name
      basePrice
      imageUrl
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
    "ingredientIds": ["1", "2"],
    "sizeIds": ["1", "2", "3"],
    "toppingIds": ["1", "2"],
    "includedItemIds": [],
    "isAvailable": true,
    "isFeatured": true,
    "isCombo": false,
    "prepTimeMin": 15,
    "prepTimeMax": 20,
    "calories": 250,
    "image": "data:image/jpeg;base64,..."
  }
}
```

### Update Product (Admin Only)
```graphql
mutation UpdateProduct($id: ID!, $input: ProductInput!) {
  updateProduct(id: $id, input: $input) {
    product {
      id
      name
      basePrice
      imageUrl
    }
    success
    message
  }
}
```

### Delete Product (Admin Only)
```graphql
mutation DeleteProduct($id: ID!) {
  deleteProduct(id: $id) {
    success
    message
  }
}
```

---

## 📁 **CATEGORIES**

### Get All Categories
```graphql
query {
  allCategories {
    id
    name
    slug
    description
    createdAt
  }
}
```

### Get Single Category
```graphql
query GetCategory($id: ID, $slug: String) {
  category(id: $id, slug: $slug) {
    id
    name
    slug
    description
  }
}
```

### Create Category (Admin Only)
```graphql
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

# Variables:
{
  "input": {
    "name": "Pizza",
    "slug": "pizza",
    "description": "All pizza varieties"
  }
}
```

### Update Category (Admin Only)
```graphql
mutation UpdateCategory($id: ID!, $input: CategoryInput!) {
  updateCategory(id: $id, input: $input) {
    category {
      id
      name
      slug
    }
    success
    message
  }
}
```

### Delete Category (Admin Only)
```graphql
mutation DeleteCategory($id: ID!) {
  deleteCategory(id: $id) {
    success
    message
  }
}
```

---

## 🏷️ **TAGS**

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
```

### Create Tag (Admin Only)
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

### Update Tag (Admin Only)
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
```

### Delete Tag (Admin Only)
```graphql
mutation DeleteTag($id: ID!) {
  deleteTag(id: $id) {
    success
    message
  }
}
```

---

## 📏 **SIZES**

### Get All Sizes
```graphql
query AllSizes($categoryId: ID, $categorySlug: String) {
  allSizes(categoryId: $categoryId, categorySlug: $categorySlug) {
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

### Get Single Size
```graphql
query GetSize($id: ID!) {
  size(id: $id) {
    id
    name
    category
    priceModifier
    displayOrder
  }
}
```

### Create Size (Admin Only)
```graphql
mutation CreateSize($input: SizeInput!) {
  createSize(input: $input) {
    size {
      id
      name
      category {
        id
        name
      }
      priceModifier
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

### Update Size (Admin Only)
```graphql
mutation UpdateSize($id: ID!, $input: SizeInput!) {
  updateSize(id: $id, input: $input) {
    size {
      id
      name
      category {
        id
        name
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
    "categoryId": "1",
    "priceModifier": "5.00"
  }
}
```

### Delete Size (Admin Only)
```graphql
mutation DeleteSize($id: ID!) {
  deleteSize(id: $id) {
    success
    message
  }
}
```

---

## 🧀 **TOPPINGS**

### Get All Toppings
```graphql
query {
  allToppings {
    id
    name
    price
    createdAt
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
```

### Create Topping (Admin Only)
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

### Update Topping (Admin Only)
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
```

### Delete Topping (Admin Only)
```graphql
mutation DeleteTopping($id: ID!) {
  deleteTopping(id: $id) {
    success
    message
  }
}
```

---

## 🥬 **INGREDIENTS**

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
```

### Create Ingredient (Admin Only)
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

### Update Ingredient (Admin Only)
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
```

### Delete Ingredient (Admin Only)
```graphql
mutation DeleteIngredient($id: ID!) {
  deleteIngredient(id: $id) {
    success
    message
  }
}
```

---

## 🍟 **INCLUDED ITEMS**

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
```

### Create Included Item (Admin Only)
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

### Update Included Item (Admin Only)
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
```

### Delete Included Item (Admin Only)
```graphql
mutation DeleteIncludedItem($id: ID!) {
  deleteIncludedItem(id: $id) {
    success
    message
  }
}
```

---

## 🛒 **CART**

### Get Cart
```graphql
query {
  cart {
    id
    total
    itemCount
    items {
      id
      product {
        id
        name
        basePrice
        imageUrl
      }
      size {
        id
        name
        priceModifier
      }
      quantity
      selectedToppings
      unitPrice
      subtotal
    }
  }
}
```

### Add to Cart
```graphql
mutation AddToCart($input: AddToCartInput!) {
  addToCart(input: $input) {
    cartItem {
      id
      product {
        name
      }
      quantity
      subtotal
    }
    cart {
      total
      itemCount
    }
    success
    message
  }
}

# Variables:
{
  "input": {
    "productId": "1",
    "quantity": 2,
    "sizeId": "2",
    "toppingIds": ["1", "2"]
  }
}
```

### Update Cart Item
```graphql
mutation UpdateCartItem($input: UpdateCartItemInput!) {
  updateCartItem(input: $input) {
    cartItem {
      id
      quantity
      subtotal
    }
    cart {
      total
      itemCount
    }
    success
    message
  }
}

# Variables:
{
  "input": {
    "itemId": "1",
    "quantity": 3,
    "sizeId": "3",
    "toppingIds": ["1"]
  }
}
```

### Remove from Cart
```graphql
mutation RemoveFromCart($itemId: ID!) {
  removeFromCart(itemId: $itemId) {
    cart {
      total
      itemCount
    }
    success
    message
  }
}
```

### Clear Cart
```graphql
mutation {
  clearCart {
    success
    message
  }
}
```

---

## 📦 **ORDERS**

### Get Order
```graphql
query GetOrder($orderNumber: String, $orderId: ID) {
  order(orderNumber: $orderNumber, orderId: $orderId) {
    id
    orderNumber
    customerName
    customerEmail
    customerPhone
    orderType
    orderTypeDisplay
    status
    statusDisplay
    deliveryAddress
    deliveryInstructions
    orderNotes
    subtotal
    deliveryFee
    discountCode
    discountAmount
    total
    items {
      id
      productName
      productId
      sizeName
      selectedToppings
      quantity
      unitPrice
      subtotal
      isCombo
      includedItems
    }
    createdAt
    updatedAt
    completedAt
  }
}
```

### Get All Orders (Staff/Admin Only)
```graphql
query Orders($status: String, $orderType: String, $dateFrom: Date, $dateTo: Date, $limit: Int) {
  orders(status: $status, orderType: $orderType, dateFrom: $dateFrom, dateTo: $dateTo, limit: $limit) {
    id
    orderNumber
    customerName
    customerPhone
    orderType
    orderTypeDisplay
    status
    statusDisplay
    total
    createdAt
    items {
      productName
      quantity
      subtotal
    }
  }
}
```

### Get Recent Orders (Staff/Admin Only)
```graphql
query RecentOrders($limit: Int) {
  recentOrders(limit: $limit) {
    id
    orderNumber
    customerName
    status
    statusDisplay
    total
    createdAt
  }
}
```

### Get Order Stats (Staff/Admin Only)
```graphql
query {
  orderStats {
    totalOrders
    pendingOrders
    preparingOrders
    readyOrders
    completedOrders
    cancelledOrders
    totalRevenue
    todayOrders
    todayRevenue
  }
}
```

### Create Order (Checkout)
```graphql
mutation CreateOrder($input: CreateOrderInput!) {
  createOrder(input: $input) {
    order {
      id
      orderNumber
      customerName
      total
      status
      items {
        productName
        quantity
        subtotal
      }
    }
    success
    message
  }
}

# Variables:
{
  "input": {
    "customerName": "John Doe",
    "customerEmail": "john@example.com",
    "customerPhone": "+1234567890",
    "orderType": "delivery",
    "deliveryAddress": "123 Main St, City, State 12345",
    "deliveryInstructions": "Ring doorbell twice",
    "deliveryFee": "3.00",
    "promotionCode": "SAVE10",
    "orderNotes": "Please make it spicy"
  }
}
```

### Update Order Status (Staff/Admin Only)
```graphql
mutation UpdateOrderStatus($input: UpdateOrderStatusInput!) {
  updateOrderStatus(input: $input) {
    order {
      id
      orderNumber
      status
      statusDisplay
    }
    success
    message
  }
}

# Variables:
{
  "input": {
    "orderId": "1",
    "status": "preparing"
  }
}
```

---

## ⭐ **REVIEWS**

### Get Product Reviews
```graphql
query ProductReviews($productId: ID!) {
  productReviews(productId: $productId) {
    id
    customerName
    rating
    comment
    createdAt
  }
}
```

### Submit Review
```graphql
mutation SubmitReview($input: ProductReviewInput!) {
  submitReview(input: $input) {
    review {
      id
      rating
      comment
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
    "comment": "Amazing pizza!"
  }
}
```

### Approve Review (Admin Only)
```graphql
mutation ApproveReview($id: ID!, $approve: Boolean!) {
  approveReview(id: $id, approve: $approve) {
    review {
      id
      isApproved
    }
    success
    message
  }
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
```

---

## 👥 **TEAM MANAGEMENT (Admin Only)**

### Get All Users
```graphql
query AllUsers($role: String, $isActive: Boolean) {
  allUsers(role: $role, isActive: $isActive) {
    id
    username
    email
    role
    isActive
    dateJoined
    createdAt
  }
}
```

### Get User
```graphql
query GetUser($id: ID!) {
  user(id: $id) {
    id
    username
    email
    role
    isActive
  }
}
```

### Get Team Stats
```graphql
query {
  teamStats
}
```

---

## 💰 **PRICE CALCULATION GUIDE**

### How Prices Work:

1. **Base Price**: Set on `Product.basePrice` (smallest/default size)

2. **Size Modifier**: Added from `Size.priceModifier`
   - Can be positive (+$3.00) or negative (-$1.00)
   - Final price = `basePrice + priceModifier`

3. **Toppings**: Each topping has a `price` field
   - Added to base price
   - Final price = `basePrice + sizeModifier + sum(toppingPrices)`

4. **Cart Item Price Calculation**:
   ```python
   # Location: cart/utils.py::calculate_item_price()
   price = product.base_price
   if size:
       price += size.price_modifier
   if toppings:
       for topping in toppings:
           price += Decimal(str(topping.price))
   ```

5. **Cart Item Subtotal**:
   ```python
   # Location: cart/models.py::CartItem.get_subtotal()
   toppings_total = sum(Decimal(str(t.get('price', 0))) for t in selected_toppings)
   subtotal = (unit_price + toppings_total) * quantity
   ```

6. **Cart Total**:
   ```python
   # Location: cart/models.py::Cart.get_total()
   total = sum(item.get_subtotal() for item in items.all())
   ```

7. **Order Total Calculation**:
   ```python
   # Location: orders/schema.py::CreateOrder.mutate()
   subtotal = cart.get_total()
   deliveryFee = (if delivery) ? deliveryFee : 0
   discountAmount = (if promotion) ? calculate_discount() : 0
   total = subtotal + deliveryFee - discountAmount
   ```

### Price Fields Location:

| Field | Location | Type | Description |
|-------|----------|------|-------------|
| `Product.basePrice` | `products/models.py` | `DecimalField` | Base price (smallest size) |
| `Size.priceModifier` | `products/models.py` | `DecimalField` | Size adjustment (can be negative) |
| `Topping.price` | `products/models.py` | `DecimalField` | Individual topping price |
| `CartItem.unitPrice` | `cart/models.py` | `DecimalField` | Snapshot of calculated price |
| `CartItem.get_subtotal()` | `cart/models.py` | Method | `(unitPrice + toppings) * quantity` |
| `Cart.get_total()` | `cart/models.py` | Method | Sum of all item subtotals |
| `Order.subtotal` | `orders/models.py` | `DecimalField` | Cart total at checkout |
| `Order.deliveryFee` | `orders/models.py` | `DecimalField` | Delivery fee (if delivery) |
| `Order.discountAmount` | `orders/models.py` | `DecimalField` | Discount from promotion |
| `Order.total` | `orders/models.py` | `DecimalField` | Final order total |

### Important Notes:

- **All prices are stored as `Decimal`** for precision (no floating point errors)
- **Prices in GraphQL mutations must be strings** (e.g., `"14.99"` not `14.99`)
- **Cart item prices are snapshotted** when added to cart (prevents price changes affecting existing cart)
- **Order prices are snapshotted** at checkout (historical record)
- **Topping prices are stored as strings in JSON** for compatibility

---

## 📝 **NOTES FOR FRONTEND**

1. **Authentication**: Use session-based authentication. After login, cookies are automatically set.

2. **Cart**: Cart is session-based, no login required. Cart persists across page refreshes.

3. **Image Upload**: Use base64 encoding for product images:
   ```
   "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
   ```

4. **Price Format**: Always send prices as strings in mutations:
   ```json
   "basePrice": "14.99"  // ✅ Correct
   "basePrice": 14.99    // ❌ Wrong
   ```

5. **Order Status Values**:
   - `pending`
   - `preparing`
   - `ready`
   - `delivered`
   - `picked_up`
   - `cancelled`

6. **Order Type Values**:
   - `delivery`
   - `pickup`

7. **User Roles**:
   - `admin`
   - `staff`

8. **Error Handling**: All mutations return `success` and `message` fields. Check `success` before using data.

9. **Permissions**:
   - **Public**: Cart queries, Product queries, Order creation
   - **Staff/Admin**: Order queries, Order status updates
   - **Admin Only**: All create/update/delete mutations for Products, Categories, Tags, Sizes, Toppings, Ingredients, Included Items, Users

---

**Last Updated**: 2024

