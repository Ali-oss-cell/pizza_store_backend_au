# POS & Inventory GraphQL Reference Guide

Complete reference for all GraphQL queries and mutations needed for POS and Inventory management.

---

## 📋 Table of Contents

1. [POS Queries](#pos-queries)
2. [POS Mutations](#pos-mutations)
3. [Inventory Queries](#inventory-queries)
4. [Inventory Mutations](#inventory-mutations)
5. [Barcode Operations](#barcode-operations)
6. [Complete Examples](#complete-examples)

---

## 🔍 POS Queries

### **1. Get POS Products**

Get all products optimized for POS display with stock information.

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

**Variables:**
```json
{
  "categoryId": "1",        // Optional: Filter by category
  "search": "pizza",        // Optional: Search by name/barcode/SKU
  "inStockOnly": true        // Optional: Show only in-stock items
}
```

**Use Cases:**
- Display product grid in POS
- Search products
- Filter by category
- Show only available items

---

### **2. Get Single POS Product**

Get a single product by ID, barcode, or SKU.

```graphql
query POSProduct($productId: ID, $barcode: String, $sku: String) {
  posProduct(id: $productId, barcode: $barcode, sku: $sku) {
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

**Variables:**
```json
{
  "productId": "1"          // Use ID, barcode, OR sku (not all)
}
```

---

### **3. Scan Barcode**

Scan a barcode to find product (main POS operation).

```graphql
query ScanBarcode($barcode: String!) {
  scanBarcode(barcode: $barcode) {
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

**Variables:**
```json
{
  "barcode": "1234567890123"
}
```

**Use Case:**
- Barcode scanner integration
- Quick product lookup

---

### **4. Get Recent Orders**

Get recent orders for POS display.

```graphql
query POSRecentOrders($limit: Int) {
  posRecentOrders(limit: $limit) {
    id
    orderNumber
    customerName
    customerPhone
    total
    status
    orderType
    createdAt
    itemCount
  }
}
```

**Variables:**
```json
{
  "limit": 20              // Optional: Default 20
}
```

---

### **5. Get Single Order**

Get order details by ID or order number.

```graphql
query POSOrder($orderId: ID, $orderNumber: String) {
  posOrder(id: $orderId, orderNumber: $orderNumber) {
    id
    orderNumber
    customerName
    customerPhone
    orderType
    status
    subtotal
    deliveryFee
    discountAmount
    total
    createdAt
    items {
      id
      productName
      quantity
      unitPrice
      subtotal
    }
  }
}
```

**Variables:**
```json
{
  "orderId": "1"           // OR orderNumber
}
```

---

### **6. Get Receipt Data**

Get formatted receipt data for printing.

```graphql
query Receipt($orderId: ID, $orderNumber: String) {
  receipt(orderId: $orderId, orderNumber: $orderNumber) {
    orderNumber
    date
    time
    customerName
    customerPhone
    customerEmail
    items {
      productName
      size
      quantity
      unitPrice
      subtotal
      toppings
    }
    subtotal
    deliveryFee
    discountAmount
    total
    paymentMethod
    orderType
    deliveryAddress
  }
}
```

**Variables:**
```json
{
  "orderId": "1"
}
```

---

### **7. Get Today's Statistics**

Get today's sales and inventory statistics.

```graphql
query POSTodayStats {
  posTodayStats {
    date
    totalSales
    orderCount
    averageOrderValue
    cashSales
    cardSales
    deliveryOrders
    pickupOrders
    topProducts {
      id
      name
      currentPrice
    }
  }
}
```

**Use Case:**
- POS dashboard
- Daily sales summary

---

### **8. Get Daily Statistics**

Get sales statistics for multiple days.

```graphql
query POSDailyStats($days: Int) {
  posDailyStats(days: $days) {
    date
    totalSales
    orderCount
    averageOrderValue
    cashSales
    cardSales
    deliveryOrders
    pickupOrders
    topProducts {
      id
      name
      currentPrice
    }
  }
}
```

**Variables:**
```json
{
  "days": 7                // Optional: Default 7
}
```

---

## ✏️ POS Mutations

### **1. Create POS Order**

Create an order directly from POS (no cart needed).

```graphql
mutation CreatePOSOrder($input: POSOrderInput!) {
  createPosOrder(input: $input) {
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

**Variables:**
```json
{
  "input": {
    "customerName": "John Doe",
    "customerPhone": "0412345678",
    "customerEmail": "john@example.com",
    "orderType": "pickup",              // "pickup" | "delivery" | "dine_in"
    "deliveryAddress": "",               // Required if delivery
    "deliveryInstructions": "",
    "orderNotes": "",
    "paymentMethod": "cash",             // "cash" | "card" | "split"
    "items": [
      {
        "productId": "1",
        "quantity": 2,
        "sizeId": "1",                   // Optional
        "toppings": []                   // Optional
      }
    ]
  }
}
```

**Notes:**
- Automatically deducts stock if tracking enabled
- Generates unique order number
- Calculates totals automatically

---

## 📦 Inventory Queries

### **1. Get All Stock Items**

Get all products with stock information.

```graphql
query AllStockItems {
  allStockItems {
    id
    product {
      id
      name
      barcode
      sku
    }
    quantity
    reorderLevel
    reorderQuantity
    lastRestocked
    isLowStock
    isOutOfStock
    createdAt
    updatedAt
  }
}
```

---

### **2. Get Stock Item by Product**

Get stock information for a specific product.

```graphql
query StockItemByProduct($productId: ID!) {
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

**Variables:**
```json
{
  "productId": "1"
}
```

---

### **3. Get Low Stock Items**

Get all products with low stock (below reorder level).

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
    isLowStock
  }
}
```

---

### **4. Get Out of Stock Items**

Get all products that are out of stock.

```graphql
query OutOfStockItems {
  outOfStockItems {
    id
    product {
      id
      name
      barcode
    }
    quantity
    isOutOfStock
  }
}
```

---

### **5. Get Stock Movements**

Get stock movement history for a product.

```graphql
query StockMovementsByProduct($productId: ID!) {
  stockMovementsByProduct(productId: $productId) {
    id
    movementType
    quantityChange
    quantityBefore
    quantityAfter
    reference
    notes
    createdBy {
      id
      username
    }
    createdAt
  }
}
```

**Variables:**
```json
{
  "productId": "1"
}
```

---

### **6. Get All Stock Movements**

Get all stock movements across all products.

```graphql
query AllStockMovements {
  allStockMovements {
    id
    stockItem {
      product {
        name
      }
    }
    movementType
    quantityChange
    quantityBefore
    quantityAfter
    reference
    createdAt
  }
}
```

---

### **7. Get Stock Alerts**

Get all active stock alerts.

```graphql
query ActiveStockAlerts {
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

### **8. Find Product by Barcode**

Find product using barcode (alternative to scanBarcode).

```graphql
query ProductByBarcode($barcode: String!) {
  productByBarcode(barcode: $barcode) {
    id
    name
    barcode
    currentPrice
    stockQuantity
    isInStock
  }
}
```

**Variables:**
```json
{
  "barcode": "1234567890123"
}
```

---

### **9. Find Product by SKU**

Find product using SKU.

```graphql
query ProductBySKU($sku: String!) {
  productBySku(sku: $sku) {
    id
    name
    sku
    currentPrice
    stockQuantity
    isInStock
  }
}
```

**Variables:**
```json
{
  "sku": "PIZZ-MARG-0001"
}
```

---

## 🔧 Inventory Mutations

### **1. Adjust Stock**

Manually adjust stock (increase or decrease).

```graphql
mutation AdjustStock($input: AdjustStockInput!) {
  adjustStock(input: $input) {
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

**Variables:**
```json
{
  "input": {
    "productId": "1",
    "quantityChange": -5,              // Negative = decrease, Positive = increase
    "movementType": "adjustment",      // "sale" | "adjustment" | "receipt" | "return" | "damaged"
    "reference": "Manual adjustment",
    "notes": "Correcting inventory count"
  }
}
```

---

### **2. Receive Stock**

Add stock when receiving from supplier.

```graphql
mutation ReceiveStock($input: ReceiveStockInput!) {
  receiveStock(input: $input) {
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

**Variables:**
```json
{
  "input": {
    "productId": "1",
    "quantity": 50,
    "notes": "Received from supplier"
  }
}
```

---

### **3. Return Stock**

Add stock back (e.g., customer return).

```graphql
mutation ReturnStock($input: ReturnStockInput!) {
  returnStock(input: $input) {
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

**Variables:**
```json
{
  "input": {
    "productId": "1",
    "quantity": 1,
    "reference": "ORDER-12345",
    "notes": "Customer return"
  }
}
```

---

### **4. Acknowledge Stock Alert**

Mark a stock alert as acknowledged/resolved.

```graphql
mutation AcknowledgeStockAlert($alertId: ID!) {
  acknowledgeStockAlert(alertId: $alertId) {
    success
    message
    alert {
      id
      status
      acknowledgedAt
    }
  }
}
```

**Variables:**
```json
{
  "alertId": "1"
}
```

---

## 🏷️ Barcode Operations

### **1. Generate Barcode for Product**

Generate and assign barcode to a product.

```graphql
mutation GenerateBarcode($productId: ID!, $barcode: String) {
  generateBarcode(productId: $productId, barcode: $barcode) {
    success
    message
    barcode
    product {
      id
      name
      barcode
    }
  }
}
```

**Variables:**
```json
{
  "productId": "1",
  "barcode": null              // Optional: Auto-generate if null
}
```

---

### **2. Generate SKU for Product**

Generate and assign SKU to a product.

```graphql
mutation GenerateSKU($productId: ID!, $sku: String) {
  generateSku(productId: $productId, sku: $sku) {
    success
    message
    sku
    product {
      id
      name
      sku
    }
  }
}
```

**Variables:**
```json
{
  "productId": "1",
  "sku": null                  // Optional: Auto-generate if null
}
```

---

### **3. Generate All Barcodes**

Generate barcodes and SKUs for all products (Admin only).

```graphql
mutation GenerateAllBarcodes {
  generateAllBarcodes {
    success
    message
    barcodesAssigned
    skusAssigned
    errors
  }
}
```

**Use Case:**
- Bulk barcode generation
- Initial setup

---

## 📝 Complete Examples

### **Example 1: Complete POS Transaction**

```graphql
# Step 1: Scan barcode
query {
  scanBarcode(barcode: "1234567890123") {
    id
    name
    currentPrice
    stockQuantity
    isInStock
  }
}

# Step 2: Create order
mutation {
  createPosOrder(input: {
    customerName: "John Doe"
    customerPhone: "0412345678"
    orderType: "pickup"
    paymentMethod: "cash"
    items: [
      {
        productId: "1"
        quantity: 2
      }
    ]
  }) {
    success
    order {
      orderNumber
      total
    }
  }
}

# Step 3: Get receipt
query {
  receipt(orderId: "1") {
    orderNumber
    items {
      productName
      quantity
      subtotal
    }
    total
  }
}
```

---

### **Example 2: Inventory Management**

```graphql
# Check stock levels
query {
  lowStockItems {
    product {
      name
      barcode
    }
    quantity
    reorderLevel
  }
}

# Receive stock
mutation {
  receiveStock(input: {
    productId: "1"
    quantity: 50
    notes: "New shipment received"
  }) {
    success
    stockItem {
      quantity
    }
  }
}

# View stock movements
query {
  stockMovementsByProduct(productId: "1") {
    movementType
    quantityChange
    createdAt
  }
}
```

---

### **Example 3: Daily Operations**

```graphql
# Get today's stats
query {
  posTodayStats {
    totalSales
    orderCount
    topProducts {
      name
    }
  }
}

# Get recent orders
query {
  posRecentOrders(limit: 10) {
    orderNumber
    customerName
    total
    status
  }
}

# Check inventory alerts
query {
  activeStockAlerts {
    stockItem {
      product {
        name
      }
    }
    message
  }
}
```

---

## 🔐 Authentication Requirements

### **POS Operations:**
- Requires: Staff or Admin (`isStaffMember` or `isAdmin`)
- All POS queries and mutations require authentication

### **Inventory Operations:**
- Requires: Staff or Admin
- Some operations (like `generateAllBarcodes`) require Admin only

### **Example Login:**
```graphql
mutation {
  login(input: {
    username: "staff"
    password: "password"
  }) {
    success
    user {
      id
      username
      isStaffMember
      isAdmin
    }
  }
}
```

---

## 📊 Response Types

### **POSProductType:**
```typescript
{
  id: string
  name: string
  basePrice: number
  currentPrice: number
  barcode: string | null
  sku: string | null
  stockQuantity: number | null
  isInStock: boolean
  isLowStock: boolean
  category: string
  imageUrl: string | null
  trackInventory: boolean
}
```

### **StockItemType:**
```typescript
{
  id: string
  product: ProductType
  quantity: number
  reorderLevel: number
  reorderQuantity: number
  lastRestocked: string | null
  isLowStock: boolean
  isOutOfStock: boolean
  createdAt: string
  updatedAt: string
}
```

### **StockMovementType:**
```typescript
{
  id: string
  stockItem: StockItemType
  movementType: "sale" | "adjustment" | "receipt" | "return" | "damaged"
  quantityChange: number
  quantityBefore: number
  quantityAfter: number
  reference: string
  notes: string
  createdBy: UserType | null
  createdAt: string
}
```

---

## 🚀 Quick Reference

### **Most Common POS Operations:**

1. **Scan Barcode** → `scanBarcode(barcode: String!)`
2. **Get Products** → `posProducts(...)`
3. **Create Order** → `createPosOrder(input: POSOrderInput!)`
4. **Get Receipt** → `receipt(orderId: ID!)`
5. **Today's Stats** → `posTodayStats`

### **Most Common Inventory Operations:**

1. **Check Stock** → `stockItemByProduct(productId: ID!)`
2. **Low Stock** → `lowStockItems`
3. **Receive Stock** → `receiveStock(input: ReceiveStockInput!)`
4. **Adjust Stock** → `adjustStock(input: AdjustStockInput!)`
5. **Stock Movements** → `stockMovementsByProduct(productId: ID!)`

---

## 📝 Notes

- All queries/mutations require authentication (staff/admin)
- Stock is automatically deducted when creating POS orders
- Barcodes are auto-generated if not provided
- All prices are in Decimal format (handle as numbers)
- Dates are in ISO 8601 format
- Stock quantities are integers

---

**This is your complete GraphQL reference for POS and Inventory!** 🎯
