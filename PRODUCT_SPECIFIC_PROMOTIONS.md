# Product-Specific Promotions System

## Overview

The promotion system now supports **product-specific discounts**, allowing admins to create targeted promotions that apply only to selected products, toppings, or combo items. This provides much more flexibility and control over promotional campaigns.

---

## 🎯 **Key Features**

### 1. **Product Selection**
- Admins can select specific products that the promotion applies to
- If no products are selected, the promotion applies to all products (entire order)
- Supports selecting multiple products at once

### 2. **Granular Discount Control**
Admins can choose exactly what parts of a product get discounted:

- **Base Price** (`apply_to_base_price`): Apply discount to the product's base price
- **Toppings** (`apply_to_toppings`): Apply discount to toppings/add-ons
- **Included Items** (`apply_to_included_items`): Apply discount to combo items (e.g., chips, salad)

### 3. **Order Scope**
- **Entire Order** (`apply_to_entire_order = True`): Discount applies to the whole order (default)
- **Selected Products Only** (`apply_to_entire_order = False`): Discount only applies to selected products

---

## 📋 **Model Fields**

### New Fields in `Promotion` Model:

```python
applicable_products = ManyToManyField(Product, blank=True)
# Products this promotion applies to. Empty = all products

apply_to_base_price = BooleanField(default=True)
# Apply discount to product base price

apply_to_toppings = BooleanField(default=False)
# Apply discount to toppings/add-ons

apply_to_included_items = BooleanField(default=False)
# Apply discount to included items (e.g., chips, salad in combos)

apply_to_entire_order = BooleanField(default=True)
# If True, applies to entire order. If False, only selected products.
```

---

## 🔧 **How It Works**

### Discount Calculation Logic:

1. **Free Delivery**: Always applies to delivery fee (regardless of product selection)

2. **Entire Order Discount** (`apply_to_entire_order = True`):
   - Applies discount to the entire order subtotal
   - Product selection is ignored

3. **Product-Specific Discount** (`apply_to_entire_order = False`):
   - Only applies to selected products in the order
   - Calculates discount based on:
     - Base price (if `apply_to_base_price = True`)
     - Toppings (if `apply_to_toppings = True`)
     - Included items (if `apply_to_included_items = True`)

---

## 📝 **GraphQL API**

### **PromotionType** (Query Response)

```graphql
type PromotionType {
  id: ID!
  code: String!
  name: String!
  description: String
  discountType: String!
  discountValue: Decimal!
  minimumOrderAmount: Decimal
  maximumDiscount: Decimal
  usageLimit: Int
  timesUsed: Int!
  isActive: Boolean!
  validFrom: DateTime!
  validUntil: DateTime!
  
  # New fields
  applicableProducts: [ProductType!]!
  applyToBasePrice: Boolean!
  applyToToppings: Boolean!
  applyToIncludedItems: Boolean!
  applyToEntireOrder: Boolean!
  
  # Computed fields
  isValid: Boolean!
  discountDisplay: String!
}
```

### **PromotionInput** (Create/Update)

```graphql
input PromotionInput {
  code: String!                    # Required
  name: String!                    # Required
  description: String
  discountType: String!            # 'percentage' | 'fixed' | 'free_delivery'
  discountValue: Decimal!          # Required
  minimumOrderAmount: Decimal
  maximumDiscount: Decimal
  usageLimit: Int
  isActive: Boolean!               # Required
  validFrom: DateTime!            # Required
  validUntil: DateTime!           # Required
  
  # New fields
  applicableProductIds: [ID!]     # Product IDs (empty = all products)
  applyToBasePrice: Boolean       # Default: true
  applyToToppings: Boolean        # Default: false
  applyToIncludedItems: Boolean   # Default: false
  applyToEntireOrder: Boolean     # Default: true
}
```

---

## 💡 **Example Use Cases**

### Example 1: 20% Off All Pizzas

```graphql
mutation {
  createPromotion(input: {
    code: "PIZZA20"
    name: "20% Off All Pizzas"
    discountType: "percentage"
    discountValue: "20.00"
    applyToEntireOrder: false
    applicableProductIds: ["1", "2", "3"]  # Pizza product IDs
    applyToBasePrice: true
    applyToToppings: false
    isActive: true
    validFrom: "2024-01-01T00:00:00Z"
    validUntil: "2024-12-31T23:59:59Z"
  }) {
    promotion {
      id
      code
      name
    }
    success
  }
}
```

**Result**: Only pizza products get 20% discount on their base price. Toppings are not discounted.

---

### Example 2: Free Toppings on Chicken Pizzas

```graphql
mutation {
  createPromotion(input: {
    code: "FREETOPPINGS"
    name: "Free Toppings on Chicken Pizzas"
    discountType: "percentage"
    discountValue: "100.00"  # 100% = free
    applyToEntireOrder: false
    applicableProductIds: ["10", "11", "12"]  # Chicken pizza IDs
    applyToBasePrice: false
    applyToToppings: true    # Only toppings discounted
    applyToIncludedItems: false
    isActive: true
    validFrom: "2024-01-01T00:00:00Z"
    validUntil: "2024-12-31T23:59:59Z"
  }) {
    promotion {
      id
      code
    }
    success
  }
}
```

**Result**: Toppings are free on selected chicken pizzas. Base price is not discounted.

---

### Example 3: $5 Off Combo Meals (Including Sides)

```graphql
mutation {
  createPromotion(input: {
    code: "COMBO5"
    name: "$5 Off Combo Meals"
    discountType: "fixed"
    discountValue: "5.00"
    applyToEntireOrder: false
    applicableProductIds: ["20", "21", "22"]  # Combo product IDs
    applyToBasePrice: true
    applyToToppings: false
    applyToIncludedItems: true  # Discount includes chips, salad, etc.
    isActive: true
    validFrom: "2024-01-01T00:00:00Z"
    validUntil: "2024-12-31T23:59:59Z"
  }) {
    promotion {
      id
      code
    }
    success
  }
}
```

**Result**: $5 off the entire combo (base price + included items like chips and salad).

---

### Example 4: 15% Off Entire Order (Traditional)

```graphql
mutation {
  createPromotion(input: {
    code: "SAVE15"
    name: "15% Off Entire Order"
    discountType: "percentage"
    discountValue: "15.00"
    applyToEntireOrder: true  # Applies to everything
    # applicableProductIds not needed
    isActive: true
    validFrom: "2024-01-01T00:00:00Z"
    validUntil: "2024-12-31T23:59:59Z"
  }) {
    promotion {
      id
      code
    }
    success
  }
}
```

**Result**: 15% discount on the entire order, regardless of products.

---

## 🔍 **Query Examples**

### Get All Promotions with Product Details

```graphql
query {
  allPromotions {
    id
    code
    name
    discountDisplay
    applicableProducts {
      id
      name
      category {
        name
      }
    }
    applyToBasePrice
    applyToToppings
    applyToIncludedItems
    applyToEntireOrder
    isActive
    validFrom
    validUntil
  }
}
```

### Get Single Promotion

```graphql
query {
  promotion(id: "1") {
    id
    code
    name
    description
    discountType
    discountValue
    applicableProducts {
      id
      name
      basePrice
    }
    applyToBasePrice
    applyToToppings
    applyToIncludedItems
    applyToEntireOrder
    isActive
    validFrom
    validUntil
  }
}
```

---

## 🛠️ **Admin Interface**

The Django Admin interface has been updated to include:

1. **Product Selection Widget**: Multi-select widget to choose applicable products
2. **Checkboxes**: For `apply_to_base_price`, `apply_to_toppings`, `apply_to_included_items`, `apply_to_entire_order`
3. **Clear Organization**: Fields grouped in a "Product Selection" fieldset

### Admin Fieldsets:

- **Basic Info**: Code, name, description, active status
- **Discount Details**: Type, value, maximum discount
- **Product Selection**: Products, apply flags (NEW)
- **Conditions**: Minimum order amount
- **Usage Limits**: Usage limit, times used
- **Validity Period**: Valid from/until dates

---

## ⚙️ **Technical Details**

### Discount Calculation Flow:

1. **Order Creation**:
   - Order items are created first
   - Promotion code is validated
   - `calculate_discount()` is called with order items
   - Discount is calculated based on product selection and apply flags
   - Order is updated with discount amount

2. **Product-Specific Calculation**:
   ```python
   if order_items and not apply_to_entire_order:
       # Filter to applicable products
       # Calculate discount on:
       # - Base price (if apply_to_base_price)
       # - Toppings (if apply_to_toppings)
       # - Included items (if apply_to_included_items)
   else:
       # Apply to entire order
   ```

3. **Percentage Discounts**:
   - Applied to discountable amount
   - Respects `maximum_discount` if set

4. **Fixed Discounts**:
   - Applied up to the discountable amount
   - Cannot exceed the discountable total

---

## 📊 **Best Practices**

1. **Product Selection**:
   - Use product IDs from your product catalog
   - Leave empty for order-wide discounts
   - Group related products (e.g., all pizzas) for category discounts

2. **Apply Flags**:
   - `apply_to_base_price = True` for most promotions
   - `apply_to_toppings = True` for "free toppings" promotions
   - `apply_to_included_items = True` for combo discounts

3. **Testing**:
   - Test with single products first
   - Test with multiple products
   - Test with mixed orders (some products eligible, some not)
   - Verify discount amounts match expectations

4. **Performance**:
   - Product-specific discounts require order items to be created first
   - Consider caching applicable product IDs for frequently used promotions

---

## 🚀 **Migration Notes**

The system is backward compatible:
- Existing promotions default to `apply_to_entire_order = True`
- Existing promotions have empty `applicable_products` (apply to all)
- All existing promotions continue to work as before

---

## ✅ **Summary**

The product-specific promotion system provides:

✅ **Flexibility**: Target specific products or entire orders  
✅ **Granularity**: Control what parts of products get discounted  
✅ **Professional**: Enterprise-level promotion management  
✅ **Scalable**: Works with any number of products  
✅ **Backward Compatible**: Existing promotions still work  

This makes the promotion system much more powerful and suitable for professional pizza store operations! 🍕🎉

