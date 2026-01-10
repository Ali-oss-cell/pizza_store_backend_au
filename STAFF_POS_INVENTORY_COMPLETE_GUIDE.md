# Staff, POS & Inventory - Complete System Guide

Complete documentation for the staff management, POS (Point of Sale), and inventory systems.

---

## 📋 Table of Contents

1. [Staff User System](#staff-user-system)
2. [Creating Staff from Dashboard](#creating-staff-from-dashboard)
3. [POS System](#pos-system)
4. [Inventory System](#inventory-system)
5. [Complete Workflow Examples](#complete-workflow-examples)

---

# 👥 Staff User System

## User Roles

The system has two user roles:

### 1. Admin Users
- **Role:** `admin`
- **Access:** Full access to everything
- **Can do:** Create users, manage products, inventory, orders, settings
- **Use:** Dashboard + POS

### 2. Staff Users
- **Role:** `staff`
- **Access:** Limited based on permissions
- **Can do:** Based on assigned permissions
- **Use:** POS + Limited dashboard

---

## Staff Permissions

Staff users have granular permissions:

| Permission | Description | Default |
|------------|-------------|---------|
| `canManageOrders` | View and update order status | ✅ True |
| `canManageProducts` | Create, update, delete products | ❌ False |
| `canManageCategories` | Create, update, delete categories | ❌ False |
| `canManagePromotions` | Create, update, delete promotions | ❌ False |
| `canViewReports` | View sales reports and analytics | ❌ False |
| `canManageReviews` | Approve or reject product reviews | ❌ False |

---

## Staff User Types

### Cashier (POS Only)
- Can: Create orders, scan barcodes, print receipts
- Cannot: Modify products, inventory, settings
- Permissions:
  ```
  canManageOrders: true
  canManageProducts: false
  canManageCategories: false
  canManagePromotions: false
  canViewReports: false
  canManageReviews: false
  ```

### Shift Manager
- Can: Orders + View reports
- Permissions:
  ```
  canManageOrders: true
  canViewReports: true
  canManageReviews: true
  ```

### Store Manager
- Can: Everything except user management
- Permissions:
  ```
  canManageOrders: true
  canManageProducts: true
  canManageCategories: true
  canManagePromotions: true
  canViewReports: true
  canManageReviews: true
  ```

---

# 🖥️ Creating Staff from Dashboard

## GraphQL Mutation

### Create Cashier (POS User)

```graphql
mutation CreateCashier {
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

### Create Shift Manager

```graphql
mutation CreateShiftManager {
  register(input: {
    username: "shift_manager1"
    email: "manager1@marinapizzas.com.au"
    password: "secure_password_123"
    passwordConfirm: "secure_password_123"
    firstName: "Jane"
    lastName: "Smith"
    phone: "0412345679"
    role: "staff"
    canManageOrders: true
    canManageProducts: false
    canManageCategories: false
    canManagePromotions: false
    canViewReports: true
    canManageReviews: true
  }) {
    success
    message
    user {
      id
      username
      role
      permissions
    }
  }
}
```

### Create Store Manager

```graphql
mutation CreateStoreManager {
  register(input: {
    username: "store_manager"
    email: "store_manager@marinapizzas.com.au"
    password: "secure_password_123"
    passwordConfirm: "secure_password_123"
    firstName: "Mike"
    lastName: "Johnson"
    phone: "0412345670"
    role: "staff"
    canManageOrders: true
    canManageProducts: true
    canManageCategories: true
    canManagePromotions: true
    canViewReports: true
    canManageReviews: true
  }) {
    success
    user {
      id
      username
      permissions
    }
  }
}
```

### Create Admin User

```graphql
mutation CreateAdmin {
  register(input: {
    username: "admin1"
    email: "admin1@marinapizzas.com.au"
    password: "secure_password_123"
    passwordConfirm: "secure_password_123"
    firstName: "Admin"
    lastName: "User"
    role: "admin"
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

---

## Dashboard UI for Creating Staff

### React Component Example

```javascript
// CreateStaffForm.js
import React, { useState } from 'react';
import { useMutation, gql } from '@apollo/client';

const CREATE_STAFF = gql`
  mutation CreateStaff($input: RegisterInput!) {
    register(input: $input) {
      success
      message
      user {
        id
        username
        email
        role
        permissions
      }
    }
  }
`;

const CreateStaffForm = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    passwordConfirm: '',
    firstName: '',
    lastName: '',
    phone: '',
    role: 'staff',
    canManageOrders: true,
    canManageProducts: false,
    canManageCategories: false,
    canManagePromotions: false,
    canViewReports: false,
    canManageReviews: false,
  });

  const [createStaff, { loading }] = useMutation(CREATE_STAFF);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const result = await createStaff({
        variables: { input: formData }
      });
      if (result.data.register.success) {
        alert('Staff user created successfully!');
      }
    } catch (error) {
      alert('Error: ' + error.message);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Create Staff User</h2>
      
      {/* Basic Info */}
      <input
        type="text"
        placeholder="Username"
        value={formData.username}
        onChange={(e) => setFormData({...formData, username: e.target.value})}
        required
      />
      <input
        type="email"
        placeholder="Email"
        value={formData.email}
        onChange={(e) => setFormData({...formData, email: e.target.value})}
        required
      />
      <input
        type="password"
        placeholder="Password"
        value={formData.password}
        onChange={(e) => setFormData({...formData, password: e.target.value})}
        required
      />
      <input
        type="password"
        placeholder="Confirm Password"
        value={formData.passwordConfirm}
        onChange={(e) => setFormData({...formData, passwordConfirm: e.target.value})}
        required
      />
      <input
        type="text"
        placeholder="First Name"
        value={formData.firstName}
        onChange={(e) => setFormData({...formData, firstName: e.target.value})}
      />
      <input
        type="text"
        placeholder="Last Name"
        value={formData.lastName}
        onChange={(e) => setFormData({...formData, lastName: e.target.value})}
      />
      <input
        type="tel"
        placeholder="Phone"
        value={formData.phone}
        onChange={(e) => setFormData({...formData, phone: e.target.value})}
      />
      
      {/* Role Selection */}
      <select
        value={formData.role}
        onChange={(e) => setFormData({...formData, role: e.target.value})}
      >
        <option value="staff">Staff</option>
        <option value="admin">Admin</option>
      </select>
      
      {/* Permissions (only for staff role) */}
      {formData.role === 'staff' && (
        <div className="permissions">
          <h3>Permissions</h3>
          <label>
            <input
              type="checkbox"
              checked={formData.canManageOrders}
              onChange={(e) => setFormData({...formData, canManageOrders: e.target.checked})}
            />
            Can Manage Orders
          </label>
          <label>
            <input
              type="checkbox"
              checked={formData.canManageProducts}
              onChange={(e) => setFormData({...formData, canManageProducts: e.target.checked})}
            />
            Can Manage Products
          </label>
          <label>
            <input
              type="checkbox"
              checked={formData.canManageCategories}
              onChange={(e) => setFormData({...formData, canManageCategories: e.target.checked})}
            />
            Can Manage Categories
          </label>
          <label>
            <input
              type="checkbox"
              checked={formData.canManagePromotions}
              onChange={(e) => setFormData({...formData, canManagePromotions: e.target.checked})}
            />
            Can Manage Promotions
          </label>
          <label>
            <input
              type="checkbox"
              checked={formData.canViewReports}
              onChange={(e) => setFormData({...formData, canViewReports: e.target.checked})}
            />
            Can View Reports
          </label>
          <label>
            <input
              type="checkbox"
              checked={formData.canManageReviews}
              onChange={(e) => setFormData({...formData, canManageReviews: e.target.checked})}
            />
            Can Manage Reviews
          </label>
        </div>
      )}
      
      <button type="submit" disabled={loading}>
        {loading ? 'Creating...' : 'Create Staff User'}
      </button>
    </form>
  );
};

export default CreateStaffForm;
```

---

## View All Staff Users

### GraphQL Query

```graphql
query AllStaff {
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
    canManageProducts
    canManageCategories
    canManagePromotions
    canViewReports
    canManageReviews
    createdAt
  }
}
```

---

## Update Staff Permissions

### GraphQL Mutation

```graphql
mutation UpdateStaffPermissions($id: ID!, $input: TeamMemberInput!) {
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
    "canManageOrders": true,
    "canManageProducts": true,
    "canViewReports": true
  }
}
```

---

# 📱 POS System

## Overview

The POS (Point of Sale) system allows staff to:
- Scan barcodes to find products
- Create orders directly (no cart)
- Print receipts
- View daily sales statistics

---

## Who Can Access POS

- **Admin users:** ✅ Full access
- **Staff users:** ✅ Full access
- **Customers:** ❌ No access

**Permission Check:**
```python
if not user or not (user.is_staff or user.is_superuser):
    raise GraphQLError("Permission denied. Staff access required for POS.")
```

---

## POS Login Flow

### Step 1: Login

```graphql
mutation POSLogin {
  login(input: {
    username: "cashier1"
    password: "password123"
  }) {
    success
    message
    user {
      id
      username
      role
      isStaffMember
      isAdmin
    }
  }
}
```

### Step 2: Verify POS Access

After login, check if user can access POS:

```javascript
// In your POS frontend
const canAccessPOS = (user) => {
  return user.isStaffMember || user.isAdmin;
};

if (!canAccessPOS(currentUser)) {
  // Redirect to error page
  alert("You don't have permission to access POS");
}
```

---

## POS Operations

### 1. Get Products for POS

```graphql
query POSProducts($categoryId: ID, $search: String, $inStockOnly: Boolean) {
  posProducts(categoryId: $categoryId, search: $search, inStockOnly: $inStockOnly) {
    id
    name
    basePrice
    currentPrice
    barcode
    sku
    stockQuantity
    isInStock
    isLowStock
    category
    imageUrl
    trackInventory
  }
}
```

### 2. Scan Barcode

```graphql
query ScanBarcode($barcode: String!) {
  scanBarcode(barcode: $barcode) {
    id
    name
    currentPrice
    barcode
    stockQuantity
    isInStock
    category
    imageUrl
  }
}
```

### 3. Create POS Order

```graphql
mutation CreatePOSOrder {
  createPosOrder(input: {
    customerName: "Walk-in Customer"
    customerPhone: "0412345678"
    orderType: "pickup"
    paymentMethod: "cash"
    items: [
      { productId: "1", quantity: 2 }
      { productId: "5", quantity: 1, sizeId: "2" }
    ]
  }) {
    success
    message
    order {
      id
      orderNumber
      total
      status
      createdAt
    }
  }
}
```

### 4. Get Receipt

```graphql
query Receipt($orderId: ID!) {
  receipt(orderId: $orderId) {
    orderNumber
    date
    time
    customerName
    customerPhone
    items {
      productName
      size
      quantity
      unitPrice
      subtotal
    }
    subtotal
    deliveryFee
    discountAmount
    total
    paymentMethod
    orderType
  }
}
```

### 5. Today's Statistics

```graphql
query TodayStats {
  posTodayStats {
    date
    totalSales
    orderCount
    averageOrderValue
    cashSales
    cardSales
    deliveryOrders
    pickupOrders
  }
}
```

---

## Barcode Scanning Workflow

### How It Works

1. **USB barcode scanner** connected to Windows computer
2. Scanner works as **"keyboard wedge"** (types barcode automatically)
3. POS frontend has **auto-focused input field**
4. When barcode is scanned, it **queries the API**
5. Product is **found and added to cart**

### Frontend Implementation

```javascript
// BarcodeScanner.js
import React, { useRef, useEffect } from 'react';
import { useLazyQuery, gql } from '@apollo/client';

const SCAN_BARCODE = gql`
  query ScanBarcode($barcode: String!) {
    scanBarcode(barcode: $barcode) {
      id
      name
      currentPrice
      stockQuantity
      isInStock
    }
  }
`;

const BarcodeScanner = ({ onProductScanned }) => {
  const inputRef = useRef(null);
  const [scanBarcode, { data, loading, error }] = useLazyQuery(SCAN_BARCODE);

  // Auto-focus on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // When barcode is scanned
  const handleInput = (e) => {
    const barcode = e.target.value.trim();
    
    // Barcode typically 8-13 digits
    if (barcode.length >= 8) {
      scanBarcode({ variables: { barcode } });
      e.target.value = ''; // Clear for next scan
    }
  };

  // Handle scan result
  useEffect(() => {
    if (data?.scanBarcode) {
      onProductScanned(data.scanBarcode);
    }
  }, [data, onProductScanned]);

  return (
    <div className="barcode-scanner">
      <input
        ref={inputRef}
        type="text"
        placeholder="Scan barcode..."
        onInput={handleInput}
        autoFocus
        className="barcode-input"
      />
      {loading && <span>Scanning...</span>}
      {error && <span className="error">Product not found</span>}
    </div>
  );
};

export default BarcodeScanner;
```

---

## POS Complete Transaction Flow

```
1. Staff logs in
   ↓
2. POS interface opens
   ↓
3. Staff scans barcode (or searches product)
   ↓
4. Product added to cart
   ↓
5. Repeat for more items
   ↓
6. Enter customer info
   ↓
7. Select payment method (cash/card)
   ↓
8. Create order (stock automatically deducted)
   ↓
9. Print receipt
   ↓
10. Ready for next customer
```

---

# 📦 Inventory System

## Overview

The inventory system tracks:
- Stock quantities for products
- Stock movements (sales, receipts, adjustments)
- Low stock and out-of-stock alerts
- Stock history

---

## Inventory Models

### 1. StockItem
- Links to Product
- Stores current quantity
- Tracks reorder level
- Flags for low/out of stock

### 2. StockMovement
- Records every stock change
- Types: `sale`, `receipt`, `adjustment`, `return`, `damaged`
- Stores quantity before/after
- Links to user who made change

### 3. StockAlert
- Created when stock is low or out
- Can be acknowledged/resolved
- Helps managers track issues

---

## Enabling Inventory Tracking

### Per Product

Products have inventory fields:

```graphql
mutation EnableInventoryTracking {
  updateProduct(input: {
    id: "1"
    trackInventory: true
    reorderLevel: 10
    barcode: "1234567890123"
    sku: "PIZZA-MARG-001"
  }) {
    product {
      id
      name
      trackInventory
      reorderLevel
      barcode
      sku
    }
  }
}
```

---

## Inventory Queries

### 1. Get All Stock Items

```graphql
query AllStockItems {
  allStockItems {
    id
    product {
      id
      name
      barcode
    }
    quantity
    reorderLevel
    isLowStock
    isOutOfStock
    lastRestocked
  }
}
```

### 2. Get Stock for Product

```graphql
query StockByProduct($productId: ID!) {
  stockItemByProduct(productId: $productId) {
    id
    quantity
    reorderLevel
    isLowStock
    isOutOfStock
    lastRestocked
  }
}
```

### 3. Low Stock Items

```graphql
query LowStockItems {
  lowStockItems {
    id
    product {
      id
      name
      barcode
    }
    quantity
    reorderLevel
  }
}
```

### 4. Out of Stock Items

```graphql
query OutOfStockItems {
  outOfStockItems {
    id
    product {
      id
      name
    }
    quantity
  }
}
```

### 5. Stock Movement History

```graphql
query StockMovements($productId: ID!) {
  stockMovementsByProduct(productId: $productId) {
    id
    movementType
    quantityChange
    quantityBefore
    quantityAfter
    reference
    notes
    createdBy {
      username
    }
    createdAt
  }
}
```

### 6. Active Stock Alerts

```graphql
query ActiveAlerts {
  activeStockAlerts {
    id
    stockItem {
      product {
        name
      }
    }
    alertType
    message
    status
    createdAt
  }
}
```

---

## Inventory Mutations

### 1. Receive Stock (from supplier)

```graphql
mutation ReceiveStock {
  receiveStock(input: {
    productId: "1"
    quantity: 50
    notes: "Delivery from supplier"
  }) {
    success
    message
    stockItem {
      id
      quantity
    }
    stockMovement {
      id
      movementType
      quantityChange
    }
  }
}
```

### 2. Adjust Stock (manual correction)

```graphql
mutation AdjustStock {
  adjustStock(input: {
    productId: "1"
    quantityChange: -5
    movementType: "adjustment"
    notes: "Inventory count correction"
  }) {
    success
    message
    stockItem {
      quantity
    }
    stockMovement {
      id
      quantityChange
    }
  }
}
```

### 3. Return Stock (customer return)

```graphql
mutation ReturnStock {
  returnStock(input: {
    productId: "1"
    quantity: 1
    reference: "ORDER-12345"
    notes: "Customer returned item"
  }) {
    success
    stockItem {
      quantity
    }
  }
}
```

### 4. Acknowledge Stock Alert

```graphql
mutation AcknowledgeAlert($alertId: ID!) {
  acknowledgeStockAlert(alertId: $alertId) {
    success
    alert {
      id
      status
      acknowledgedAt
    }
  }
}
```

---

## Automatic Stock Deduction

When an order is created (via POS or online):

1. System checks if product tracks inventory
2. If yes, stock is **automatically deducted**
3. Stock movement is recorded (type: `sale`)
4. If stock goes low, alert is created
5. If stock goes to 0, out-of-stock alert is created

**No manual action needed!** Stock is managed automatically.

---

## Inventory Dashboard Features

### What to Build

1. **Overview Dashboard**
   - Total products tracking inventory
   - Low stock count
   - Out of stock count
   - Recent stock movements

2. **Stock Items List**
   - All products with stock
   - Filter by low/out of stock
   - Search by name/barcode

3. **Receive Stock Form**
   - Select product
   - Enter quantity
   - Add notes

4. **Adjust Stock Form**
   - Select product
   - Enter adjustment (+/-)
   - Select reason
   - Add notes

5. **Stock Movement History**
   - Filter by product
   - Filter by date
   - Filter by type

6. **Stock Alerts**
   - List of active alerts
   - Acknowledge button
   - Filter by type

---

# 🔄 Complete Workflow Examples

## Example 1: Setting Up New Cashier

### Step 1: Admin creates cashier account

```graphql
mutation {
  register(input: {
    username: "cashier_john"
    email: "john@store.com"
    password: "secure123"
    passwordConfirm: "secure123"
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
    user {
      id
      username
    }
  }
}
```

### Step 2: Cashier logs into POS

```graphql
mutation {
  login(input: {
    username: "cashier_john"
    password: "secure123"
  }) {
    success
    user {
      isStaffMember
    }
  }
}
```

### Step 3: Cashier uses POS

- Scan barcodes
- Create orders
- Print receipts

---

## Example 2: Daily Inventory Management

### Morning: Check stock levels

```graphql
query {
  lowStockItems {
    product { name }
    quantity
    reorderLevel
  }
  outOfStockItems {
    product { name }
  }
}
```

### When delivery arrives: Receive stock

```graphql
mutation {
  receiveStock(input: {
    productId: "1"
    quantity: 100
    notes: "Morning delivery"
  }) {
    success
    stockItem { quantity }
  }
}
```

### End of day: Check alerts

```graphql
query {
  activeStockAlerts {
    stockItem { product { name } }
    message
  }
}
```

---

## Example 3: Complete POS Transaction

### 1. Scan first item

```graphql
query {
  scanBarcode(barcode: "1234567890123") {
    id
    name
    currentPrice
  }
}
```

### 2. Scan second item

```graphql
query {
  scanBarcode(barcode: "9876543210987") {
    id
    name
    currentPrice
  }
}
```

### 3. Create order

```graphql
mutation {
  createPosOrder(input: {
    customerName: "Customer"
    customerPhone: "0412345678"
    orderType: "pickup"
    paymentMethod: "cash"
    items: [
      { productId: "1", quantity: 1 }
      { productId: "2", quantity: 2 }
    ]
  }) {
    success
    order {
      orderNumber
      total
    }
  }
}
```

### 4. Print receipt

```graphql
query {
  receipt(orderId: "1") {
    orderNumber
    items { productName quantity subtotal }
    total
  }
}
```

---

## Summary

### Staff System
- Two roles: Admin (full access) and Staff (limited)
- Staff have granular permissions
- Only admins can create users
- Both can access POS

### POS System
- For in-store transactions
- Barcode scanning support
- Direct order creation
- Receipt printing
- Daily statistics

### Inventory System
- Per-product tracking
- Automatic stock deduction on sales
- Receive, adjust, return stock
- Low stock alerts
- Movement history

---

**All systems are connected and working together!** 🎉
