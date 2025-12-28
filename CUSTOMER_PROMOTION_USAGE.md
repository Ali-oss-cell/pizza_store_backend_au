# How Customers Use Promotion Codes

## Overview

Customers can use promotion codes during checkout to get discounts on their orders. The system provides two ways to use codes:

1. **Validate Code** (Optional): Check if a code is valid and see the discount amount before checkout
2. **Apply Code at Checkout**: Enter the code when creating an order

---

## 🛒 **Customer Flow**

### Step 1: Add Items to Cart
Customer adds products to their cart as usual.

### Step 2: Enter Promotion Code (Optional)
Customer enters a promotion code in the checkout form.

### Step 3: Validate Code (Recommended)
Before checkout, the frontend can validate the code to show the customer:
- If the code is valid
- What discount they'll get
- Any error messages

### Step 4: Create Order with Code
Customer completes checkout with the promotion code. The system:
- Validates the code
- Calculates the discount (product-specific if applicable)
- Applies the discount to the order total
- Records the code usage

---

## 📱 **Frontend Implementation**

### 1. Validate Promotion Code (Before Checkout)

**GraphQL Query:**
```graphql
query ValidatePromotion($code: String!, $subtotal: Decimal!, $deliveryFee: Decimal) {
  validatePromotion(
    code: $code
    subtotal: $subtotal
    deliveryFee: $deliveryFee
  ) {
    valid
    promotion {
      code
      name
      discountDisplay
      discountType
      discountValue
    }
    discountAmount
    message
  }
}
```

**Variables:**
```json
{
  "code": "SAVE10",
  "subtotal": "50.00",
  "deliveryFee": "5.00"
}
```

**Response (Valid Code):**
```json
{
  "data": {
    "validatePromotion": {
      "valid": true,
      "promotion": {
        "code": "SAVE10",
        "name": "10% Off",
        "discountDisplay": "10% off",
        "discountType": "percentage",
        "discountValue": "10.00"
      },
      "discountAmount": "5.00",
      "message": "Code applied! You save $5.00"
    }
  }
}
```

**Response (Invalid Code):**
```json
{
  "data": {
    "validatePromotion": {
      "valid": false,
      "promotion": null,
      "discountAmount": "0.00",
      "message": "Invalid promotion code"
    }
  }
}
```

**Response (Minimum Order Not Met):**
```json
{
  "data": {
    "validatePromotion": {
      "valid": false,
      "promotion": {
        "code": "SAVE10",
        "name": "10% Off",
        "discountDisplay": "10% off"
      },
      "discountAmount": "0.00",
      "message": "Minimum order amount is $30.00"
    }
  }
}
```

---

### 2. Create Order with Promotion Code

**GraphQL Mutation:**
```graphql
mutation CreateOrder($input: CreateOrderInput!) {
  createOrder(input: $input) {
    order {
      id
      orderNumber
      customerName
      subtotal
      deliveryFee
      discountAmount
      discountCode
      total
      items {
        productName
        quantity
        subtotal
      }
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
    "customerName": "John Doe",
    "customerEmail": "john@example.com",
    "customerPhone": "+1234567890",
    "orderType": "delivery",
    "deliveryAddress": "123 Main St, City, State 12345",
    "deliveryInstructions": "Ring doorbell twice",
    "deliveryFee": "5.00",
    "orderNotes": "Please make it spicy",
    "promotionCode": "SAVE10"
  }
}
```

**Response:**
```json
{
  "data": {
    "createOrder": {
      "order": {
        "id": "1",
        "orderNumber": "ORD-2024-001",
        "customerName": "John Doe",
        "subtotal": "50.00",
        "deliveryFee": "5.00",
        "discountAmount": "5.00",
        "discountCode": "SAVE10",
        "total": "50.00",
        "items": [
          {
            "productName": "Margherita Pizza",
            "quantity": 2,
            "subtotal": "50.00"
          }
        ]
      },
      "success": true,
      "message": "Order created successfully! Order number: ORD-2024-001"
    }
  }
}
```

---

## 💡 **Example Frontend Flow**

### React/TypeScript Example:

```typescript
// 1. Validate code when user enters it
const validatePromotionCode = async (code: string, subtotal: number, deliveryFee: number) => {
  const response = await graphqlClient.query({
    query: VALIDATE_PROMOTION_QUERY,
    variables: {
      code: code.toUpperCase(),
      subtotal: subtotal.toFixed(2),
      deliveryFee: deliveryFee.toFixed(2)
    }
  });
  
  return response.data.validatePromotion;
};

// 2. Show validation result to user
const handleCodeValidation = async () => {
  const result = await validatePromotionCode(
    enteredCode,
    cartSubtotal,
    deliveryFee
  );
  
  if (result.valid) {
    setDiscountAmount(result.discountAmount);
    setDiscountMessage(result.message);
    setPromotionCode(enteredCode);
  } else {
    setError(result.message);
    setDiscountAmount(0);
  }
};

// 3. Apply code during checkout
const handleCheckout = async () => {
  const orderInput = {
    customerName: formData.name,
    customerEmail: formData.email,
    customerPhone: formData.phone,
    orderType: orderType,
    deliveryAddress: formData.address,
    deliveryFee: deliveryFee,
    promotionCode: promotionCode, // Include the validated code
    // ... other fields
  };
  
  const response = await graphqlClient.mutate({
    mutation: CREATE_ORDER_MUTATION,
    variables: { input: orderInput }
  });
  
  return response.data.createOrder;
};
```

---

## ✅ **What Happens Behind the Scenes**

### When Customer Enters Code:

1. **Validation Query** (`validatePromotion`):
   - Checks if code exists
   - Verifies code is active and within validity period
   - Checks if usage limit is reached
   - Validates minimum order amount
   - Calculates discount amount
   - Returns discount preview

2. **Order Creation** (`createOrder`):
   - Creates order items first
   - Validates promotion code again
   - Calculates discount based on:
     - Product selection (if product-specific)
     - Apply flags (base price, toppings, included items)
     - Discount type (percentage, fixed, free delivery)
   - Applies discount to order total
   - Increments promotion usage count
   - Saves order with discount details

---

## 🎯 **Product-Specific Promotions**

When a promotion is product-specific:

1. **Validation**: Shows discount preview based on current cart items
2. **Order Creation**: Only applies discount to eligible products in the order
3. **Calculation**: Discount is calculated only on:
   - Selected products (if `apply_to_entire_order = false`)
   - Base price (if `apply_to_base_price = true`)
   - Toppings (if `apply_to_toppings = true`)
   - Included items (if `apply_to_included_items = true`)

**Example:**
- Promotion: "20% Off Pizzas" (only applies to pizza products)
- Cart: 2 Pizzas ($30) + 1 Pasta ($15) = $45 subtotal
- Discount: Only $6 (20% of $30, not $45)
- Final Total: $39 + delivery fee

---

## ⚠️ **Error Handling**

### Common Error Messages:

1. **"Invalid promotion code"**
   - Code doesn't exist
   - Code was mistyped

2. **"This promotion hasn't started yet"**
   - Current date is before `valid_from`

3. **"This promotion has expired"**
   - Current date is after `valid_until`

4. **"This promotion has reached its usage limit"**
   - `times_used >= usage_limit`

5. **"This promotion is not active"**
   - `is_active = false`

6. **"Minimum order amount is $X.XX"**
   - Order subtotal is less than `minimum_order_amount`

---

## 📋 **Best Practices for Frontend**

1. **Validate Before Checkout**:
   - Show discount preview immediately
   - Update total in real-time
   - Display clear error messages

2. **User Experience**:
   - Auto-uppercase the code (backend does this too)
   - Show discount amount prominently
   - Display promotion name/description
   - Allow removing the code

3. **Error Handling**:
   - Show specific error messages
   - Highlight invalid codes
   - Clear discount if code is removed

4. **Visual Feedback**:
   - Show checkmark for valid codes
   - Show discount badge
   - Update order summary with discount

---

## 🔒 **Security Notes**

- Codes are case-insensitive (backend uppercases them)
- Validation happens on both frontend (preview) and backend (actual order)
- Usage limits are enforced server-side
- Discount amounts are calculated server-side (never trust client)

---

## 📊 **Summary**

**Customer Experience:**
1. ✅ Add items to cart
2. ✅ Enter promotion code
3. ✅ See discount preview (optional validation)
4. ✅ Complete checkout with code
5. ✅ Discount automatically applied to order

**Backend Handles:**
- ✅ Code validation
- ✅ Discount calculation
- ✅ Product-specific logic
- ✅ Usage tracking
- ✅ Error handling

The system is designed to be simple for customers while providing powerful, flexible promotion management for admins! 🎉

