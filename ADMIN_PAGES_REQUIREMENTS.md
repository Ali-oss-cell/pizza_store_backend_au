# 🔐 Admin Dashboard Pages Requirements

Complete guide for building the React admin dashboard to manage the pizza store.

---

## 📋 **ADMIN PAGES LIST**

### 1. **Login Page** (`/admin/login`)
**Purpose**: Staff/Admin authentication

**Required Fields:**
- Username input (text)
- Password input (password)
- "Login" button
- Error message display area

**GraphQL Mutation:**
```graphql
mutation Login($input: LoginInput!) {
  login(input: $input) {
    user {
      id username email role
      isAdmin isStaffMember
    }
    success message
  }
}
```

---

### 2. **Dashboard Home** (`/admin/dashboard`)
**Purpose**: Overview statistics and quick actions

**Required Fields/Components:**
- **Statistics Cards:**
  - Total Orders (number)
  - Pending Orders (number, orange badge)
  - Preparing Orders (number, purple badge)
  - Ready Orders (number, green badge)
  - Completed Orders (number, dark green badge)
  - Cancelled Orders (number, red badge)
  - Total Revenue (currency)
  - Today's Orders (number)
  - Today's Revenue (currency)

- **Recent Orders Table:**
  - Order Number
  - Customer Name
  - Status (badge)
  - Type (Delivery/Pickup)
  - Total (currency)
  - Time (relative, e.g., "5 min ago")
  - View button

- **Quick Actions:**
  - View All Orders button
  - Add New Product button
  - View Settings button

**GraphQL Queries:**
```graphql
query Dashboard {
  me {
    id username email role
    isAdmin isStaffMember
  }
  
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
  
  recentOrders(limit: 10) {
    id orderNumber customerName
    status statusDisplay
    orderType orderTypeDisplay
    total createdAt
  }
}
```

---

### 3. **Orders Management** (`/admin/orders`)
**Purpose**: List and filter all orders

**Required Fields/Components:**
- **Filters Bar:**
  - Status dropdown (All, Pending, Confirmed, Preparing, Ready, Delivered, Picked Up, Cancelled)
  - Order Type dropdown (All, Delivery, Pickup)
  - Date From (date picker)
  - Date To (date picker)
  - Search input (order number, customer name)

- **Orders Table:**
  - Checkbox (for bulk actions)
  - Order Number (link to detail)
  - Customer Name
  - Phone
  - Type (Delivery/Pickup badge)
  - Status (color-coded badge)
  - Total (currency)
  - Time Since Order (relative time, color-coded)
  - Created At (date/time)
  - Actions dropdown (View, Update Status)

- **Bulk Actions:**
  - Mark as Confirmed
  - Mark as Preparing
  - Mark as Ready
  - Mark as Delivered/Picked Up
  - Cancel Orders

- **Pagination** (if many orders)

**GraphQL Queries:**
```graphql
query Orders($status: String, $orderType: String, $dateFrom: Date, $dateTo: Date, $limit: Int) {
  orders(status: $status, orderType: $orderType, dateFrom: $dateFrom, dateTo: $dateTo, limit: $limit) {
    id orderNumber customerName customerPhone
    orderType orderTypeDisplay
    status statusDisplay
    total createdAt
    items {
      productName quantity
    }
  }
}
```

**GraphQL Mutations:**
```graphql
mutation UpdateOrderStatus($input: UpdateOrderStatusInput!) {
  updateOrderStatus(input: $input) {
    order {
      id orderNumber status statusDisplay
    }
    success message
  }
}
```

---

### 4. **Order Detail Page** (`/admin/orders/:id`)
**Purpose**: View and manage single order

**Required Fields/Components:**
- **Order Header:**
  - Order Number (large, prominent)
  - Status dropdown (with update button)
  - Order Type badge
  - Created At timestamp
  - Updated At timestamp
  - Completed At timestamp (if completed)

- **Customer Information Card:**
  - Name
  - Email
  - Phone

- **Order Items Table:**
  - Product Name
  - Size (if applicable)
  - Selected Toppings (list)
  - Included Items (if combo)
  - Quantity
  - Unit Price
  - Subtotal

- **Pricing Breakdown:**
  - Subtotal
  - Delivery Fee (if delivery)
  - Discount Code (if applied)
  - Discount Amount
  - **Total** (large, bold)

- **Delivery Information** (if delivery):
  - Delivery Address (full address)
  - Delivery Instructions

- **Order Notes** (if any)

- **Actions:**
  - Update Status button
  - Print Order button (optional)
  - Back to Orders button

**GraphQL Queries:**
```graphql
query OrderDetail($id: ID!) {
  order(orderId: $id) {
    id orderNumber
    customerName customerEmail customerPhone
    orderType orderTypeDisplay
    status statusDisplay
    orderNotes
    deliveryAddress deliveryInstructions
    subtotal deliveryFee
    discountCode discountAmount
    total
    items {
      productName productId
      isCombo includedItems
      sizeName selectedToppings
      quantity unitPrice subtotal
    }
    createdAt updatedAt completedAt
  }
}
```

---

### 5. **Products Management** (`/admin/products`)
**Purpose**: List all products

**Required Fields/Components:**
- **Filters:**
  - Category dropdown
  - Tag dropdown (multi-select)
  - Availability toggle (All, Available, Unavailable)
  - Featured toggle (All, Featured, Not Featured)
  - Search input (name, description)

- **Products Table:**
  - Image thumbnail
  - Name (link to edit)
  - Category
  - Base Price
  - Rating (★ 4.8 (25))
  - Prep Time (15-20 min)
  - Status badge (Available/Unavailable)
  - Featured badge (if featured)
  - Tags (chips/badges)
  - Actions dropdown (Edit, Delete, Duplicate)

- **"Add New Product" button**

- **Bulk Actions:**
  - Mark as Available
  - Mark as Unavailable
  - Mark as Featured
  - Delete Products

**GraphQL Queries:**
```graphql
query Products {
  allProducts {
    id name basePrice
    averageRating ratingCount
    prepTimeDisplay
    isAvailable isFeatured
    imageUrl
    category {
      id name
    }
    tags {
      id name color
    }
  }
  
  allCategories {
    id name
  }
  
  allTags {
    id name
  }
}
```

---

### 6. **Product Editor** (`/admin/products/new` or `/admin/products/:id/edit`)
**Purpose**: Create or edit a product

**Required Fields/Components:**

**Section 1: Basic Information**
- Name (text input, required)
- Short Description (text input, max 255 chars)
- Full Description (textarea, rich text editor optional)
- Category (dropdown/select, required)
- Base Price (number input, decimal, required)
- Image Upload (file input with preview)

**Section 2: Classification**
- Tags (multi-select checkboxes with color preview)
- Is Featured (toggle switch)
- Is Available (toggle switch)
- Is Combo (toggle switch)

**Section 3: Ingredients**
- Ingredients (multi-select checkboxes)
- Show ingredient icons if available

**Section 4: Sizes & Pricing**
- Available Sizes (multi-select checkboxes)
  - Show: Size name, category, price modifier
  - Display calculated price for each size

**Section 5: Customization Options**
- Available Toppings (multi-select checkboxes)
  - Show: Topping name, price

**Section 6: Combo Items** (if Is Combo is checked)
- Included Items (multi-select checkboxes)

**Section 7: Additional Details**
- Prep Time Min (number input, minutes)
- Prep Time Max (number input, minutes)
- Calories (number input, optional)

**Section 8: Reviews** (if editing existing product)
- Average Rating display
- Rating Count
- Link to reviews management

**Actions:**
- Save button
- Save & Add Another button
- Cancel button
- Delete button (if editing)

**GraphQL Queries:**
```graphql
query ProductEditor($id: ID) {
  product(id: $id) {
    id name shortDescription description
    basePrice category { id name }
    tags { id name }
    ingredients { id name icon }
    availableSizes { id name category priceModifier }
    availableToppings { id name price }
    includedItems { id name }
    isAvailable isFeatured isCombo
    prepTimeMin prepTimeMax calories
    imageUrl
    averageRating ratingCount
  }
  
  allCategories {
    id name
  }
  
  allTags {
    id name slug color
  }
  
  allIngredients {
    id name icon
  }
  
  allSizes {
    id name category priceModifier displayOrder
  }
  
  allToppings {
    id name price
  }
  
  allIncludedItems {
    id name
  }
}
```

**GraphQL Mutations:**
```graphql
mutation CreateProduct($input: ProductInput!) {
  createProduct(input: $input) {
    product {
      id name
    }
    success message
  }
}

mutation UpdateProduct($id: ID!, $input: ProductInput!) {
  updateProduct(id: $id, input: $input) {
    product {
      id name
    }
    success message
  }
}

mutation DeleteProduct($id: ID!) {
  deleteProduct(id: $id) {
    success message
  }
}
```

---

### 7. **Categories Management** (`/admin/categories`)
**Purpose**: Manage product categories

**Required Fields/Components:**
- **Categories List/Table:**
  - Name
  - Slug (auto-generated, editable)
  - Description
  - Product Count (number of products in category)
  - Created At
  - Actions (Edit, Delete)

- **Category Form** (modal or separate page):
  - Name (text input, required)
  - Slug (text input, auto-filled from name)
  - Description (textarea)

- **"Add Category" button**

**GraphQL Operations:**
```graphql
query {
  allCategories {
    id name slug description
    createdAt
  }
}

mutation CreateCategory($input: CategoryInput!) {
  createCategory(input: $input) {
    category {
      id name slug
    }
    success message
  }
}

mutation UpdateCategory($id: ID!, $input: CategoryInput!) {
  updateCategory(id: $id, input: $input) {
    category {
      id name
    }
    success message
  }
}

mutation DeleteCategory($id: ID!) {
  deleteCategory(id: $id) {
    success message
  }
}
```

---

### 8. **Tags Management** (`/admin/tags`)
**Purpose**: Manage pizza tags (Meat, Vegetarian, Chicken, etc.)

**Required Fields/Components:**
- **Tags List:**
  - Color preview (colored square/circle)
  - Name
  - Slug
  - Color code (#hex)
  - Product Count
  - Actions (Edit, Delete)

- **Tag Form:**
  - Name (text input, required)
  - Slug (text input, auto-filled)
  - Color (color picker, required)

- **"Add Tag" button**

**GraphQL Operations:**
```graphql
query {
  allTags {
    id name slug color
  }
}

mutation CreateTag($input: TagInput!) {
  createTag(input: $input) {
    tag {
      id name color
    }
    success message
  }
}

mutation UpdateTag($id: ID!, $input: TagInput!) {
  updateTag(id: $id, input: $input) {
    tag {
      id name color
    }
    success message
  }
}

mutation DeleteTag($id: ID!) {
  deleteTag(id: $id) {
    success message
  }
}
```

---

### 9. **Ingredients Management** (`/admin/ingredients`)
**Purpose**: Manage base ingredients

**Required Fields/Components:**
- **Ingredients List:**
  - Icon (emoji/icon display)
  - Name
  - Used In (product count)
  - Actions (Edit, Delete)

- **Ingredient Form:**
  - Name (text input, required)
  - Icon (text input, emoji picker optional)

- **"Add Ingredient" button**

**GraphQL Operations:**
```graphql
query {
  allIngredients {
    id name icon
  }
}

mutation CreateIngredient($input: IngredientInput!) {
  createIngredient(input: $input) {
    ingredient {
      id name icon
    }
    success message
  }
}

mutation UpdateIngredient($id: ID!, $input: IngredientInput!) {
  updateIngredient(id: $id, input: $input) {
    ingredient {
      id name icon
    }
    success message
  }
}

mutation DeleteIngredient($id: ID!) {
  deleteIngredient(id: $id) {
    success message
  }
}
```

---

### 10. **Sizes Management** (`/admin/sizes`)
**Purpose**: Manage product sizes

**Required Fields/Components:**
- **Sizes Table** (grouped by category):
  - Category badge
  - Name
  - Price Modifier (+$3.00 or -$1.00)
  - Display Order
  - Actions (Edit, Delete)

- **Size Form:**
  - Name (text input, required)
  - Category (dropdown: Pizza, Drink, Pasta, Other)
  - Price Modifier (number input, decimal, can be negative)
  - Display Order (number input)

- **"Add Size" button**

**GraphQL Operations:**
```graphql
query {
  allSizes {
    id name category priceModifier displayOrder
  }
}

mutation CreateSize($input: SizeInput!) {
  createSize(input: $input) {
    size {
      id name category
    }
    success message
  }
}

mutation UpdateSize($id: ID!, $input: SizeInput!) {
  updateSize(id: $id, input: $input) {
    size {
      id name
    }
    success message
  }
}

mutation DeleteSize($id: ID!) {
  deleteSize(id: $id) {
    success message
  }
}
```

---

### 11. **Toppings Management** (`/admin/toppings`)
**Purpose**: Manage extra toppings

**Required Fields/Components:**
- **Toppings Table:**
  - Name
  - Price (+$2.00)
  - Created At
  - Actions (Edit, Delete)

- **Topping Form:**
  - Name (text input, required)
  - Price (number input, decimal, required)

- **"Add Topping" button**

**GraphQL Operations:**
```graphql
query {
  allToppings {
    id name price
    createdAt
  }
}

mutation CreateTopping($input: ToppingInput!) {
  createTopping(input: $input) {
    topping {
      id name price
    }
    success message
  }
}

mutation UpdateTopping($id: ID!, $input: ToppingInput!) {
  updateTopping(id: $id, input: $input) {
    topping {
      id name price
    }
    success message
  }
}

mutation DeleteTopping($id: ID!) {
  deleteTopping(id: $id) {
    success message
  }
}
```

---

### 12. **Included Items Management** (`/admin/included-items`)
**Purpose**: Manage combo included items (chips, salad, etc.)

**Required Fields/Components:**
- **Included Items List:**
  - Name
  - Actions (Edit, Delete)

- **Included Item Form:**
  - Name (text input, required)

- **"Add Included Item" button**

**GraphQL Operations:**
```graphql
query {
  allIncludedItems {
    id name
  }
}

mutation CreateIncludedItem($input: IncludedItemInput!) {
  createIncludedItem(input: $input) {
    includedItem {
      id name
    }
    success message
  }
}

mutation UpdateIncludedItem($id: ID!, $input: IncludedItemInput!) {
  updateIncludedItem(id: $id, input: $input) {
    includedItem {
      id name
    }
    success message
  }
}

mutation DeleteIncludedItem($id: ID!) {
  deleteIncludedItem(id: $id) {
    success message
  }
}
```

---

### 13. **Promotions Management** (`/admin/promotions`)
**Purpose**: Manage discount codes

**Required Fields/Components:**
- **Filters:**
  - Status (All, Active, Inactive, Expired, Upcoming)
  - Discount Type (All, Percentage, Fixed, Free Delivery)

- **Promotions Table:**
  - Code (prominent)
  - Name
  - Discount Display (10% off, $5 off, Free Delivery)
  - Status Badge (Active/Expired/Upcoming/Limit Reached)
  - Usage (X / Y or X / ∞)
  - Valid From (date)
  - Valid Until (date)
  - Actions (Edit, Delete)

- **Promotion Form:**
  - Code (text input, uppercase, required)
  - Name (text input, required)
  - Description (textarea)
  - Discount Type (radio/select: Percentage, Fixed Amount, Free Delivery)
  - Discount Value (number input, required)
  - Maximum Discount (number input, for percentage only)
  - Minimum Order Amount (number input, optional)
  - Usage Limit (number input, optional, null = unlimited)
  - Is Active (toggle switch)
  - Valid From (date/time picker, required)
  - Valid Until (date/time picker, required)

- **"Add Promotion" button**

**GraphQL Operations:**
```graphql
query {
  allPromotions {
    id code name discountDisplay
    discountType discountValue
    minimumOrderAmount maximumDiscount
    usageLimit timesUsed
    isActive validFrom validUntil
  }
}

mutation CreatePromotion($input: PromotionInput!) {
  createPromotion(input: $input) {
    promotion {
      id code name
    }
    success message
  }
}

mutation UpdatePromotion($id: ID!, $input: PromotionInput!) {
  updatePromotion(id: $id, input: $input) {
    promotion {
      id code
    }
    success message
  }
}

mutation DeletePromotion($id: ID!) {
  deletePromotion(id: $id) {
    success message
  }
}
```

---

### 14. **Store Settings** (`/admin/settings`)
**Purpose**: Configure store-wide settings

**Required Fields/Components:**

**Section 1: Store Information**
- Store Name (text input)
- Store Phone (text input)
- Store Email (email input)
- Store Address (textarea)

**Section 2: Business Hours**
- JSON Editor or Day-by-Day Form:
  - Monday: Open Time, Close Time
  - Tuesday: Open Time, Close Time
  - ... (all 7 days)
  - Closed checkbox per day

**Section 3: Order Settings**
- Accept Orders (toggle switch)
- Delivery Enabled (toggle switch)
- Pickup Enabled (toggle switch)
- Order Notes Enabled (toggle switch)

**Section 4: Delivery Settings**
- Delivery Fee (number input, decimal)
- Free Delivery Threshold (number input, decimal)
- Minimum Order Amount (number input, decimal)
- Delivery Radius (km) (number input, decimal)
- Estimated Delivery Time (minutes) (number input)
- Estimated Pickup Time (minutes) (number input)

**Section 5: Tax Settings**
- Tax Rate (%) (number input, decimal)
- Tax Included in Prices (toggle switch)

**Actions:**
- Save Settings button

**GraphQL Operations:**
```graphql
query {
  storeSettings {
    storeName storePhone storeEmail storeAddress
    businessHours
    acceptOrders deliveryEnabled pickupEnabled orderNotesEnabled
    deliveryFee freeDeliveryThreshold minimumOrderAmount
    deliveryRadiusKm estimatedDeliveryTime estimatedPickupTime
    taxRate taxIncludedInPrices
  }
}

mutation UpdateStoreSettings($input: StoreSettingsInput!) {
  updateStoreSettings(input: $input) {
    settings {
      storeName
    }
    success message
  }
}
```

---

### 15. **Team Management** (`/admin/team`) - Admin Only
**Purpose**: Manage staff members

**Required Fields/Components:**
- **Team Stats Cards:**
  - Total Users
  - Admins Count
  - Staff Count
  - Active Users
  - Inactive Users

- **Team Members Table:**
  - Username
  - Email
  - Role Badge (Admin/Staff)
  - Status Badge (Active/Inactive)
  - Created At
  - Actions (Edit, Deactivate/Activate, Delete)

- **User Form** (modal or separate page):
  - Username (text input, required)
  - Email (email input, required)
  - Password (password input, required for new)
  - Confirm Password (password input, required for new)
  - Role (radio/select: Admin, Staff)
  - Is Active (toggle switch)

- **"Add Staff Member" button**

**GraphQL Operations:**
```graphql
query {
  allUsers {
    id username email role
    isActive dateJoined createdAt
  }
  
  teamStats
}

mutation Register($input: RegisterInput!) {
  register(input: $input) {
    user {
      id username email role
    }
    success message
  }
}

mutation UpdateUser($userId: ID, $email: String, $role: String, $isActive: Boolean) {
  updateUser(userId: $userId, email: $email, role: $role, isActive: $isActive) {
    user {
      id username email role isActive
    }
    success message
  }
}
```

---

### 16. **Reviews Management** (`/admin/reviews`)
**Purpose**: Approve/reject product reviews

**Required Fields/Components:**
- **Filters:**
  - Status (All, Pending, Approved, Rejected)
  - Rating (All, 5★, 4★, 3★, 2★, 1★)
  - Product (dropdown)

- **Reviews Table:**
  - Product Name (link)
  - Customer Name
  - Rating (stars display: ★★★★☆)
  - Comment (truncated, expandable)
  - Status Badge (Pending/Approved)
  - Created At
  - Actions (Approve, Reject, Delete)

- **Review Detail Modal** (on click):
  - Full comment
  - Product link
  - Customer email
  - Approve/Reject buttons

**GraphQL Operations:**
```graphql
query Reviews($productId: ID) {
  # Get reviews for specific product or all
  productReviews(productId: $productId) {
    id customerName customerEmail
    rating comment
    isApproved createdAt
    product {
      id name
    }
  }
}

mutation ApproveReview($id: ID!, $approve: Boolean!) {
  approveReview(id: $id, approve: $approve) {
    review {
      id isApproved
    }
    success message
  }
}

mutation DeleteReview($id: ID!) {
  deleteReview(id: $id) {
    success message
  }
}
```

---

## 🎨 **SHARED ADMIN COMPONENTS**

### Reusable Components Needed:
1. **StatusBadge** - Color-coded status indicators
2. **DataTable** - Reusable table with sorting, filtering, pagination
3. **FormModal** - Modal for create/edit forms
4. **ImageUpload** - File upload with preview
5. **MultiSelect** - For tags, ingredients, sizes, etc.
6. **ColorPicker** - For tag colors
7. **DateRangePicker** - For promotions validity
8. **ToggleSwitch** - For boolean fields
9. **LoadingSpinner** - For async operations
10. **ErrorAlert** - Display GraphQL errors
11. **SuccessToast** - Show success messages
12. **ConfirmDialog** - For delete confirmations
13. **Breadcrumbs** - Navigation breadcrumbs
14. **Sidebar** - Navigation menu
15. **Header** - Top bar with user info, logout

---

## 🔑 **AUTHENTICATION & AUTHORIZATION**

### Flow:
1. **Login** → Store session token
2. **Check `me` query** on app load
3. **Protect routes:**
   - All `/admin/*` routes require authentication
   - Some routes require `isAdmin` (Team, Settings)

### GraphQL Query:
```graphql
query {
  me {
    id username email role
    isAdmin isStaffMember
  }
}
```

---

## 📦 **STATE MANAGEMENT**

### Required State:
- **Current User** (from `me` query)
- **Store Settings** (cached, refresh on settings page)
- **Orders** (for dashboard and orders list)
- **Products** (for products list)
- **Form Data** (for create/edit forms)

### Recommended:
- React Context or Redux/Zustand
- Apollo Client for GraphQL
- Form state: React Hook Form or Formik

---

## 🚀 **DEVELOPMENT PRIORITY**

### Phase 1 (Essential):
1. Login
2. Dashboard
3. Orders Management
4. Order Detail
5. Products Management
6. Product Editor

### Phase 2 (Important):
7. Categories Management
8. Tags Management
9. Sizes Management
10. Toppings Management
11. Promotions Management

### Phase 3 (Complete):
12. Ingredients Management
13. Included Items Management
14. Store Settings
15. Team Management
16. Reviews Management

---

This covers all admin pages with exact fields and GraphQL operations needed! 🎯

