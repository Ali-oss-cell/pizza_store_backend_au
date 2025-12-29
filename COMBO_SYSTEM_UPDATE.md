# 🍕 Combo System Update - Frontend Integration Guide

## Overview

The combo system has been updated to allow products to be sold **both as regular items AND as combos**. Customers can now choose whether to include combo items (chips, salad, drink, etc.) when adding a product to their cart.

---

## ✨ What Changed

### Key Feature
- **Same product can be regular OR combo**: A pizza product can be sold as:
  - **Regular**: Just the pizza (no combo items)
  - **Combo**: Pizza + included items (chips, salad, drink, etc.)

### Previous Behavior
- `isCombo` was a boolean flag - product was either always a combo or never a combo
- Included items were always included if product had `isCombo: true`

### New Behavior
- `isCombo` indicates the product **can** be sold as a combo (capability flag)
- Customer chooses whether to include combo items when adding to cart
- Same product with different combo choices = different cart items

---

## 📋 GraphQL Schema Updates

### New Fields in `AddToCartInput`

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `includeComboItems` | Boolean | No | `false` | If `true` and product is a combo, includes combo items |

### New Fields in `UpdateCartItemInput`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `includeComboItems` | Boolean | No | Update combo option for this cart item |

### New Fields in `CartItemType` Response

| Field | Type | Description |
|-------|------|-------------|
| `includeComboItems` | Boolean | Whether combo items are included in this cart item |
| `isComboOrder` | Boolean | Whether this is a combo order (product is combo AND combo items selected) |
| `includedItems` | `[IncludedItemSelectionType]` | List of included items for this combo order |
| `comboAvailable` | Boolean | Whether this product can be ordered as a combo |

### New Type: `IncludedItemSelectionType`

| Field | Type | Description |
|-------|------|-------------|
| `id` | ID | Included item ID |
| `name` | String | Included item name (e.g., "Chips", "Salad", "Drink") |

---

## 🔧 Updated Queries

### Get Cart (Updated)

The cart query now returns combo information:

**New Fields Available:**
- `items.includeComboItems` - Boolean
- `items.isComboOrder` - Boolean
- `items.includedItems` - Array of included items
- `items.comboAvailable` - Boolean

**Example Response:**
```json
{
  "cart": {
    "items": [
      {
        "id": "1",
        "product": {
          "id": "5",
          "name": "Margherita Pizza",
          "isCombo": true
        },
        "includeComboItems": true,
        "isComboOrder": true,
        "comboAvailable": true,
        "includedItems": [
          { "id": "1", "name": "Chips" },
          { "id": "2", "name": "Salad" },
          { "id": "3", "name": "Drink" }
        ]
      },
      {
        "id": "2",
        "product": {
          "id": "5",
          "name": "Margherita Pizza",
          "isCombo": true
        },
        "includeComboItems": false,
        "isComboOrder": false,
        "comboAvailable": true,
        "includedItems": []
      }
    ]
  }
}
```

**Note:** The same product (ID: 5) appears twice - once as combo, once as regular. They are treated as separate cart items.

---

## 🔄 Updated Mutations

### Add to Cart

**New Input Field:**
- `includeComboItems` (Boolean, optional, default: `false`)

**Behavior:**
- If `includeComboItems: true` AND product has `isCombo: true` → Combo order (includes combo items)
- If `includeComboItems: false` OR product has `isCombo: false` → Regular order (no combo items)
- If `includeComboItems: true` but product is not a combo → Silently ignored (treated as regular)

**Item Matching:**
- Items are matched by: Product + Size + Toppings + **Combo Option**
- Same product with different combo choices = different cart items (quantities don't merge)

**Response:**
- `cartItem.includeComboItems` - Shows if combo items are included
- `cartItem.isComboOrder` - Shows if this is a combo order
- `cartItem.includedItems` - List of included items (if combo)
- `message` - May include "as combo" text if combo option selected

### Update Cart Item

**New Input Field:**
- `includeComboItems` (Boolean, optional)

**Behavior:**
- Can toggle combo option on/off
- If setting to `true` and product is a combo → Includes combo items
- If setting to `false` → Removes combo items
- Price is recalculated if needed

---

## 💡 How It Works

### Product Configuration

1. **Product with `isCombo: true`**:
   - Can be sold as regular OR combo
   - Has `includedItems` (chips, salad, drink, etc.)
   - Customer chooses at cart time

2. **Product with `isCombo: false`**:
   - Always sold as regular
   - No combo option available
   - `includeComboItems` is ignored if sent

### Cart Item Matching

Items are considered the same (quantities merge) if:
- ✅ Same product
- ✅ Same size
- ✅ Same toppings
- ✅ **Same combo option** (`includeComboItems`)

Items are different (separate cart items) if:
- ❌ Different product
- ❌ Different size
- ❌ Different toppings
- ❌ **Different combo option**

### Example Scenarios

**Scenario 1: Same Pizza, Different Options**
- Add "Margherita Pizza" with `includeComboItems: false` → Regular pizza
- Add "Margherita Pizza" with `includeComboItems: true` → Combo pizza
- Result: **2 separate cart items** (different combo options)

**Scenario 2: Same Pizza, Same Options**
- Add "Margherita Pizza" with `includeComboItems: true` (quantity: 1)
- Add "Margherita Pizza" with `includeComboItems: true` (quantity: 1)
- Result: **1 cart item** with quantity: 2 (same combo option)

**Scenario 3: Non-Combo Product**
- Add "Regular Pizza" (not a combo) with `includeComboItems: true`
- Result: Treated as regular (combo option ignored)

---

## 📊 Display Recommendations

### Product Detail Page

**For Combo Products (`isCombo: true`):**
- Show toggle/checkbox: "Include Combo Items"
- Display included items list when combo option is selected
- Show price difference (if combo costs more) or "Free" if included items are free
- Example: "✓ Include Combo: Chips + Salad + Drink (Free)"

**For Regular Products (`isCombo: false`):**
- Don't show combo option
- Display normally

### Cart Display

**Show Combo Status:**
- Display badge/indicator if `isComboOrder: true`
- Show included items list for combo orders
- Example: "Margherita Pizza (Combo) - Includes: Chips, Salad, Drink"

**Cart Item List:**
- Show `includeComboItems` status
- Display `includedItems` when combo is selected
- Differentiate between regular and combo versions of same product

### Menu Display

**Combo Products:**
- Show both options available:
  - Regular price (pizza only)
  - Combo price (pizza + items)
- Or show toggle on product card
- Display included items in combo description

---

## ⚠️ Important Notes

### 1. Backward Compatibility
- Existing cart items without `includeComboItems` will default to `false`
- Old cart items will work normally (treated as regular)

### 2. Price Calculation
- Base price is the same for regular and combo
- Combo items are typically included in base price (no extra charge)
- If combo items have prices, they should be factored into `basePrice`

### 3. Order Processing
- Order items will include `isCombo` and `includedItems` snapshot
- This preserves what customer ordered even if product changes later

### 4. Validation
- If `includeComboItems: true` but product is not a combo → Silently ignored
- No error thrown, just treated as regular order

### 5. Admin Panel
- Admin can see combo status in cart items
- Shows which items are combo orders vs regular orders
- Displays included items for combo orders

---

## 🔍 Field Reference

### CartItemType - Complete Field List

| Field | Type | Description |
|-------|------|-------------|
| `id` | ID | Cart item ID |
| `product` | ProductType | Product object |
| `size` | SizeType | Size object (null if no size) |
| `quantity` | Int | Quantity |
| `unitPrice` | Decimal | Base unit price |
| `unitPriceWithToppings` | Decimal | Unit price including toppings |
| `subtotal` | Decimal | Total for this item |
| `selectedToppings` | JSONString | Toppings as JSON (backward compatibility) |
| `toppings` | [ToppingSelectionType] | Toppings as structured list |
| **`includeComboItems`** | **Boolean** | **Whether combo items are included** |
| **`isComboOrder`** | **Boolean** | **Whether this is a combo order** |
| **`includedItems`** | **[IncludedItemSelectionType]** | **Included items for combo** |
| **`comboAvailable`** | **Boolean** | **Whether product can be ordered as combo** |
| `createdAt` | DateTime | When item was added |

### ProductType - Combo Fields

| Field | Type | Description |
|-------|------|-------------|
| `isCombo` | Boolean | Whether product can be sold as combo |
| `includedItems` | [IncludedItemType] | Available combo items |

---

## 📝 Usage Examples

### Adding Regular Pizza (No Combo)

**Input:**
```json
{
  "productId": "5",
  "quantity": 1,
  "sizeId": "2",
  "includeComboItems": false
}
```

**Result:** Regular pizza, no combo items

---

### Adding Combo Pizza

**Input:**
```json
{
  "productId": "5",
  "quantity": 1,
  "sizeId": "2",
  "includeComboItems": true
}
```

**Result:** Combo pizza with included items (chips, salad, drink)

---

### Updating Cart Item to Combo

**Input:**
```json
{
  "itemId": "1",
  "includeComboItems": true
}
```

**Result:** Cart item updated to include combo items

---

### Updating Cart Item to Regular

**Input:**
```json
{
  "itemId": "1",
  "includeComboItems": false
}
```

**Result:** Cart item updated to remove combo items

---

## ✅ Testing Checklist

- [ ] Add product as regular (no combo)
- [ ] Add same product as combo (with combo items)
- [ ] Verify they appear as separate cart items
- [ ] Add same product with same combo option twice (should merge quantities)
- [ ] Update cart item to toggle combo option
- [ ] Verify included items display correctly
- [ ] Test with non-combo product (combo option should be ignored)
- [ ] Verify cart total calculation
- [ ] Check order creation includes combo info
- [ ] Verify admin panel shows combo status

---

## 🔗 Related Documentation

- [Cart System](./CART_SYSTEM_FRONTEND.md) - Complete cart system guide
- [Product Queries](./PRODUCT_QUERIES.md) - Product queries and structure
- [Price Handling](./PRICE_HANDLING.md) - Price calculation details

---

## 📅 Summary of Changes

**Backend Changes:**
1. ✅ Added `include_combo_items` field to `CartItem` model
2. ✅ Added `selected_included_items` snapshot field
3. ✅ Updated `AddToCartInput` with `includeComboItems`
4. ✅ Updated `UpdateCartItemInput` with `includeComboItems`
5. ✅ Enhanced `CartItemType` with combo-related fields
6. ✅ Updated cart matching logic to consider combo option
7. ✅ Updated admin panel to show combo status
8. ✅ Created migration and applied

**Frontend Updates Needed:**
1. Update product detail page to show combo toggle
2. Update cart display to show combo status and included items
3. Update add to cart mutation to include `includeComboItems`
4. Update update cart item mutation to handle combo toggle
5. Update cart query to fetch new combo fields

---

**Last Updated:** 2024-01-15  
**Backend Version:** 1.1.0  
**Migration:** `cart.0002_add_combo_items_to_cart`

