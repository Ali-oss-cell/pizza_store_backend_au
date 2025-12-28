# 🎟️ Promotion System Documentation

## 📋 **Overview**

The promotion system allows admins to create discount codes that customers can use during checkout. Promotions support multiple discount types, usage limits, validity periods, and minimum order amounts.

---

## 🏗️ **Promotion Model Structure**

### Basic Information
- **code**: Unique discount code (e.g., "SAVE10", "FREEDEL")
- **name**: Promotion name (e.g., "10% Off Weekend Special")
- **description**: Optional description

### Discount Details
- **discount_type**: Type of discount (percentage, fixed, free_delivery)
- **discount_value**: Discount amount or percentage
- **maximum_discount**: Maximum discount cap (for percentage discounts)

### Conditions
- **minimum_order_amount**: Minimum order amount required
- **usage_limit**: Total number of times code can be used (optional)
- **times_used**: Counter for how many times code has been used

### Validity
- **is_active**: Enable/disable promotion
- **valid_from**: Start date/time
- **valid_until**: End date/time

---

## 💰 **Discount Types**

### 1. Percentage Discount
- **Type:** `percentage`
- **How it works:** Discount is calculated as percentage of order subtotal
- **Example:** 10% off = `discount_value: 10`
- **Calculation:** `discount = subtotal × (discount_value / 100)`
- **Maximum cap:** Can set `maximum_discount` to limit the discount amount

**Example:**
- Order subtotal: $50.00
- Discount: 10%
- Discount amount: $5.00
- Final: $45.00

**With Maximum Cap:**
- Order subtotal: $100.00
- Discount: 20%
- Discount amount: $20.00
- Maximum discount: $15.00
- **Final discount:** $15.00 (capped)

### 2. Fixed Amount Discount
- **Type:** `fixed`
- **How it works:** Fixed dollar amount off the order
- **Example:** $5 off = `discount_value: 5.00`
- **Calculation:** `discount = min(discount_value, subtotal)`
- **Note:** Cannot exceed order subtotal

**Example:**
- Order subtotal: $30.00
- Discount: $5.00 off
- Final: $25.00

**Edge Case:**
- Order subtotal: $3.00
- Discount: $5.00 off
- **Final discount:** $3.00 (cannot exceed subtotal)

### 3. Free Delivery
- **Type:** `free_delivery`
- **How it works:** Removes delivery fee from order
- **Example:** Free delivery = `discount_value: 0` (not used)
- **Calculation:** `discount = delivery_fee`
- **Note:** Only applies to delivery orders

**Example:**
- Order subtotal: $25.00
- Delivery fee: $5.00
- Discount: Free delivery
- Discount amount: $5.00
- Final: $25.00

---

## ✅ **Promotion Validation**

### Validation Checks (in order)

1. **Code Exists**
   - Promotion with code must exist in database
   - Case-insensitive matching

2. **Is Active**
   - `is_active` must be `True`

3. **Date Validity**
   - Current time must be between `valid_from` and `valid_until`
   - Cannot use before start date
   - Cannot use after end date

4. **Usage Limit**
   - If `usage_limit` is set, `times_used` must be less than limit
   - Prevents overuse of limited promotions

5. **Minimum Order Amount**
   - If `minimum_order_amount` is set, order subtotal must meet or exceed it
   - Example: "$50 minimum" means order must be at least $50

### Validation Flow

```
Customer enters code
    ↓
Check if code exists
    ↓
Check if is_active = True
    ↓
Check if current time is within valid_from and valid_until
    ↓
Check if times_used < usage_limit (if limit exists)
    ↓
Check if subtotal >= minimum_order_amount (if required)
    ↓
Calculate discount amount
    ↓
Return discount to customer
```

---

## 🧮 **Discount Calculation**

### Location: `team/models.py::Promotion.calculate_discount()`

### Calculation Logic

```python
def calculate_discount(self, order_subtotal, delivery_fee=Decimal('0.00')):
    # 1. Check if promotion is valid
    if not self.is_valid:
        return Decimal('0.00')
    
    # 2. Check minimum order amount
    if self.minimum_order_amount and order_subtotal < self.minimum_order_amount:
        return Decimal('0.00')
    
    # 3. Calculate based on discount type
    if self.discount_type == 'percentage':
        discount = order_subtotal * (self.discount_value / 100)
        if self.maximum_discount:
            discount = min(discount, self.maximum_discount)
        return discount
    
    elif self.discount_type == 'fixed':
        return min(self.discount_value, order_subtotal)
    
    elif self.discount_type == 'free_delivery':
        return delivery_fee
    
    return Decimal('0.00')
```

---

## 🛒 **How Promotions Work in Checkout**

### Step 1: Customer Enters Code (Optional)
- Customer can enter promotion code during checkout
- Code is sent in `createOrder` mutation as `promotionCode`

### Step 2: Validate Code (Before Order Creation)
- Backend validates the code using `validate_promotion` query (optional)
- Or validates during order creation

### Step 3: Apply Discount (During Order Creation)
- When `createOrder` is called with `promotion_code`:
  1. Look up promotion by code
  2. Validate promotion is active and valid
  3. Check minimum order amount
  4. Calculate discount amount
  5. Increment `times_used` counter
  6. Apply discount to order total

### Step 4: Calculate Final Total
```
subtotal = cart.get_total()
deliveryFee = (if delivery) ? deliveryFee : 0
discountAmount = (if promotion) ? calculate_discount() : 0
total = subtotal + deliveryFee - discountAmount
```

### Step 5: Store in Order
- `discount_amount`: Calculated discount amount
- `discount_code`: Promotion code used
- Both stored in Order model for historical record

---

## 📊 **Order Total Calculation with Promotion**

### Example 1: Percentage Discount
```
Cart Subtotal: $50.00
Delivery Fee: $5.00
Promotion: 10% off
Discount: $50.00 × 10% = $5.00
Final Total: $50.00 + $5.00 - $5.00 = $50.00
```

### Example 2: Fixed Amount
```
Cart Subtotal: $30.00
Delivery Fee: $5.00
Promotion: $5.00 off
Discount: $5.00
Final Total: $30.00 + $5.00 - $5.00 = $30.00
```

### Example 3: Free Delivery
```
Cart Subtotal: $25.00
Delivery Fee: $5.00
Promotion: Free delivery
Discount: $5.00 (delivery fee)
Final Total: $25.00 + $5.00 - $5.00 = $25.00
```

### Example 4: With Minimum Order
```
Cart Subtotal: $40.00
Minimum Required: $50.00
Promotion: 10% off
Result: ❌ Invalid - order too small
```

---

## 🔍 **GraphQL Operations**

### Validate Promotion (Public)
```graphql
query ValidatePromotion($code: String!, $subtotal: Decimal!, $deliveryFee: Decimal) {
  validatePromotion(code: $code, subtotal: $subtotal, deliveryFee: $deliveryFee) {
    valid
    promotion {
      id
      code
      name
      discountType
      discountValue
    }
    discountAmount
    message
  }
}

# Variables:
{
  "code": "SAVE10",
  "subtotal": "50.00",
  "deliveryFee": "5.00"
}
```

### Create Order with Promotion
```graphql
mutation CreateOrder($input: CreateOrderInput!) {
  createOrder(input: $input) {
    order {
      id
      orderNumber
      subtotal
      deliveryFee
      discountCode
      discountAmount
      total
    }
    success
    message
  }
}

# Variables:
{
  "input": {
    "customerName": "John Doe",
    "customerEmail": "john@example.com",
    "customerPhone": "+1234567890",
    "orderType": "delivery",
    "deliveryAddress": "123 Main St",
    "deliveryFee": "5.00",
    "promotionCode": "SAVE10"
  }
}
```

### Create Promotion (Admin Only)
```graphql
mutation CreatePromotion($input: PromotionInput!) {
  createPromotion(input: $input) {
    promotion {
      id
      code
      name
      discountType
    }
    success
    message
  }
}

# Variables:
{
  "input": {
    "code": "SAVE10",
    "name": "10% Off Weekend Special",
    "description": "Get 10% off your order",
    "discountType": "percentage",
    "discountValue": "10.00",
    "maximumDiscount": "15.00",
    "minimumOrderAmount": "30.00",
    "usageLimit": 100,
    "isActive": true,
    "validFrom": "2025-01-01T00:00:00Z",
    "validUntil": "2025-12-31T23:59:59Z"
  }
}
```

---

## 📝 **Promotion Fields Reference**

### Required Fields
- `code`: String (unique discount code)
- `name`: String (promotion name)
- `discount_type`: String (`percentage`, `fixed`, `free_delivery`)
- `discount_value`: Decimal (percentage or amount)
- `valid_from`: DateTime (start date)
- `valid_until`: DateTime (end date)

### Optional Fields
- `description`: String
- `minimum_order_amount`: Decimal
- `maximum_discount`: Decimal (for percentage discounts)
- `usage_limit`: Integer
- `is_active`: Boolean (default: true)

### Auto-Managed Fields
- `times_used`: Integer (auto-incremented on use)
- `created_at`: DateTime
- `updated_at`: DateTime

---

## 🔄 **Usage Tracking**

### Automatic Tracking
- When promotion is used in `createOrder`:
  1. `times_used` is incremented by 1
  2. Promotion is saved to database
  3. Code cannot be used again if `times_used >= usage_limit`

### Example
```
Promotion: "SAVE10"
Usage Limit: 50
Times Used: 0

After 50 orders use the code:
Times Used: 50
Status: ❌ Cannot be used anymore (reached limit)
```

---

## ⚠️ **Important Notes**

### 1. Code Uniqueness
- Promotion codes must be unique
- Codes are automatically converted to uppercase
- Case-insensitive matching when validating

### 2. Discount Calculation
- Percentage discounts are calculated on **subtotal only** (not including delivery)
- Free delivery discounts apply to **delivery fee only**
- Fixed discounts apply to **subtotal only** (cannot exceed subtotal)

### 3. Order of Operations
```
1. Calculate cart subtotal
2. Add delivery fee (if delivery)
3. Apply promotion discount
4. Calculate final total
```

### 4. Historical Record
- Discount code and amount are stored in Order
- Even if promotion is deleted later, order history is preserved
- `discount_code` and `discount_amount` are snapshots

### 5. Validation Timing
- Code is validated **before** order is created
- If validation fails, order creation fails with error
- Customer must fix issue before completing order

---

## 🎯 **Use Cases**

### Use Case 1: Weekend Special
- **Code:** "WEEKEND20"
- **Type:** Percentage (20% off)
- **Minimum:** $25.00
- **Valid:** Friday 5pm - Sunday 11pm
- **Limit:** 200 uses

### Use Case 2: First Order Discount
- **Code:** "FIRST5"
- **Type:** Fixed ($5 off)
- **Minimum:** $15.00
- **Valid:** Always active
- **Limit:** 1 use per customer (handled by frontend)

### Use Case 3: Free Delivery Promotion
- **Code:** "FREEDEL"
- **Type:** Free delivery
- **Minimum:** $30.00
- **Valid:** All week
- **Limit:** Unlimited

### Use Case 4: Limited Time Offer
- **Code:** "FLASH50"
- **Type:** Percentage (50% off, max $20)
- **Minimum:** $40.00
- **Valid:** Today only (24 hours)
- **Limit:** 50 uses

---

## ✅ **Current Implementation Status**

### ✅ Fully Implemented
- Promotion model with all fields
- Three discount types (percentage, fixed, free_delivery)
- Validation system
- Discount calculation
- Usage tracking
- Order integration
- GraphQL queries and mutations
- Admin interface

### ✅ Working Features
- Create/Update/Delete promotions (Admin)
- Validate promotion codes (Public)
- Apply promotions during checkout
- Track usage automatically
- Store discount in orders
- Support all discount types
- Enforce minimum order amounts
- Enforce usage limits
- Date-based validity

---

## 📋 **Summary**

**Promotions are fully functional and ready to use!**

The system supports:
- ✅ Multiple discount types
- ✅ Flexible conditions
- ✅ Usage limits
- ✅ Date-based validity
- ✅ Automatic tracking
- ✅ Order integration

**No changes needed - promotions work correctly!**

