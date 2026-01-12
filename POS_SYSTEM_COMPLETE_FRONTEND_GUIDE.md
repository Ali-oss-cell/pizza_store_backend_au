# 🖥️ POS System - Complete Frontend Integration Guide

**Complete documentation for building the Point of Sale (POS) frontend application.**

**API Endpoint:** `https://api.marinapizzas.com.au/graphql/`

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Authentication & Setup](#authentication--setup)
3. [GraphQL Queries](#graphql-queries)
4. [GraphQL Mutations](#graphql-mutations)
5. [Data Types & Structures](#data-types--structures)
6. [Complete Workflows](#complete-workflows)
7. [Barcode Scanning](#barcode-scanning)
8. [Error Handling](#error-handling)
9. [Frontend Implementation Examples](#frontend-implementation-examples)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

### What is the POS System?

The POS (Point of Sale) system is an in-store application that allows staff to:
- ✅ Scan barcodes to find products
- ✅ Create orders directly (no cart system)
- ✅ Process payments (cash, card, split)
- ✅ Print receipts
- ✅ View daily sales statistics
- ✅ Manage orders

### Who Can Access POS?

- ✅ **Admin users** - Full access
- ✅ **Staff users** - Full access (must have `canManageOrders: true`)
- ❌ **Customers** - No access

### Key Features

1. **Barcode Scanning** - USB barcode scanners work as keyboard input
2. **Direct Order Creation** - No cart, orders created immediately
3. **Stock Management** - Automatically deducts stock when orders are created
4. **Receipt Printing** - Formatted receipt data for printing
5. **Real-time Statistics** - Daily sales, order counts, top products

---

## 🔐 Authentication & Setup

### Step 1: Configure GraphQL Client

**Important:** You MUST include `credentials: 'include'` to send session cookies!

```javascript
import { ApolloClient, InMemoryCache, createHttpLink } from '@apollo/client';

const httpLink = createHttpLink({
  uri: 'https://api.marinapizzas.com.au/graphql/',
  credentials: 'include', // CRITICAL: Sends session cookies
});

const client = new ApolloClient({
  link: httpLink,
  cache: new InMemoryCache(),
  credentials: 'include',
});
```

### Step 2: Login Before Accessing POS

All POS queries and mutations require staff/admin authentication.

```graphql
mutation Login($input: LoginInput!) {
  login(input: $input) {
    success
    message
    user {
      id
      username
      email
      role
      isAdmin
      isStaffMember
      permissions
    }
  }
}
```

**Variables:**
```json
{
  "input": {
    "username": "cashier1",
    "password": "password123"
  }
}
```

### Step 3: Verify User Can Access POS

```graphql
query {
  me {
    id
    username
    role
    isAdmin
    isStaffMember
    permissions
  }
}
```

**Required:**
- `role: "staff"` OR `role: "admin"`
- `isStaffMember: true` OR `isAdmin: true`

**If user doesn't have access:**
- Redirect to login page
- Show error message: "You need staff access to use POS"

---

## 🔍 GraphQL Queries

### 1. Get All Products for POS

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
  "categoryId": null,        // Optional: Filter by category ID
  "search": null,            // Optional: Search by name/barcode/SKU
  "inStockOnly": false       // Optional: Show only in-stock items
}
```

**Example with filters:**
```json
{
  "categoryId": "1",
  "search": "pizza",
  "inStockOnly": true
}
```

**Response:**
```json
{
  "data": {
    "posProducts": [
      {
        "id": "1",
        "name": "Margherita Pizza",
        "basePrice": "14.99",
        "currentPrice": "14.99",
        "barcode": "1234567890123",
        "sku": "PIZZA-MARG-001",
        "stockQuantity": 50,
        "isInStock": true,
        "isLowStock": false,
        "category": "Pizzas",
        "imageUrl": "https://api.marinapizzas.com.au/media/products/pizza.jpg",
        "trackInventory": true
      }
    ]
  }
}
```

**Use Cases:**
- Display product grid in POS
- Search products by name/barcode/SKU
- Filter by category
- Show only available items

---

### 2. Get Single Product

Get a single product by ID.

```graphql
query POSProduct($productId: ID!) {
  posProduct(productId: $productId) {
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
  "productId": "1"
}
```

---

### 3. Scan Barcode ⭐ (KEY FEATURE)

**This is the main query for barcode scanning!**

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

**Response:**
```json
{
  "data": {
    "scanBarcode": {
      "id": "1",
      "name": "Margherita Pizza",
      "basePrice": "14.99",
      "currentPrice": "14.99",
      "barcode": "1234567890123",
      "stockQuantity": 50,
      "isInStock": true,
      "isLowStock": false,
      "category": "Pizzas",
      "imageUrl": "https://...",
      "trackInventory": true
    }
  }
}
```

**Error if barcode not found:**
```json
{
  "errors": [
    {
      "message": "Product with barcode '1234567890123' not found"
    }
  ]
}
```

---

### 4. Get Recent Orders

Get recent orders for POS display.

```graphql
query POSRecentOrders($limit: Int) {
  posRecentOrders(limit: $limit) {
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

**Variables:**
```json
{
  "limit": 20  // Optional: Default is 20
}
```

**Response:**
```json
{
  "data": {
    "posRecentOrders": [
      {
        "id": "1",
        "orderNumber": "ORD-2024-001",
        "customerName": "John Doe",
        "total": "29.98",
        "status": "confirmed",
        "orderType": "pickup",
        "createdAt": "2024-01-15T10:30:00Z",
        "itemCount": 2
      }
    ]
  }
}
```

---

### 5. Get Order Details

Get full order details by order ID.

```graphql
query POSOrder($orderId: ID!) {
  posOrder(orderId: $orderId) {
    id
    orderNumber
    customerName
    customerPhone
    customerEmail
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
      sizeName
      quantity
      unitPrice
      subtotal
      selectedToppings
    }
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

### 6. Get Receipt Data

Get formatted receipt data for printing.

```graphql
query Receipt($orderId: ID!) {
  receipt(orderId: $orderId) {
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

**Response:**
```json
{
  "data": {
    "receipt": {
      "orderNumber": "ORD-2024-001",
      "date": "2024-01-15",
      "time": "10:30:00",
      "customerName": "John Doe",
      "customerPhone": "0412345678",
      "customerEmail": "john@example.com",
      "items": [
        {
          "productName": "Margherita Pizza",
          "size": "Large",
          "quantity": 2,
          "unitPrice": "14.99",
          "subtotal": "29.98",
          "toppings": ["Extra Cheese", "Pepperoni"]
        }
      ],
      "subtotal": "29.98",
      "deliveryFee": "0.00",
      "discountAmount": "0.00",
      "total": "29.98",
      "paymentMethod": "cash",
      "orderType": "pickup",
      "deliveryAddress": ""
    }
  }
}
```

---

### 7. Get Today's Sales Statistics

Get today's sales statistics.

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
    topProducts
  }
}
```

**Response:**
```json
{
  "data": {
    "posTodayStats": {
      "date": "2024-01-15",
      "totalSales": "1250.50",
      "orderCount": 45,
      "averageOrderValue": "27.79",
      "cashSales": "500.00",
      "cardSales": "750.50",
      "deliveryOrders": 20,
      "pickupOrders": 25,
      "topProducts": [
        {
          "product_name": "Margherita Pizza",
          "total_quantity": 50,
          "total_revenue": "749.50"
        }
      ]
    }
  }
}
```

---

### 8. Get Daily Sales Statistics (Any Date)

Get sales statistics for a specific date.

```graphql
query POSDailyStats($date: String) {
  posDailyStats(date: $date) {
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

**Variables:**
```json
{
  "date": "2024-01-15"  // Format: YYYY-MM-DD, or null for today
}
```

---

## ✏️ GraphQL Mutations

### 1. Create POS Order ⭐ (KEY FEATURE)

Create an order directly from POS (no cart system).

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
    "orderType": "pickup",
    "deliveryAddress": "",
    "deliveryInstructions": "",
    "orderNotes": "Extra napkins please",
    "paymentMethod": "cash",
    "items": [
      {
        "productId": "1",
        "quantity": 2,
        "sizeId": "3",
        "toppings": [
          {
            "id": "1",
            "name": "Extra Cheese",
            "price": "2.00"
          }
        ]
      },
      {
        "productId": "5",
        "quantity": 1
      }
    ]
  }
}
```

**Required Fields:**
- `customerName` - String (required)
- `customerPhone` - String (required)
- `orderType` - String: `"delivery"` or `"pickup"` (required)
- `paymentMethod` - String: `"cash"`, `"card"`, or `"split"` (required)
- `items` - Array (required, must have at least 1 item)

**Optional Fields:**
- `customerEmail` - String
- `deliveryAddress` - String (required if `orderType: "delivery"`)
- `deliveryInstructions` - String
- `orderNotes` - String

**Item Structure:**
```json
{
  "productId": "1",        // Required: Product ID
  "quantity": 2,          // Required: Quantity (must be > 0)
  "sizeId": "3",           // Optional: Size ID
  "toppings": [            // Optional: Array of toppings
    {
      "id": "1",
      "name": "Extra Cheese",
      "price": "2.00"      // Price as string
    }
  ]
}
```

**Response (Success):**
```json
{
  "data": {
    "createPosOrder": {
      "success": true,
      "message": "Order created successfully! Order number: ORD-2024-001",
      "order": {
        "id": "1",
        "orderNumber": "ORD-2024-001",
        "total": "29.98",
        "status": "confirmed",
        "createdAt": "2024-01-15T10:30:00Z"
      }
    }
  }
}
```

**Response (Error):**
```json
{
  "errors": [
    {
      "message": "Order must have at least one item"
    }
  ]
}
```

**Important Notes:**
- ✅ Stock is automatically deducted when order is created
- ✅ Prices are calculated automatically (base price + size modifier + toppings)
- ✅ Order number is generated automatically
- ✅ Order status is set to `"confirmed"` automatically

---

## 📊 Data Types & Structures

### POSProductType

Product data optimized for POS display.

```typescript
interface POSProduct {
  id: string;
  name: string;
  basePrice: string;        // Decimal as string: "14.99"
  currentPrice: string;      // Current price (sale price if on sale)
  barcode: string | null;    // Barcode for scanning
  sku: string | null;        // SKU code
  stockQuantity: number;     // Current stock quantity
  isInStock: boolean;        // Whether product is in stock
  isLowStock: boolean;       // Whether stock is low
  category: string;          // Category name
  imageUrl: string | null;   // Full URL to product image
  trackInventory: boolean;   // Whether inventory is tracked
}
```

### POSOrderType

Simplified order data for POS display.

```typescript
interface POSOrder {
  id: string;
  orderNumber: string;
  customerName: string;
  total: string;            // Decimal as string
  status: string;           // "pending", "confirmed", "preparing", "ready", "delivered", "picked_up", "cancelled"
  orderType: string;         // "delivery" or "pickup"
  createdAt: string;         // ISO 8601 date string
  itemCount: number;         // Number of items in order
}
```

### ReceiptType

Formatted receipt data for printing.

```typescript
interface Receipt {
  orderNumber: string;
  date: string;             // Format: "YYYY-MM-DD"
  time: string;             // Format: "HH:MM:SS"
  customerName: string;
  customerPhone: string;
  customerEmail: string;
  items: ReceiptItem[];
  subtotal: string;
  deliveryFee: string;
  discountAmount: string;
  total: string;
  paymentMethod: string;
  orderType: string;
  deliveryAddress: string;
}

interface ReceiptItem {
  productName: string;
  size: string;
  quantity: number;
  unitPrice: string;
  subtotal: string;
  toppings: string[];        // Array of topping names
}
```

### DailySalesStatsType

Daily sales statistics.

```typescript
interface DailySalesStats {
  date: string;             // Format: "YYYY-MM-DD"
  totalSales: string;        // Decimal as string
  orderCount: number;
  averageOrderValue: string; // Decimal as string
  cashSales: string;        // Decimal as string
  cardSales: string;        // Decimal as string
  deliveryOrders: number;
  pickupOrders: number;
  topProducts: TopProduct[]; // Array of top products
}

interface TopProduct {
  product_name: string;
  total_quantity: number;
  total_revenue: string;    // Decimal as string
}
```

### POSOrderInput

Input for creating a POS order.

```typescript
interface POSOrderInput {
  customerName: string;      // Required
  customerPhone: string;     // Required
  customerEmail?: string;    // Optional
  orderType: "delivery" | "pickup"; // Required
  deliveryAddress?: string;  // Required if orderType is "delivery"
  deliveryInstructions?: string;
  orderNotes?: string;
  paymentMethod: "cash" | "card" | "split"; // Required
  items: POSOrderItemInput[]; // Required, must have at least 1 item
}

interface POSOrderItemInput {
  productId: string;         // Required
  quantity: number;          // Required, must be > 0
  sizeId?: string;           // Optional
  toppings?: ToppingInput[]; // Optional
}

interface ToppingInput {
  id: string;
  name: string;
  price: string;             // Decimal as string: "2.00"
}
```

---

## 🔄 Complete Workflows

### Workflow 1: Complete POS Transaction

**Step 1: User logs in**
```graphql
mutation {
  login(input: { username: "cashier1", password: "password123" }) {
    success
    user { id username role }
  }
}
```

**Step 2: Load products**
```graphql
query {
  posProducts {
    id
    name
    basePrice
    currentPrice
    barcode
    isInStock
  }
}
```

**Step 3: Scan barcode or select product**
- Option A: Scan barcode → `scanBarcode` query
- Option B: Click product from grid → Use product ID

**Step 4: Add to order (local state)**
- Store items in component state
- Calculate running total
- Show order summary

**Step 5: Collect customer info**
- Name (required)
- Phone (required)
- Email (optional)
- Order type: delivery or pickup
- Delivery address (if delivery)

**Step 6: Create order**
```graphql
mutation {
  createPosOrder(input: { ... }) {
    success
    message
    order { id orderNumber total }
  }
}
```

**Step 7: Get receipt and print**
```graphql
query {
  receipt(orderId: "1") {
    orderNumber
    date
    time
    customerName
    items { ... }
    total
  }
}
```

**Step 8: Show success message**
- Display order number
- Option to print receipt
- Option to create new order

---

### Workflow 2: Barcode Scanning

**Step 1: Setup barcode input field**
- Auto-focus on page load
- Listen for barcode input (scanner types automatically)

**Step 2: When barcode is scanned**
- Capture barcode value
- Call `scanBarcode` query

**Step 3: Handle response**
- If product found: Add to order
- If not found: Show error message

**Step 4: Clear input and focus again**
- Ready for next scan

---

### Workflow 3: View Daily Statistics

**Step 1: Load today's stats**
```graphql
query {
  posTodayStats {
    totalSales
    orderCount
    averageOrderValue
    topProducts
  }
}
```

**Step 2: Display statistics**
- Total sales
- Order count
- Average order value
- Top products

**Step 3: Option to view different date**
- Date picker
- Call `posDailyStats` with selected date

---

## 📱 Barcode Scanning

### How Barcode Scanners Work

1. **USB barcode scanner** connected to Windows computer
2. Scanner works as **"keyboard wedge"** (types barcode automatically)
3. POS frontend has **auto-focused input field**
4. When barcode is scanned, it **queries the API**
5. Product is **found and added to order**

### Frontend Implementation

```javascript
import React, { useRef, useEffect, useState } from 'react';
import { useLazyQuery } from '@apollo/client';
import { SCAN_BARCODE } from './queries';

function BarcodeScanner({ onProductScanned }) {
  const inputRef = useRef(null);
  const [barcode, setBarcode] = useState('');
  const [scanBarcode, { data, loading, error }] = useLazyQuery(SCAN_BARCODE);

  // Auto-focus on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // Handle barcode input
  const handleBarcodeChange = (e) => {
    const value = e.target.value;
    setBarcode(value);

    // When barcode is complete (usually 13 digits for EAN-13)
    if (value.length >= 13) {
      scanBarcode({ variables: { barcode: value } });
    }
  };

  // Handle scan result
  useEffect(() => {
    if (data?.scanBarcode) {
      onProductScanned(data.scanBarcode);
      setBarcode(''); // Clear input
      inputRef.current?.focus(); // Focus again for next scan
    }
  }, [data, onProductScanned]);

  // Handle errors
  useEffect(() => {
    if (error) {
      alert(`Product not found: ${error.message}`);
      setBarcode(''); // Clear input
      inputRef.current?.focus();
    }
  }, [error]);

  return (
    <input
      ref={inputRef}
      type="text"
      value={barcode}
      onChange={handleBarcodeChange}
      placeholder="Scan barcode..."
      style={{ fontSize: '20px', padding: '10px' }}
    />
  );
}
```

### GraphQL Query

```javascript
import { gql } from '@apollo/client';

export const SCAN_BARCODE = gql`
  query ScanBarcode($barcode: String!) {
    scanBarcode(barcode: $barcode) {
      id
      name
      basePrice
      currentPrice
      barcode
      stockQuantity
      isInStock
      isLowStock
      category
      imageUrl
    }
  }
`;
```

---

## ⚠️ Error Handling

### Common Errors

#### 1. Authentication Error

**Error:**
```json
{
  "errors": [
    {
      "message": "Permission denied. Staff access required for POS."
    }
  ]
}
```

**Solution:**
- Check if user is logged in
- Verify user has `role: "staff"` or `role: "admin"`
- Redirect to login if not authenticated

#### 2. Barcode Not Found

**Error:**
```json
{
  "errors": [
    {
      "message": "Product with barcode '1234567890123' not found"
    }
  ]
}
```

**Solution:**
- Show user-friendly error message
- Clear barcode input
- Focus input for next scan

#### 3. Order Creation Error

**Error:**
```json
{
  "errors": [
    {
      "message": "Order must have at least one item"
    }
  ]
}
```

**Solution:**
- Validate order before submission
- Show error message to user
- Highlight missing fields

#### 4. Stock Out of Stock

**Note:** Currently, orders can be created even if stock is low/out. Stock is deducted automatically.

**Future:** Backend may return error if stock is insufficient.

### Error Handling Best Practices

```javascript
const { data, error, loading } = useMutation(CREATE_POS_ORDER, {
  onError: (error) => {
    // Handle GraphQL errors
    if (error.graphQLErrors) {
      error.graphQLErrors.forEach(({ message }) => {
        if (message.includes('Permission denied')) {
          alert('You need staff access to create orders');
          // Redirect to login
        } else if (message.includes('not found')) {
          alert('Product not found. Please try again.');
        } else {
          alert(`Error: ${message}`);
        }
      });
    }
    
    // Handle network errors
    if (error.networkError) {
      alert('Network error. Please check your connection.');
    }
  },
  onCompleted: (data) => {
    if (data.createPosOrder.success) {
      alert(`Order created! ${data.createPosOrder.message}`);
      // Show success, print receipt, etc.
    }
  }
});
```

---

## 💻 Frontend Implementation Examples

### Complete POS Component Example

```javascript
import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useLazyQuery } from '@apollo/client';
import { gql } from '@apollo/client';

// Queries
const POS_PRODUCTS = gql`
  query POSProducts {
    posProducts {
      id
      name
      basePrice
      currentPrice
      barcode
      isInStock
      imageUrl
    }
  }
`;

const SCAN_BARCODE = gql`
  query ScanBarcode($barcode: String!) {
    scanBarcode(barcode: $barcode) {
      id
      name
      basePrice
      currentPrice
      isInStock
    }
  }
`;

const CREATE_POS_ORDER = gql`
  mutation CreatePOSOrder($input: POSOrderInput!) {
    createPosOrder(input: $input) {
      success
      message
      order {
        id
        orderNumber
        total
      }
    }
  }
`;

function POS() {
  const [orderItems, setOrderItems] = useState([]);
  const [customerName, setCustomerName] = useState('');
  const [customerPhone, setCustomerPhone] = useState('');
  const [orderType, setOrderType] = useState('pickup');
  const [paymentMethod, setPaymentMethod] = useState('cash');
  const [barcode, setBarcode] = useState('');

  // Load products
  const { data: productsData, loading: productsLoading } = useQuery(POS_PRODUCTS);
  
  // Scan barcode
  const [scanBarcode, { data: scanData }] = useLazyQuery(SCAN_BARCODE);
  
  // Create order
  const [createOrder, { loading: creatingOrder }] = useMutation(CREATE_POS_ORDER);

  // Handle barcode scan
  useEffect(() => {
    if (barcode.length >= 13) {
      scanBarcode({ variables: { barcode } });
      setBarcode('');
    }
  }, [barcode, scanBarcode]);

  // Add scanned product to order
  useEffect(() => {
    if (scanData?.scanBarcode) {
      const product = scanData.scanBarcode;
      addToOrder(product);
    }
  }, [scanData]);

  const addToOrder = (product) => {
    setOrderItems([...orderItems, {
      productId: product.id,
      productName: product.name,
      quantity: 1,
      price: product.currentPrice
    }]);
  };

  const removeFromOrder = (index) => {
    setOrderItems(orderItems.filter((_, i) => i !== index));
  };

  const calculateTotal = () => {
    return orderItems.reduce((sum, item) => {
      return sum + (parseFloat(item.price) * item.quantity);
    }, 0);
  };

  const handleCreateOrder = async () => {
    if (!customerName || !customerPhone) {
      alert('Please enter customer name and phone');
      return;
    }

    if (orderItems.length === 0) {
      alert('Please add items to order');
      return;
    }

    try {
      const { data } = await createOrder({
        variables: {
          input: {
            customerName,
            customerPhone,
            orderType,
            paymentMethod,
            items: orderItems.map(item => ({
              productId: item.productId,
              quantity: item.quantity
            }))
          }
        }
      });

      if (data.createPosOrder.success) {
        alert(`Order created! ${data.createPosOrder.message}`);
        // Reset form
        setOrderItems([]);
        setCustomerName('');
        setCustomerPhone('');
      }
    } catch (error) {
      alert(`Error: ${error.message}`);
    }
  };

  return (
    <div className="pos-container">
      <h1>Point of Sale</h1>
      
      {/* Barcode Scanner */}
      <input
        type="text"
        value={barcode}
        onChange={(e) => setBarcode(e.target.value)}
        placeholder="Scan barcode..."
        autoFocus
      />

      {/* Products Grid */}
      <div className="products-grid">
        {productsData?.posProducts?.map(product => (
          <div key={product.id} onClick={() => addToOrder(product)}>
            <img src={product.imageUrl} alt={product.name} />
            <h3>{product.name}</h3>
            <p>${product.currentPrice}</p>
            {!product.isInStock && <span>Out of Stock</span>}
          </div>
        ))}
      </div>

      {/* Order Summary */}
      <div className="order-summary">
        <h2>Current Order</h2>
        {orderItems.map((item, index) => (
          <div key={index}>
            <span>{item.productName} x{item.quantity}</span>
            <span>${(parseFloat(item.price) * item.quantity).toFixed(2)}</span>
            <button onClick={() => removeFromOrder(index)}>Remove</button>
          </div>
        ))}
        <div className="total">
          <strong>Total: ${calculateTotal().toFixed(2)}</strong>
        </div>
      </div>

      {/* Customer Info */}
      <div className="customer-info">
        <input
          type="text"
          placeholder="Customer Name"
          value={customerName}
          onChange={(e) => setCustomerName(e.target.value)}
        />
        <input
          type="tel"
          placeholder="Phone"
          value={customerPhone}
          onChange={(e) => setCustomerPhone(e.target.value)}
        />
        <select value={orderType} onChange={(e) => setOrderType(e.target.value)}>
          <option value="pickup">Pickup</option>
          <option value="delivery">Delivery</option>
        </select>
        <select value={paymentMethod} onChange={(e) => setPaymentMethod(e.target.value)}>
          <option value="cash">Cash</option>
          <option value="card">Card</option>
          <option value="split">Split</option>
        </select>
      </div>

      {/* Create Order Button */}
      <button onClick={handleCreateOrder} disabled={creatingOrder}>
        {creatingOrder ? 'Creating...' : 'Create Order'}
      </button>
    </div>
  );
}

export default POS;
```

---

## ✅ Best Practices

### 1. Always Check Authentication

```javascript
// Before accessing POS
const { data: userData } = useQuery(ME_QUERY);

useEffect(() => {
  if (userData?.me && !userData.me.isStaffMember && !userData.me.isAdmin) {
    // Redirect to login
    window.location.href = '/login';
  }
}, [userData]);
```

### 2. Handle Loading States

```javascript
const { data, loading, error } = useQuery(POS_PRODUCTS);

if (loading) return <div>Loading products...</div>;
if (error) return <div>Error: {error.message}</div>;
```

### 3. Validate Before Submission

```javascript
const validateOrder = () => {
  if (!customerName) return 'Customer name is required';
  if (!customerPhone) return 'Customer phone is required';
  if (orderItems.length === 0) return 'Order must have at least one item';
  if (orderType === 'delivery' && !deliveryAddress) {
    return 'Delivery address is required';
  }
  return null;
};
```

### 4. Show User Feedback

```javascript
// Success
if (data.createPosOrder.success) {
  toast.success(`Order created! ${data.createPosOrder.message}`);
}

// Error
if (error) {
  toast.error(`Error: ${error.message}`);
}
```

### 5. Auto-focus Barcode Input

```javascript
useEffect(() => {
  barcodeInputRef.current?.focus();
}, []);
```

### 6. Clear Input After Scan

```javascript
// After successful scan
setBarcode('');
barcodeInputRef.current?.focus();
```

### 7. Format Prices

```javascript
const formatPrice = (price) => {
  return parseFloat(price).toFixed(2);
};
```

### 8. Handle Stock Warnings

```javascript
{!product.isInStock && (
  <span className="out-of-stock">Out of Stock</span>
)}
{product.isLowStock && (
  <span className="low-stock">Low Stock</span>
)}
```

---

## 🐛 Troubleshooting

### Issue: 400 Bad Request

**Cause:** User not authenticated or query format issue

**Solution:**
1. Check if user is logged in
2. Verify GraphQL client has `credentials: 'include'`
3. Check query syntax

### Issue: Permission Denied

**Cause:** User doesn't have staff/admin role

**Solution:**
1. Verify user has `role: "staff"` or `role: "admin"`
2. Check user permissions
3. Login as admin to create staff users

### Issue: Barcode Not Found

**Cause:** Product doesn't have barcode or barcode is incorrect

**Solution:**
1. Verify product has barcode in database
2. Check barcode format (usually 13 digits for EAN-13)
3. Show user-friendly error message

### Issue: Order Creation Fails

**Cause:** Missing required fields or invalid data

**Solution:**
1. Validate all required fields before submission
2. Check error message from API
3. Ensure items array is not empty

---

## 📞 Support

**API Endpoint:** `https://api.marinapizzas.com.au/graphql/`

**Test Queries:** Use GraphiQL at `https://api.marinapizzas.com.au/graphql/`

**Common Issues:**
- Check browser console for errors
- Check Network tab for request/response
- Verify authentication status
- Check server logs for detailed errors

---

**This guide covers everything you need to build the POS frontend!** 🎉

For additional questions or issues, refer to:
- `POS_TROUBLESHOOTING.md` - Detailed troubleshooting guide
- `CREATE_POS_USER_GUIDE.md` - How to create POS users
- `STAFF_POS_INVENTORY_COMPLETE_GUIDE.md` - Complete system overview
