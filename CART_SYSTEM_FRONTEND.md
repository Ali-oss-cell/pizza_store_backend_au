# 🛒 Cart System - Frontend Integration Guide

## Overview

The cart system is **session-based** (no login required). Each user session has its own cart that persists across page refreshes. The cart properly stores and distinguishes between:
- ✅ **Product** (required)
- ✅ **Size** (optional, stored as ForeignKey)
- ✅ **Toppings** (optional, stored as JSON with id, name, price)
- ✅ **Quantity** (default: 1)

**Important:** Items with the same product but different sizes or toppings are treated as **separate cart items**. If you add the exact same product with the same size and toppings again, the quantity will be merged.

---

## 📋 GraphQL Queries

### Get Cart

```graphql
query GetCart {
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
        currentPrice
        isOnSale
        imageUrl
        slug
      }
      size {
        id
        name
        priceModifier
        category {
          id
          name
        }
      }
      quantity
      unitPrice
      unitPriceWithToppings
      subtotal
      selectedToppings  # JSON string (backward compatibility)
      toppings {        # Structured list (recommended)
        id
        name
        price
      }
      createdAt
    }
  }
}
```

**Response Example:**
```json
{
  "data": {
    "cart": {
      "id": "1",
      "total": "45.50",
      "itemCount": 2,
      "items": [
        {
          "id": "1",
          "product": {
            "id": "5",
            "name": "Margherita Pizza",
            "basePrice": "12.99",
            "currentPrice": "10.99",
            "isOnSale": true,
            "imageUrl": "/media/products/...",
            "slug": "margherita-pizza"
          },
          "size": {
            "id": "2",
            "name": "Large",
            "priceModifier": "3.00",
            "category": {
              "id": "1",
              "name": "Pizza"
            }
          },
          "quantity": 2,
          "unitPrice": "13.99",
          "unitPriceWithToppings": "16.99",
          "subtotal": "33.98",
          "selectedToppings": "[{\"id\":\"1\",\"name\":\"Extra Cheese\",\"price\":\"2.00\"},{\"id\":\"3\",\"name\":\"Mushrooms\",\"price\":\"1.00\"}]",
          "toppings": [
            {
              "id": "1",
              "name": "Extra Cheese",
              "price": "2.00"
            },
            {
              "id": "3",
              "name": "Mushrooms",
              "price": "1.00"
            }
          ],
          "createdAt": "2024-01-15T10:30:00Z"
        }
      ]
    }
  }
}
```

---

## 🔧 GraphQL Mutations

### Add to Cart

```graphql
mutation AddToCart($input: AddToCartInput!) {
  addToCart(input: $input) {
    cartItem {
      id
      product {
        id
        name
      }
      size {
        id
        name
      }
      quantity
      toppings {
        id
        name
        price
      }
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
```

**Variables:**
```json
{
  "input": {
    "productId": "5",
    "quantity": 2,
    "sizeId": "2",
    "toppingIds": ["1", "3"]
  }
}
```

**Notes:**
- If the exact same product with same size and toppings already exists, **quantity is merged** (not a new item)
- `sizeId` is optional (can be `null` for products without sizes)
- `toppingIds` is optional (can be `[]` or omitted)
- `quantity` defaults to 1 if not provided

**Response:**
```json
{
  "data": {
    "addToCart": {
      "cartItem": {
        "id": "1",
        "product": { "id": "5", "name": "Margherita Pizza" },
        "size": { "id": "2", "name": "Large" },
        "quantity": 2,
        "toppings": [
          { "id": "1", "name": "Extra Cheese", "price": "2.00" },
          { "id": "3", "name": "Mushrooms", "price": "1.00" }
        ],
        "subtotal": "33.98"
      },
      "cart": {
        "total": "33.98",
        "itemCount": 1
      },
      "success": true,
      "message": "Item added to cart successfully"
    }
  }
}
```

**If item already exists:**
```json
{
  "message": "Quantity updated. Total quantity: 3"
}
```

---

### Update Cart Item

```graphql
mutation UpdateCartItem($input: UpdateCartItemInput!) {
  updateCartItem(input: $input) {
    cartItem {
      id
      quantity
      size {
        id
        name
      }
      toppings {
        id
        name
        price
      }
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
```

**Variables:**
```json
{
  "input": {
    "itemId": "1",
    "quantity": 3,
    "sizeId": "3",
    "toppingIds": ["1", "2"]
  }
}
```

**Notes:**
- All fields in `input` are optional except `itemId`
- If `quantity` is provided, it replaces the current quantity (must be > 0)
- If `sizeId` is provided, it updates the size (can be `null` to remove size)
- If `toppingIds` is provided, it replaces all toppings (can be `[]` to remove all)
- Price is automatically recalculated when size or toppings change

---

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

**Variables:**
```json
{
  "itemId": "1"
}
```

---

### Clear Cart

```graphql
mutation ClearCart {
  clearCart {
    success
    message
  }
}
```

---

## 💰 Price Calculation

### How Prices Work

1. **Base Price**: Product's `currentPrice` (sale price if on sale, otherwise `basePrice`)
2. **Size Modifier**: Added if size is selected (`size.priceModifier`)
3. **Toppings**: Each topping's price is added
4. **Unit Price**: `basePrice + sizeModifier` (stored in `unitPrice` field)
5. **Unit Price with Toppings**: `unitPrice + sum(toppingPrices)` (calculated field)
6. **Subtotal**: `(unitPrice + sum(toppingPrices)) * quantity`

### Example Calculation

```
Product: Margherita Pizza
- Base Price: $12.99
- Sale Price: $10.99 (currently on sale)
- Size: Large (+$3.00)
- Toppings: Extra Cheese (+$2.00), Mushrooms (+$1.00)
- Quantity: 2

Unit Price = $10.99 + $3.00 = $13.99
Unit Price with Toppings = $13.99 + $2.00 + $1.00 = $16.99
Subtotal = $16.99 × 2 = $33.98
```

---

## 🔍 Item Matching Logic

The cart uses **intelligent matching** to determine if items are the same:

1. **Product** must match (same product ID)
2. **Size** must match (both null or same size ID)
3. **Toppings** must match (same topping IDs, order doesn't matter)

**Examples:**

| Product | Size | Toppings | Result |
|---------|------|----------|--------|
| Pizza A | Large | [Cheese] | ✅ Same item (quantity merged) |
| Pizza A | Large | [Cheese] | |
| Pizza A | Medium | [Cheese] | ❌ Different item (different size) |
| Pizza A | Large | [Cheese] | |
| Pizza A | Large | [Mushrooms] | ❌ Different item (different toppings) |
| Pizza A | Large | [Cheese] | |
| Pizza B | Large | [Cheese] | ❌ Different item (different product) |
| Pizza A | Large | [Cheese] | |

---

## 📊 Field Reference

### CartItemType Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | ID | Cart item ID |
| `product` | ProductType | Product object |
| `size` | SizeType | Size object (null if no size) |
| `quantity` | Int | Quantity |
| `unitPrice` | Decimal | Base unit price (product + size, excluding toppings) |
| `unitPriceWithToppings` | Decimal | Unit price including toppings |
| `subtotal` | Decimal | Total for this item (unitPriceWithToppings × quantity) |
| `selectedToppings` | JSONString | Toppings as JSON (backward compatibility) |
| `toppings` | [ToppingSelectionType] | Toppings as structured list (recommended) |
| `createdAt` | DateTime | When item was added |

### ToppingSelectionType Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | ID | Topping ID |
| `name` | String | Topping name |
| `price` | Decimal | Topping price |

### CartType Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | ID | Cart ID |
| `items` | [CartItemType] | All cart items |
| `total` | Decimal | Total cart price |
| `itemCount` | Int | Total number of items |

---

## ⚠️ Important Notes

### 1. Session-Based Cart
- Cart is tied to browser session
- No login required
- Cart persists across page refreshes
- Each browser/tab has its own cart

### 2. Size and Toppings Storage
- ✅ **Size is stored** as ForeignKey (not lost)
- ✅ **Toppings are stored** as JSON with id, name, price
- ✅ Both are returned in GraphQL queries
- ✅ Use `toppings` field (structured) instead of `selectedToppings` (JSON string)

### 3. Item Uniqueness
- Items are unique by: Product + Size + Toppings
- Same product with different size = different item
- Same product with different toppings = different item
- Same product, size, and toppings = quantity merged

### 4. Price Updates
- `unitPrice` is a snapshot (price at time of adding to cart)
- If product goes on sale after adding, cart item price doesn't change
- To update price, remove and re-add item

### 5. Error Handling

**Product not found:**
```json
{
  "errors": [{
    "message": "Product not found"
  }]
}
```

**Product not available:**
```json
{
  "errors": [{
    "message": "Product is not available"
  }]
}
```

**Size not available for product:**
```json
{
  "errors": [{
    "message": "Size 'Large' is not available for this product"
  }]
}
```

**Topping not available for product:**
```json
{
  "errors": [{
    "message": "Topping 'Extra Cheese' is not available for this product"
  }]
}
```

**Cart not found:**
```json
{
  "errors": [{
    "message": "Cart not found"
  }]
}
```

---

## 🎯 Frontend Implementation Tips

### 1. Displaying Cart Items

```typescript
// Recommended: Use structured toppings field
cart.items.map(item => ({
  id: item.id,
  product: item.product.name,
  size: item.size?.name || null,
  toppings: item.toppings.map(t => t.name).join(', '),
  quantity: item.quantity,
  price: item.unitPriceWithToppings,
  subtotal: item.subtotal
}))
```

### 2. Adding to Cart

```typescript
// Make sure to include sizeId and toppingIds
const addToCart = async (productId, sizeId, toppingIds, quantity = 1) => {
  const result = await addToCartMutation({
    variables: {
      input: {
        productId,
        sizeId: sizeId || null,  // Can be null
        toppingIds: toppingIds || [],  // Can be empty array
        quantity
      }
    }
  });
  
  // Check if quantity was merged
  if (result.data.addToCart.message.includes("Quantity updated")) {
    // Show toast: "Item quantity updated"
  } else {
    // Show toast: "Item added to cart"
  }
};
```

### 3. Updating Cart Item

```typescript
// Update only what changed
const updateCartItem = async (itemId, updates) => {
  const input: any = { itemId };
  
  if (updates.quantity !== undefined) input.quantity = updates.quantity;
  if (updates.sizeId !== undefined) input.sizeId = updates.sizeId;
  if (updates.toppingIds !== undefined) input.toppingIds = updates.toppingIds;
  
  await updateCartItemMutation({ variables: { input } });
};
```

### 4. Checking if Item Exists

The backend automatically handles this, but if you want to check client-side:

```typescript
const findMatchingItem = (cart, productId, sizeId, toppingIds) => {
  return cart.items.find(item => {
    // Check product
    if (item.product.id !== productId) return false;
    
    // Check size
    const itemSizeId = item.size?.id || null;
    if (itemSizeId !== (sizeId || null)) return false;
    
    // Check toppings (sort IDs for comparison)
    const itemToppingIds = item.toppings.map(t => t.id).sort();
    const newToppingIds = (toppingIds || []).sort();
    if (JSON.stringify(itemToppingIds) !== JSON.stringify(newToppingIds)) {
      return false;
    }
    
    return true;
  });
};
```

---

## ✅ Testing Checklist

- [ ] Add product without size/toppings
- [ ] Add product with size only
- [ ] Add product with toppings only
- [ ] Add product with size and toppings
- [ ] Add same product again (quantity should merge)
- [ ] Add same product with different size (should be separate item)
- [ ] Add same product with different toppings (should be separate item)
- [ ] Update cart item quantity
- [ ] Update cart item size
- [ ] Update cart item toppings
- [ ] Remove cart item
- [ ] Clear cart
- [ ] Verify prices are calculated correctly
- [ ] Verify subtotals are correct
- [ ] Verify cart total is correct

---

## 🔗 Related Documentation

- [Product Queries](./PRODUCT_QUERIES.md) - How to fetch products with sizes and toppings
- [Product Mutations](./PRODUCT_MUTATIONS.md) - Admin product management
- [Sale Pricing System](./SALE_PRICING_SYSTEM.md) - How sale prices work
- [Price Handling](./PRICE_HANDLING.md) - Price calculation details

---

**Last Updated:** 2024-01-15  
**Backend Version:** 1.0.0

