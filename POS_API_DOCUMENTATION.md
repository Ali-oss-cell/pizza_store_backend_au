# POS API Documentation

## 🎯 Phase 2: POS API Extensions - Complete

All POS-specific GraphQL queries and mutations are now available for the Point of Sale frontend.

---

## 📋 Available POS Queries

### **1. Get Products for POS**

Optimized product list for POS display with stock information.

```graphql
query {
  posProducts(
    categoryId: "1"  # Optional: filter by category
    search: "pizza"  # Optional: search by name/SKU/barcode
    inStockOnly: true  # Optional: only show in-stock items
  ) {
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

### **2. Get Single Product for POS**

```graphql
query {
  posProduct(productId: "1") {
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
  }
}
```

### **3. Scan Barcode (POS Barcode Scanner)**

**This is the key query for barcode scanning!**

```graphql
query {
  scanBarcode(barcode: "1234567890123") {
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
  }
}
```

**Usage in POS:**
1. User scans barcode with scanner
2. Scanner types barcode into input field
3. Call this query with the barcode
4. Product is returned instantly
5. Add to cart or display product details

### **4. Get Recent Orders**

Get recent orders for POS display.

```graphql
query {
  posRecentOrders(limit: 20) {
    id
    orderNumber
    customerName
    total
    status
    orderType
    createdAt
    itemCount
  }
}
```

### **5. Get Order Details**

```graphql
query {
  posOrder(orderId: "1") {
    id
    orderNumber
    customerName
    customerPhone
    customerEmail
    total
    status
    orderType
    items {
      id
      productName
      quantity
      unitPrice
      subtotal
    }
    createdAt
  }
}
```

### **6. Generate Receipt**

Get formatted receipt data for printing.

```graphql
query {
  receipt(orderId: "1") {
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

**Receipt Format:**
- Ready for thermal printer (80mm width)
- Includes all order details
- Formatted date and time
- Itemized list with prices
- Totals and payment info

### **7. Daily Sales Statistics**

Get daily sales statistics for reporting.

```graphql
query {
  posDailyStats(date: "2024-12-29") {  # Optional: defaults to today
    date
    totalSales
    orderCount
    averageOrderValue
    cashSales
    cardSales
    deliveryOrders
    pickupOrders
    topProducts
  }
}
```

### **8. Today's Statistics**

Quick access to today's stats.

```graphql
query {
  posTodayStats {
    date
    totalSales
    orderCount
    averageOrderValue
    cashSales
    cardSales
    deliveryOrders
    pickupOrders
    topProducts
  }
}
```

---

## 🔧 Available POS Mutations

### **Create Order from POS**

Create order directly from POS (without cart system).

```graphql
mutation {
  createPosOrder(input: {
    customerName: "John Doe"
    customerPhone: "0412345678"
    customerEmail: "john@example.com"
    orderType: "pickup"  # or "delivery"
    deliveryAddress: "123 Main St"  # Required if delivery
    deliveryInstructions: "Ring doorbell"
    orderNotes: "Extra napkins please"
    paymentMethod: "cash"  # "cash", "card", or "split"
    items: [
      {
        productId: "1"
        quantity: 2
        sizeId: "3"  # Optional
        toppings: [  # Optional
          {
            id: "1"
            name: "Extra Cheese"
            price: "2.00"
          }
        ]
      },
      {
        productId: "5"
        quantity: 1
      }
    ]
  }) {
    success
    message
    order {
      id
      orderNumber
      total
      status
    }
  }
}
```

**Features:**
- ✅ Creates order directly (no cart needed)
- ✅ Automatically deducts stock
- ✅ Calculates prices (including sizes and toppings)
- ✅ Supports delivery and pickup
- ✅ Returns order with order number

---

## 🔐 Authentication

**All POS queries and mutations require staff/admin authentication.**

You must be logged in as a staff member or admin to use POS endpoints.

**Login first:**
```graphql
mutation {
  login(input: {
    username: "admin"
    password: "yourpassword"
  }) {
    success
    user {
      id
      username
      role
      isStaffMember
    }
  }
}
```

---

## 📊 POS Product Type Fields

The `POSProductType` includes all necessary fields for POS display:

- `id` - Product ID
- `name` - Product name
- `basePrice` - Base price
- `currentPrice` - Current price (sale price if on sale)
- `barcode` - Barcode for scanning
- `sku` - SKU code
- `stockQuantity` - Current stock quantity
- `isInStock` - Whether product is in stock
- `isLowStock` - Whether stock is low
- `category` - Category name
- `imageUrl` - Full URL to product image
- `trackInventory` - Whether inventory is tracked

---

## 🎯 POS Workflow Example

### **Complete POS Transaction Flow:**

1. **Login**
```graphql
mutation { login(input: { username: "staff", password: "pass" }) { success } }
```

2. **Scan Barcode**
```graphql
query { scanBarcode(barcode: "1234567890123") { id name currentPrice stockQuantity } }
```

3. **Get Products (if needed)**
```graphql
query { posProducts(inStockOnly: true) { id name currentPrice } }
```

4. **Create Order**
```graphql
mutation {
  createPosOrder(input: {
    customerName: "Customer Name"
    customerPhone: "0412345678"
    orderType: "pickup"
    paymentMethod: "cash"
    items: [{ productId: "1", quantity: 1 }]
  }) {
    order { orderNumber total }
  }
}
```

5. **Generate Receipt**
```graphql
query { receipt(orderId: "1") { orderNumber items { productName quantity subtotal } total } }
```

6. **View Today's Stats**
```graphql
query { posTodayStats { totalSales orderCount } }
```

---

## 🚀 Integration with Barcode Scanner

### **How Barcode Scanning Works:**

1. **Hardware Setup:**
   - USB barcode scanner connected to Windows computer
   - Scanner works as "keyboard wedge" (types barcode automatically)

2. **Frontend Implementation:**
   ```javascript
   // Auto-focus on barcode input field
   const barcodeInput = document.getElementById('barcode-input');
   barcodeInput.focus();
   
   // When barcode is scanned (auto-typed by scanner)
   barcodeInput.addEventListener('input', async (e) => {
     const barcode = e.target.value;
     
     // Call GraphQL query
     const result = await graphql(`
       query { scanBarcode(barcode: "${barcode}") { id name currentPrice stockQuantity } }
     `);
     
     // Display product and add to cart
     if (result.data.scanBarcode) {
       addToCart(result.data.scanBarcode);
     }
     
     // Clear input for next scan
     e.target.value = '';
   });
   ```

3. **No Special Drivers Needed:**
   - USB scanners work automatically
   - Just focus on input field and scan
   - Barcode is typed like keyboard input

---

## 📝 Receipt Printing

### **Receipt Data Format:**

The `receipt` query returns data formatted for thermal printers:

```json
{
  "orderNumber": "ORD-20241229-A3B7",
  "date": "2024-12-29",
  "time": "14:30:15",
  "customerName": "John Doe",
  "items": [
    {
      "productName": "Margherita Pizza",
      "size": "Large",
      "quantity": 2,
      "unitPrice": "15.99",
      "subtotal": "31.98",
      "toppings": ["Extra Cheese"]
    }
  ],
  "subtotal": "31.98",
  "deliveryFee": "0.00",
  "discountAmount": "0.00",
  "total": "31.98"
}
```

**Frontend can:**
- Format this data for thermal printer
- Use browser print API
- Or send to printer via ESC/POS commands

---

## ✅ Status

**Phase 2 Complete!**

All POS API extensions are implemented and ready for frontend integration:

- ✅ POS-optimized product queries
- ✅ Barcode scanning query
- ✅ Recent orders query
- ✅ Receipt generation
- ✅ Daily sales statistics
- ✅ POS order creation mutation
- ✅ Stock information included
- ✅ Staff authentication required

**Ready for POS frontend development!**

