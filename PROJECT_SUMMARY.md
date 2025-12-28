# 🍕 Pizza Store Backend - Project Summary

## 📋 **Overview**

A complete Django + GraphQL backend for an e-commerce pizza and pasta store with:
- **Session-based guest cart** (no login required for customers)
- **Two-level user system** (Admin/Staff) for in-store team management
- **Full menu management** with products, categories, sizes, toppings, tags, ingredients
- **Order management** with status tracking
- **Promotions/Coupons system**
- **Store settings management**
- **Product reviews**

---

## 🏗️ **Project Structure**

```
pizza-store-backend/
├── pizza_store/
│   ├── accounts/          # User authentication & management
│   ├── products/          # Menu items, categories, sizes, toppings
│   ├── cart/              # Session-based shopping cart
│   ├── orders/            # Order management & tracking
│   ├── team/              # Store settings & promotions
│   ├── payments/          # (Placeholder - not implemented)
│   └── pizza_store/       # Main project settings
├── venv/                  # Python virtual environment
├── media/                 # Product images
├── db.sqlite3             # SQLite database
└── requirements.txt       # Python dependencies
```

---

## 📦 **Django Apps**

### 1. **Accounts App** (`accounts/`)
**Purpose:** User authentication and team management

**Models:**
- `User` - Custom user model with Admin/Staff roles

**Features:**
- ✅ Custom User model extending AbstractUser
- ✅ Role-based system (Admin/Staff)
- ✅ Session-based authentication
- ✅ Login/Logout mutations
- ✅ User registration (Admin only)
- ✅ Password change
- ✅ User management (Admin only)
- ✅ Team statistics query

**GraphQL Operations:**
- `me` - Get current user
- `allUsers` - Get all users (Admin only)
- `user` - Get user by ID (Admin only)
- `teamStats` - Get team statistics (Admin only)
- `login` - Authenticate user
- `logout` - Logout user
- `register` - Create new user (Admin only)
- `changePassword` - Change password
- `updateUser` - Update user info

**Admin:**
- ✅ User management with role filtering

---

### 2. **Products App** (`products/`)
**Purpose:** Menu management - products, categories, sizes, toppings, tags, ingredients

**Models:**
- `Category` - Product categories (Pizza, Pasta, Drinks, etc.)
- `Tag` - Product tags (Meat, Vegetarian, Chicken, etc.)
- `Size` - Product sizes with price modifiers
- `Topping` - Extra toppings/add-ons
- `Ingredient` - Base ingredients
- `IncludedItem` - Items included in combos
- `Product` - Main product model
- `ProductReview` - Customer reviews

**Product Features:**
- ✅ Base price system
- ✅ Size-based pricing (price modifiers)
- ✅ Topping system
- ✅ Tag system for flexible categorization
- ✅ Ingredient tracking
- ✅ Combo items with included items
- ✅ Featured products
- ✅ Product ratings & reviews
- ✅ Image upload (base64)
- ✅ Prep time tracking
- ✅ Calories tracking
- ✅ Availability toggle

**GraphQL Operations:**
- **Queries:**
  - `allProducts` - Get all products
  - `product` - Get single product
  - `productsByCategory` - Filter by category
  - `productsByTag` - Filter by tag
  - `searchProducts` - Search products
  - `availableProducts` - Get available only
  - `featuredProducts` - Get featured products
  - `topRatedProducts` - Get top rated
  - `allCategories` - Get all categories
  - `category` - Get single category
  - `allTags` - Get all tags
  - `allSizes` - Get all sizes
  - `size` - Get single size
  - `allToppings` - Get all toppings
  - `topping` - Get single topping
  - `allIngredients` - Get all ingredients
  - `ingredient` - Get single ingredient
  - `allIncludedItems` - Get all included items
  - `includedItem` - Get single included item
  - `productReviews` - Get product reviews

- **Mutations (Admin Only):**
  - `createProduct` - Create product
  - `updateProduct` - Update product
  - `deleteProduct` - Delete product
  - `createCategory` - Create category
  - `updateCategory` - Update category
  - `deleteCategory` - Delete category
  - `createTag` - Create tag
  - `updateTag` - Update tag
  - `deleteTag` - Delete tag
  - `createSize` - Create size
  - `updateSize` - Update size
  - `deleteSize` - Delete size
  - `createTopping` - Create topping
  - `updateTopping` - Update topping
  - `deleteTopping` - Delete topping
  - `createIngredient` - Create ingredient
  - `updateIngredient` - Update ingredient
  - `deleteIngredient` - Delete ingredient
  - `createIncludedItem` - Create included item
  - `updateIncludedItem` - Update included item
  - `deleteIncludedItem` - Delete included item
  - `submitReview` - Submit review (public)
  - `approveReview` - Approve review (Admin)
  - `deleteReview` - Delete review (Admin)

**Admin:**
- ✅ All models registered with proper list_display, filters, search
- ✅ Product admin with inline editing
- ✅ Category admin with slug auto-generation

---

### 3. **Cart App** (`cart/`)
**Purpose:** Session-based shopping cart for guest users

**Models:**
- `Cart` - Session-based cart
- `CartItem` - Individual cart items with product, size, toppings

**Features:**
- ✅ Session-based (no login required)
- ✅ Price calculation (base + size + toppings)
- ✅ Quantity management
- ✅ Topping selection
- ✅ Size selection
- ✅ Cart total calculation
- ✅ Item subtotal calculation

**GraphQL Operations:**
- **Queries:**
  - `cart` - Get current cart

- **Mutations:**
  - `addToCart` - Add item to cart
  - `updateCartItem` - Update cart item (quantity, size, toppings)
  - `removeFromCart` - Remove item from cart
  - `clearCart` - Clear entire cart

**Price Calculation:**
- `calculate_item_price()` - Calculates: basePrice + sizeModifier + sum(toppingPrices)
- `CartItem.get_subtotal()` - Calculates: (unitPrice + toppings) * quantity
- `Cart.get_total()` - Sum of all item subtotals

**Admin:**
- ✅ Cart and CartItem models registered

---

### 4. **Orders App** (`orders/`)
**Purpose:** Order management and tracking

**Models:**
- `Order` - Customer orders
- `OrderItem` - Order line items (snapshot of cart items)

**Order Features:**
- ✅ Guest checkout (no login required)
- ✅ Order status tracking (Pending, Preparing, Ready, Delivered, Picked Up, Cancelled)
- ✅ Delivery and Pickup support
- ✅ Customer information capture
- ✅ Delivery address and instructions
- ✅ Order notes
- ✅ Promotion code support
- ✅ Price snapshots (historical record)
- ✅ Order number generation
- ✅ Order statistics

**GraphQL Operations:**
- **Queries:**
  - `order` - Get order by number or ID
  - `orders` - Get all orders (Staff/Admin, filterable)
  - `recentOrders` - Get recent orders (Staff/Admin)
  - `orderStats` - Get order statistics (Staff/Admin)

- **Mutations:**
  - `createOrder` - Create order from cart (checkout)
  - `updateOrderStatus` - Update order status (Staff/Admin)

**Order Total Calculation:**
```
subtotal = cart.get_total()
deliveryFee = (if delivery) ? deliveryFee : 0
discountAmount = (if promotion) ? calculate_discount() : 0
total = subtotal + deliveryFee - discountAmount
```

**Admin:**
- ✅ Advanced Order admin with:
  - Color-coded status badges
  - Quick status update actions
  - Order item inline editing
  - Date hierarchy
  - Custom permissions
  - Read-only fields protection

---

### 5. **Team App** (`team/`)
**Purpose:** Store settings and promotions management

**Models:**
- `StoreSettings` - Store configuration (singleton)
- `Promotion` - Discount codes and promotions

**Store Settings Features:**
- ✅ Store information (name, phone, email, address)
- ✅ Business hours (JSON field)
- ✅ Delivery settings (fee, threshold, radius)
- ✅ Pickup settings
- ✅ Tax configuration
- ✅ Order acceptance toggle

**Promotion Features:**
- ✅ Discount types: Percentage, Fixed Amount, Free Delivery
- ✅ Usage limits
- ✅ Validity dates
- ✅ Minimum order amount
- ✅ Maximum discount cap
- ✅ Usage tracking
- ✅ Automatic discount calculation

**GraphQL Operations:**
- **Queries:**
  - `storeSettings` - Get store settings (public)
  - `validatePromotion` - Validate promotion code
  - `allPromotions` - Get all promotions (Staff/Admin)
  - `promotion` - Get promotion by ID or code (Staff/Admin)

- **Mutations (Admin Only):**
  - `updateStoreSettings` - Update store settings
  - `createPromotion` - Create promotion
  - `updatePromotion` - Update promotion
  - `deletePromotion` - Delete promotion

**Admin:**
- ✅ StoreSettings admin (singleton)
- ✅ Promotion admin with filters

---

### 6. **Payments App** (`payments/`)
**Status:** ⚠️ Placeholder - Not implemented yet

---

## 🔧 **Configuration**

### Settings (`pizza_store/settings.py`)
- ✅ Django 6.0
- ✅ Custom User model (`accounts.User`)
- ✅ GraphQL configured (Graphene-Django)
- ✅ CORS enabled for React frontend
- ✅ Session configuration for guest cart
- ✅ Media files configuration
- ✅ CSRF settings for cross-origin requests
- ✅ Database: SQLite (development)

### URLs (`pizza_store/urls.py`)
- ✅ Admin interface: `/admin/`
- ✅ GraphQL endpoint: `/graphql/` (with GraphiQL)
- ✅ Media files serving (development)

### Root Schema (`pizza_store/schema.py`)
- ✅ Combines all app schemas
- ✅ Query: AccountsQuery, ProductsQuery, CartQuery, OrdersQuery, TeamQuery
- ✅ Mutation: AccountsMutation, ProductsMutation, CartMutation, OrdersMutation, TeamMutation

---

## 📊 **Database Models Summary**

### Accounts
- `User` (1 model)

### Products
- `Category` (1)
- `Tag` (1)
- `Size` (1)
- `Topping` (1)
- `Ingredient` (1)
- `IncludedItem` (1)
- `Product` (1)
- `ProductReview` (1)
**Total: 8 models**

### Cart
- `Cart` (1)
- `CartItem` (1)
**Total: 2 models**

### Orders
- `Order` (1)
- `OrderItem` (1)
**Total: 2 models**

### Team
- `StoreSettings` (1)
- `Promotion` (1)
**Total: 2 models**

**Grand Total: 14 models**

---

## 🔐 **Authentication & Permissions**

### Public Access (No Login Required)
- ✅ Product queries (browse menu)
- ✅ Cart operations
- ✅ Order creation (checkout)
- ✅ Store settings query
- ✅ Promotion validation
- ✅ Product review submission

### Staff/Admin Access
- ✅ Order queries and status updates
- ✅ Order statistics
- ✅ Promotion management (view)

### Admin Only
- ✅ All create/update/delete mutations for:
  - Products
  - Categories
  - Tags
  - Sizes
  - Toppings
  - Ingredients
  - Included Items
  - Users
  - Store Settings
  - Promotions
- ✅ Review approval/deletion

---

## 💰 **Price System**

### Price Calculation Flow
1. **Base Price** - Set on Product model
2. **Size Modifier** - Added from Size model (can be negative)
3. **Toppings** - Each topping has a price, added to base
4. **Cart Item Price** - Snapshot when added to cart
5. **Cart Total** - Sum of all item subtotals
6. **Order Total** - Cart total + delivery fee - discount

### Price Storage
- All prices use `Decimal` for precision
- Prices stored as strings in JSON fields
- Historical snapshots in Order and OrderItem models

**See `PRICE_HANDLING.md` for detailed documentation.**

---

## 📝 **GraphQL Schema Coverage**

### ✅ Fully Implemented
- **Accounts:** Login, Logout, User Management
- **Products:** Full CRUD for all entities
- **Cart:** Add, Update, Remove, Clear
- **Orders:** Create, Query, Status Updates
- **Team:** Store Settings, Promotions

### ⚠️ Not Implemented
- **Payments:** Payment processing
- **Notifications:** Order notifications
- **Analytics:** Advanced analytics queries

---

## 🎨 **Admin Interface**

### Registered Models
- ✅ User (with role filtering)
- ✅ Category (with slug auto-generation)
- ✅ Tag
- ✅ Size
- ✅ Topping
- ✅ Ingredient
- ✅ IncludedItem
- ✅ Product (with inline editing)
- ✅ ProductReview
- ✅ Cart
- ✅ CartItem
- ✅ Order (advanced with status actions)
- ✅ OrderItem
- ✅ StoreSettings (singleton)
- ✅ Promotion

### Admin Features
- ✅ List display customization
- ✅ Search fields
- ✅ Filters
- ✅ Inline editing
- ✅ Custom actions
- ✅ Read-only fields
- ✅ Permission checks

---

## 🚀 **Dependencies**

```
Django==6.0
graphene==3.4.3
graphene-django==3.2.3
django-cors-headers==4.3.1
Pillow==10.2.0
```

---

## 📚 **Documentation Files**

1. **GRAPHQL_OPERATIONS.md** - Complete GraphQL queries and mutations
2. **PRICE_HANDLING.md** - Price calculation documentation
3. **IMAGE_UPLOAD_GUIDE.md** - Image upload instructions
4. **ADMIN_PAGES_REQUIREMENTS.md** - Admin dashboard requirements
5. **FIRST_TEST.md** - Initial testing guide
6. **ADMIN_LOGIN_TEST.md** - Admin login testing

---

## ✅ **Completed Features**

### Core Functionality
- ✅ User authentication (session-based)
- ✅ Role-based access control (Admin/Staff)
- ✅ Product management (full CRUD)
- ✅ Category management
- ✅ Size management
- ✅ Topping management
- ✅ Tag management
- ✅ Ingredient management
- ✅ Included Item management
- ✅ Session-based cart
- ✅ Guest checkout
- ✅ Order management
- ✅ Order status tracking
- ✅ Store settings
- ✅ Promotions/Coupons
- ✅ Product reviews
- ✅ Image uploads
- ✅ Price calculations

### Technical Features
- ✅ GraphQL API
- ✅ CORS configuration
- ✅ Media file serving
- ✅ Session management
- ✅ CSRF protection
- ✅ Admin interface
- ✅ Database migrations
- ✅ Decimal precision for prices

---

## ⚠️ **Missing/Incomplete Features**

### Not Implemented
- ❌ Payment processing (Payments app is placeholder)
- ❌ Email notifications
- ❌ SMS notifications
- ❌ Order analytics dashboard
- ❌ Inventory management
- ❌ Multi-store support
- ❌ Customer accounts (optional login)
- ❌ Order history for customers
- ❌ Wishlist/Favorites
- ❌ Product variants
- ❌ Bulk operations
- ❌ Export functionality

### Could Be Enhanced
- ⚠️ Advanced search/filtering
- ⚠️ Product recommendations
- ⚠️ Order scheduling
- ⚠️ Delivery tracking
- ⚠️ Customer loyalty program
- ⚠️ Product bundles/packages

---

## 🧪 **Testing Status**

- ✅ Database migrations created and applied
- ✅ Admin user creation script (`create_admin.py`)
- ✅ GraphQL endpoint accessible
- ✅ GraphiQL interface working
- ⚠️ Unit tests not written yet
- ⚠️ Integration tests not written yet

---

## 📈 **Next Steps (Optional Enhancements)**

1. **Payment Integration**
   - Implement payment processing
   - Payment gateway integration
   - Payment status tracking

2. **Notifications**
   - Email notifications for orders
   - SMS notifications
   - Push notifications

3. **Analytics**
   - Sales reports
   - Product performance
   - Customer analytics
   - Revenue tracking

4. **Customer Features**
   - Optional customer accounts
   - Order history
   - Saved addresses
   - Favorite products

5. **Advanced Features**
   - Inventory management
   - Order scheduling
   - Delivery tracking
   - Multi-language support

---

## 🎯 **Current Status: PRODUCTION READY (Core Features)**

The backend is **fully functional** for:
- ✅ Menu management
- ✅ Shopping cart
- ✅ Order processing
- ✅ Order management
- ✅ Team management
- ✅ Store configuration
- ✅ Promotions

**Ready for frontend integration!**

---

**Last Updated:** 2024
**Django Version:** 6.0
**GraphQL:** Graphene-Django 3.2.3

