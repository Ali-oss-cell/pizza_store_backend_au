# Promotion GraphQL API Verification

## ✅ **Status: All Fields Match Frontend Requirements**

This document verifies that the backend GraphQL schema matches the frontend's expected fields.

---

## **1. Promotion Query Response (`allPromotions`)**

### Frontend Expects:
```typescript
{
  id: string
  code: string
  name: string
  discountDisplay?: string        // Optional
  discountType: string            // 'percentage' | 'fixed' | 'free_delivery'
  discountValue: string           // Decimal as string
  minimumOrderAmount?: string      // Optional - Decimal as string
  maximumDiscount?: string        // Optional - Decimal as string
  usageLimit?: number             // Optional - Integer
  timesUsed: number               // Integer
  isActive: boolean
  validFrom: string               // ISO datetime string
  validUntil: string              // ISO datetime string
}
```

### Backend Provides (via `PromotionType`):
```python
# Fields in PromotionType:
- id                    → GraphQL: id (ID)
- code                  → GraphQL: code (String)
- name                  → GraphQL: name (String)
- discount_display      → GraphQL: discountDisplay (String) ✅ Custom resolver
- discount_type         → GraphQL: discountType (String)
- discount_value        → GraphQL: discountValue (Decimal → String)
- minimum_order_amount  → GraphQL: minimumOrderAmount (Decimal → String, nullable)
- maximum_discount      → GraphQL: maximumDiscount (Decimal → String, nullable)
- usage_limit           → GraphQL: usageLimit (Int, nullable)
- times_used            → GraphQL: timesUsed (Int)
- is_active             → GraphQL: isActive (Boolean)
- valid_from            → GraphQL: validFrom (DateTime → ISO String)
- valid_until           → GraphQL: validUntil (DateTime → ISO String)
```

**✅ All fields match!** Graphene-Django automatically converts:
- `snake_case` → `camelCase`
- `Decimal` → `String` in GraphQL responses
- `DateTime` → ISO 8601 string

---

## **2. Promotion Input (Create/Update Mutations)**

### Frontend Sends:
```typescript
{
  code: string                    // Required - will be uppercase
  name: string                    // Required
  description?: string | null     // Optional
  discountType: string            // Required - 'percentage' | 'fixed' | 'free_delivery'
  discountValue: string           // Required - Decimal as string (e.g., "10.00")
  maximumDiscount?: string | null  // Optional - Decimal as string
  minimumOrderAmount?: string | null // Optional - Decimal as string
  usageLimit?: number | null      // Optional - Integer
  isActive: boolean               // Required
  validFrom: string               // Required - ISO datetime string
  validUntil: string              // Required - ISO datetime string
}
```

### Backend Accepts (via `PromotionInput`):
```python
class PromotionInput:
    code = graphene.String(required=True)                    ✅
    name = graphene.String(required=True)                    ✅
    description = graphene.String()                          ✅ Optional
    discount_type = graphene.String(required=True)           ✅
    discount_value = graphene.Decimal(required=True)          ✅
    maximum_discount = graphene.Decimal()                    ✅ Optional
    minimum_order_amount = graphene.Decimal()                ✅ Optional
    usage_limit = graphene.Int()                             ✅ Optional
    is_active = graphene.Boolean(required=True)              ✅ FIXED: Now required
    valid_from = graphene.DateTime(required=True)            ✅
    valid_until = graphene.DateTime(required=True)           ✅
```

**✅ All fields match!** The backend:
- Accepts camelCase field names (Graphene converts automatically)
- Accepts Decimal values as strings
- Accepts DateTime as ISO 8601 strings
- Uppercases the `code` field automatically in mutations

---

## **3. GraphQL Operations Available**

### Queries:
1. **`allPromotions(activeOnly: Boolean)`** - Get all promotions (admin only)
2. **`promotion(id: ID, code: String)`** - Get single promotion (admin only)
3. **`validatePromotion(code: String!, subtotal: Decimal!, deliveryFee: Decimal)`** - Validate promotion code (public)

### Mutations:
1. **`createPromotion(input: PromotionInput!)`** - Create promotion (admin only)
2. **`updatePromotion(id: ID!, input: PromotionInput!)`** - Update promotion (admin only)
3. **`deletePromotion(id: ID!)`** - Delete promotion (admin only)

---

## **4. Field Type Conversions**

| Django Model Field | GraphQL Type | Frontend Receives |
|-------------------|--------------|-------------------|
| `CharField` | `String` | `string` ✅ |
| `DecimalField` | `Decimal` | `string` (e.g., "10.00") ✅ |
| `IntegerField` | `Int` | `number` ✅ |
| `BooleanField` | `Boolean` | `boolean` ✅ |
| `DateTimeField` | `DateTime` | `string` (ISO 8601) ✅ |

---

## **5. Special Behaviors**

### Code Uppercasing:
- Backend automatically uppercases `code` in `CreatePromotion` and `UpdatePromotion` mutations
- Frontend can send lowercase, backend stores as uppercase

### Discount Display:
- Backend provides `discountDisplay` resolver that formats:
  - Percentage: `"10% off"`
  - Fixed: `"$10.00 off"`
  - Free Delivery: `"Free Delivery"`
- Frontend can use this or generate its own

### Validation:
- `validatePromotion` query checks:
  - Code exists
  - Promotion is active
  - Promotion is within valid date range
  - Usage limit not exceeded
  - Minimum order amount met
  - Returns calculated discount amount

---

## **6. Example GraphQL Operations**

### Query: Get All Promotions
```graphql
query {
  allPromotions {
    id
    code
    name
    discountDisplay
    discountType
    discountValue
    minimumOrderAmount
    maximumDiscount
    usageLimit
    timesUsed
    isActive
    validFrom
    validUntil
  }
}
```

### Mutation: Create Promotion
```graphql
mutation {
  createPromotion(input: {
    code: "SAVE10"
    name: "10% Off"
    description: "Save 10% on your order"
    discountType: "percentage"
    discountValue: "10.00"
    maximumDiscount: "20.00"
    minimumOrderAmount: "30.00"
    usageLimit: 100
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
    message
  }
}
```

### Query: Validate Promotion
```graphql
query {
  validatePromotion(
    code: "SAVE10"
    subtotal: "50.00"
    deliveryFee: "5.00"
  ) {
    valid
    promotion {
      code
      name
      discountDisplay
    }
    discountAmount
    message
  }
}
```

---

## **✅ Verification Result**

**All fields match frontend requirements!**

- ✅ All required fields present
- ✅ All optional fields properly marked
- ✅ Field types match (Decimal → String, DateTime → ISO String)
- ✅ Field names auto-converted (snake_case → camelCase)
- ✅ `is_active` now required in input (fixed)
- ✅ Code uppercasing handled automatically
- ✅ Discount display resolver provided

The backend is ready for frontend integration! 🎉

