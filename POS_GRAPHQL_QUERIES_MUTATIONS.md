# POS GraphQL Queries and Mutations Reference

Complete reference for all POS-related GraphQL operations.

## Table of Contents
- [Queries](#queries)
  - [Product Queries](#product-queries)
  - [Barcode Scanning](#barcode-scanning)
  - [Order Queries](#order-queries)
  - [Receipt Generation](#receipt-generation)
  - [Sales Statistics](#sales-statistics)
- [Mutations](#mutations)
  - [Create POS Order](#create-pos-order)
- [Inventory Queries](#inventory-queries)
- [Inventory Mutations](#inventory-mutations)

---

## Queries

### Product Queries

#### Get All POS Products
Get all products optimized for POS display with stock information.

```graphql
query GetPOSProducts($categoryId: ID, $search: String, $inStockOnly: Boolean) {
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
  "categoryId": "1",  // Optional: Filter by category
  "search": "pepperoni",  // Optional: Search by name, SKU, or barcode
  "inStockOnly": true  // Optional: Only show in-stock items
}
```

**Response:**
```json
{
  "data": {
    "posProducts": [
      {
        "id": "1",
        "name": "Pepperoni Pizza",
        "basePrice": "15.99",
        "currentPrice": "15.99",
        "barcode": "1234567890123",
        "sku": "PIZ-PEP-001",
        "stockQuantity": 50,
        "isInStock": true,
        "isLowStock": false,
        "category": "Pizzas",
        "imageUrl": "https://api.marinapizzas.com.au/media/products/pepperoni.jpg",
        "trackInventory": true
      }
    ]
  }
}
```

---

#### Get Single POS Product
Get a single product by ID for POS.

```graphql
query GetPOSProduct($productId: ID!) {
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

### Barcode Scanning

#### Scan Barcode
Scan a barcode and get the product information.

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

**Error Response (if not found):**
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

### Order Queries

#### Get Recent Orders
Get recent orders for POS display.

```graphql
query GetRecentOrders($limit: Int) {
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
        "total": "45.99",
        "status": "CONFIRMED",
        "orderType": "delivery",
        "createdAt": "2024-01-15T10:30:00Z",
        "itemCount": 3
      }
    ]
  }
}
```

---

#### Get Order Details
Get full order details for POS.

```graphql
query GetPOSOrder($orderId: ID!) {
  posOrder(orderId: $orderId) {
    id
    orderNumber
    customerName
    customerEmail
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
      sizeName
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

### Receipt Generation

#### Generate Receipt
Generate receipt data for printing.

```graphql
query GetReceipt($orderId: ID!) {
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
          "productName": "Pepperoni Pizza",
          "size": "Large",
          "quantity": 2,
          "unitPrice": "15.99",
          "subtotal": "31.98",
          "toppings": ["Extra Cheese", "Mushrooms"]
        }
      ],
      "subtotal": "31.98",
      "deliveryFee": "5.00",
      "discountAmount": "0.00",
      "total": "36.98",
      "paymentMethod": "",
      "orderType": "delivery",
      "deliveryAddress": "123 Main St, City"
    }
  }
}
```

---

### Sales Statistics

#### Get Daily Sales Stats
Get daily sales statistics for a specific date.

```graphql
query GetDailyStats($date: String) {
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
  "date": "2024-01-15"  // Optional: YYYY-MM-DD format, defaults to today
}
```

**Response:**
```json
{
  "data": {
    "posDailyStats": {
      "date": "2024-01-15",
      "totalSales": "1250.50",
      "orderCount": 45,
      "averageOrderValue": "27.79",
      "cashSales": "500.00",
      "cardSales": "750.50",
      "deliveryOrders": 30,
      "pickupOrders": 15,
      "topProducts": [
        {
          "product_name": "Pepperoni Pizza",
          "total_quantity": 25,
          "total_revenue": "399.75"
        }
      ]
    }
  }
}
```

---

#### Get Today's Stats
Get today's sales statistics (convenience query).

```graphql
query GetTodayStats {
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

## Mutations

### Create POS Order

#### Create Order from POS
Create an order directly from POS without using cart.

```graphql
mutation CreatePOSOrder($input: POSOrderInput!) {
  createPosOrder(input: $input) {
    success
    message
    order {
      id
      orderNumber
      customerName
      total
      status
      orderType
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
    "orderType": "delivery",
    "deliveryAddress": "123 Main St, City, State 1234",
    "deliveryInstructions": "Ring doorbell",
    "orderNotes": "Extra napkins please",
    "paymentMethod": "card",
    "items": [
      {
        "productId": "1",
        "quantity": 2,
        "sizeId": "2",
        "toppings": [
          {
            "id": "1",
            "name": "Extra Cheese",
            "price": "2.00"
          },
          {
            "id": "2",
            "name": "Mushrooms",
            "price": "1.50"
          }
        ]
      },
      {
        "productId": "3",
        "quantity": 1,
        "sizeId": "1"
      }
    ]
  }
}
```

**Response:**
```json
{
  "data": {
    "createPosOrder": {
      "success": true,
      "message": "Order created successfully! Order number: ORD-2024-001",
      "order": {
        "id": "1",
        "orderNumber": "ORD-2024-001",
        "customerName": "John Doe",
        "total": "45.99",
        "status": "CONFIRMED",
        "orderType": "delivery",
        "createdAt": "2024-01-15T10:30:00Z"
      }
    }
  }
}
```

**Important Notes:**
- `orderType` must be either `"delivery"` or `"pickup"`
- `paymentMethod` must be `"cash"`, `"card"`, or `"split"`
- If `orderType` is `"delivery"`, `deliveryAddress` is required
- `items` array must contain at least one item
- Each item must have `productId` and `quantity`
- `sizeId` is optional (for products with sizes)
- `toppings` is optional array of objects with `id`, `name`, and `price`
- Stock is automatically deducted if product tracks inventory

**Error Responses:**
```json
{
  "errors": [
    {
      "message": "Permission denied. Staff access required for POS."
    }
  ]
}
```

```json
{
  "errors": [
    {
      "message": "Order type must be 'delivery' or 'pickup'"
    }
  ]
}
```

```json
{
  "errors": [
    {
      "message": "Delivery address is required for delivery orders"
    }
  ]
}
```

```json
{
  "errors": [
    {
      "message": "Order must have at least one item"
    }
  ]
}
```

---

## Inventory Queries

### Get All Stock Items
```graphql
query GetAllStockItems {
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
    isLowStock
    isOutOfStock
    lastRestocked
  }
}
```

---

### Get Low Stock Items
```graphql
query GetLowStockItems {
  lowStockItems {
    id
    product {
      id
      name
      barcode
      sku
    }
    quantity
    reorderLevel
    isLowStock
  }
}
```

---

### Get Out of Stock Items
```graphql
query GetOutOfStockItems {
  outOfStockItems {
    id
    product {
      id
      name
      barcode
      sku
    }
    quantity
    isOutOfStock
  }
}
```

---

### Get Stock Item by Product
```graphql
query GetStockItemByProduct($productId: ID!) {
  stockItemByProduct(productId: $productId) {
    id
    quantity
    reorderLevel
    isLowStock
    isOutOfStock
  }
}
```

---

### Get Product by Barcode
```graphql
query GetProductByBarcode($barcode: String!) {
  productByBarcode(barcode: $barcode) {
    id
    name
    basePrice
    barcode
    sku
    trackInventory
  }
}
```

---

### Get Stock Movements by Product
```graphql
query GetStockMovements($productId: ID!) {
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

---

## Inventory Mutations

### Adjust Stock
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
    "quantityChange": 10,  // Positive for increase, negative for decrease
    "movementType": "ADJUSTMENT",
    "reference": "Manual adjustment",
    "notes": "Stock count correction"
  }
}
```

**Movement Types:**
- `ADJUSTMENT` - Manual adjustment
- `SALE` - Sale (auto-deducted on order)
- `RECEIPT` - Stock received
- `RETURN` - Stock returned
- `DAMAGE` - Damaged stock
- `LOSS` - Lost stock

---

### Receive Stock
Receive stock from supplier.

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
    "notes": "Received from supplier ABC"
  }
}
```

---

### Return Stock
Return stock (e.g., customer return).

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
    "quantity": 2,
    "reference": "ORD-2024-001",
    "notes": "Customer return"
  }
}
```

---

### Generate Barcode
Generate barcode for a product.

```graphql
mutation GenerateBarcode($productId: ID!) {
  generateBarcode(productId: $productId) {
    success
    message
    product {
      id
      name
      barcode
    }
  }
}
```

---

### Generate SKU
Generate SKU for a product.

```graphql
mutation GenerateSKU($productId: ID!) {
  generateSku(productId: $productId) {
    success
    message
    product {
      id
      name
      sku
    }
  }
}
```

---

## Frontend Integration Examples

### React/Apollo Client Example

```javascript
import { useQuery, useMutation } from '@apollo/client';
import { gql } from '@apollo/client';

// Query: Get POS Products
const GET_POS_PRODUCTS = gql`
  query GetPOSProducts($categoryId: ID, $search: String, $inStockOnly: Boolean) {
    posProducts(categoryId: $categoryId, search: $search, inStockOnly: $inStockOnly) {
      id
      name
      currentPrice
      barcode
      stockQuantity
      isInStock
      imageUrl
    }
  }
`;

// Query: Scan Barcode
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

// Mutation: Create POS Order
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

// Usage in component
function POSComponent() {
  const { data, loading, error } = useQuery(GET_POS_PRODUCTS, {
    variables: { inStockOnly: true }
  });
  
  const [createOrder] = useMutation(CREATE_POS_ORDER);
  
  const handleScanBarcode = async (barcode) => {
    const { data } = await client.query({
      query: SCAN_BARCODE,
      variables: { barcode }
    });
    // Add to cart
  };
  
  const handleCheckout = async (orderData) => {
    try {
      const { data } = await createOrder({
        variables: { input: orderData }
      });
      // Show success message
    } catch (error) {
      // Handle error
    }
  };
  
  // ... rest of component
}
```

---

## Authentication Requirements

**All POS queries and mutations require:**
- User must be authenticated (logged in)
- User must have `is_staff=True` or `is_superuser=True`
- Session-based authentication (include credentials in requests)

**GraphQL Client Configuration:**
```javascript
import { ApolloClient, InMemoryCache, createHttpLink } from '@apollo/client';
import { setContext } from '@apollo/client/link/context';

const httpLink = createHttpLink({
  uri: 'https://api.marinapizzas.com.au/graphql/',
  credentials: 'include'  // IMPORTANT: Include cookies for session auth
});

const client = new ApolloClient({
  link: httpLink,
  cache: new InMemoryCache()
});
```

---

## Error Handling

All queries and mutations may return GraphQL errors. Common errors:

1. **Permission Denied:**
   ```json
   {
     "errors": [{
       "message": "Permission denied. Staff access required for POS."
     }]
   }
   ```

2. **Product Not Found:**
   ```json
   {
     "errors": [{
       "message": "Product not found"
     }]
   }
   ```

3. **Validation Errors:**
   ```json
   {
     "errors": [{
       "message": "Order must have at least one item"
     }]
   }
   ```

Always check for errors in your frontend code:

```javascript
const { data, error } = useQuery(GET_POS_PRODUCTS);

if (error) {
  console.error('GraphQL Error:', error.message);
  // Show error to user
}
```

---

## Notes

- All prices are returned as strings (Decimal type in GraphQL)
- Dates are returned in ISO 8601 format
- Stock quantities are integers
- Barcodes are EAN-13 format (13 digits)
- SKUs are auto-generated in format: `CAT-PROD-###`
- Stock is automatically deducted when creating orders (if `trackInventory=true`)
- All timestamps are in UTC
