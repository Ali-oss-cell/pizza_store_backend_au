# Sale Pricing System

## Overview

The sale pricing system allows admins to set discounted prices on products that automatically apply to **all users** without requiring a promotion code. This is different from promotions/coupons which require customers to enter a code.

---

## 🎯 **Key Features**

1. **Automatic Application**: Sale prices apply to all users automatically
2. **Time-Based**: Set start and end dates for sales
3. **Visual Indicators**: Products show sale badges and crossed-out original prices
4. **Cart Integration**: Sale prices are automatically used in cart calculations
5. **Size Support**: Sale prices work with all product sizes

---

## 📋 **Model Fields**

### New Fields in `Product` Model:

```python
sale_price = DecimalField(null=True, blank=True)
# Sale price (applies to all users when active)

sale_start_date = DateTimeField(null=True, blank=True)
# When the sale starts (leave empty to start immediately)

sale_end_date = DateTimeField(null=True, blank=True)
# When the sale ends (leave empty for no end date)
```

### Properties and Methods:

```python
@property
is_on_sale
# Returns True if product is currently on sale

def get_current_base_price()
# Returns sale_price if on sale, otherwise base_price

def get_price_for_size(size)
# Returns price for a specific size (uses sale price if on sale)

@property
discount_percentage
# Calculates discount percentage when on sale
```

---

## 🔧 **How It Works**

### Sale Status Logic:

A product is considered "on sale" when:
1. `sale_price` is set (not null/empty)
2. Current date is after `sale_start_date` (or `sale_start_date` is empty)
3. Current date is before `sale_end_date` (or `sale_end_date` is empty)

### Price Calculation:

- **When on sale**: Uses `sale_price` as the base price
- **When not on sale**: Uses `base_price` as the base price
- **With sizes**: Size modifiers are added to the current base price (sale or regular)

---

## 📝 **GraphQL API**

### **ProductType** (Query Response)

```graphql
type ProductType {
  id: ID!
  name: String!
  basePrice: Decimal!
  
  # Sale pricing fields
  salePrice: Decimal
  saleStartDate: DateTime
  saleEndDate: DateTime
  
  # Computed fields
  isOnSale: Boolean!
  currentPrice: Decimal!  # Sale price if on sale, otherwise base price
  discountPercentage: Int  # Discount percentage when on sale
  
  # ... other fields
}
```

### **ProductInput** (Create/Update)

```graphql
input ProductInput {
  name: String!
  basePrice: Decimal!
  
  # Sale pricing (optional)
  salePrice: Decimal
  saleStartDate: DateTime
  saleEndDate: DateTime
  
  # ... other fields
}
```

---

## 💡 **Example Use Cases**

### Example 1: Set a Product on Sale

**GraphQL Mutation:**
```graphql
mutation {
  updateProduct(
    id: "1"
    input: {
      salePrice: "12.99"
      saleStartDate: "2024-01-01T00:00:00Z"
      saleEndDate: "2024-01-31T23:59:59Z"
    }
  ) {
    product {
      id
      name
      basePrice
      salePrice
      isOnSale
      currentPrice
      discountPercentage
    }
    success
  }
}
```

**Result**: Product shows sale price from Jan 1 to Jan 31, 2024.

---

### Example 2: Create Product with Sale Price

```graphql
mutation {
  createProduct(input: {
    name: "Margherita Pizza"
    basePrice: "15.99"
    salePrice: "12.99"
    saleStartDate: "2024-01-01T00:00:00Z"
    saleEndDate: "2024-01-31T23:59:59Z"
    categoryId: "1"
    # ... other fields
  }) {
    product {
      id
      name
      basePrice
      salePrice
      isOnSale
      currentPrice
      discountPercentage
    }
    success
  }
}
```

---

### Example 3: Remove Sale Price

```graphql
mutation {
  updateProduct(
    id: "1"
    input: {
      salePrice: null
      saleStartDate: null
      saleEndDate: null
    }
  ) {
    product {
      id
      isOnSale
      currentPrice
    }
    success
  }
}
```

---

## 🔍 **Query Examples**

### Get Product with Sale Info

```graphql
query {
  product(id: "1") {
    id
    name
    basePrice
    salePrice
    saleStartDate
    saleEndDate
    isOnSale
    currentPrice
    discountPercentage
    availableSizes {
      id
      name
      priceModifier
    }
  }
}
```

**Response:**
```json
{
  "data": {
    "product": {
      "id": "1",
      "name": "Margherita Pizza",
      "basePrice": "15.99",
      "salePrice": "12.99",
      "saleStartDate": "2024-01-01T00:00:00Z",
      "saleEndDate": "2024-01-31T23:59:59Z",
      "isOnSale": true,
      "currentPrice": "12.99",
      "discountPercentage": 19
    }
  }
}
```

---

### Get All Products on Sale

```graphql
query {
  allProducts {
    id
    name
    basePrice
    salePrice
    isOnSale
    currentPrice
    discountPercentage
  }
}
```

**Frontend can filter:**
```javascript
const productsOnSale = products.filter(p => p.isOnSale);
```

---

## 🛒 **Cart Integration**

Sale prices are **automatically** used when:
- Adding items to cart
- Calculating cart totals
- Displaying prices in cart

**Example:**
- Product base price: $15.99
- Sale price: $12.99
- Size: Large (+$3.00)
- **Cart price**: $12.99 + $3.00 = $15.99 (not $18.99)

---

## 📊 **Admin Interface**

The Django Admin interface shows:

1. **List View**:
   - Price display with strikethrough original price
   - Sale badge indicator
   - Current price (sale or regular)

2. **Edit Form**:
   - `base_price`: Regular price
   - `sale_price`: Sale price
   - `sale_start_date`: When sale starts
   - `sale_end_date`: When sale ends

3. **Visual Indicators**:
   - Strikethrough on original price when on sale
   - Red sale badge
   - Discount percentage display

---

## 🎨 **Frontend Display Examples**

### Product Card Display:

```typescript
// React/TypeScript Example
const ProductCard = ({ product }) => {
  return (
    <div className="product-card">
      <h3>{product.name}</h3>
      
      {product.isOnSale ? (
        <div className="pricing">
          <span className="original-price">${product.basePrice}</span>
          <span className="sale-price">${product.currentPrice}</span>
          <span className="discount-badge">
            {product.discountPercentage}% OFF
          </span>
        </div>
      ) : (
        <div className="pricing">
          <span className="price">${product.basePrice}</span>
        </div>
      )}
      
      {product.isOnSale && (
        <span className="sale-badge">SALE</span>
      )}
    </div>
  );
};
```

---

## ⚙️ **Technical Details**

### Price Calculation Flow:

1. **Product Query**: Returns `isOnSale`, `currentPrice`, `discountPercentage`
2. **Cart Addition**: Uses `product.get_current_base_price()` for base price
3. **Size Modifiers**: Added to current base price (sale or regular)
4. **Cart Display**: Shows sale prices automatically

### Sale Status Check:

```python
@property
def is_on_sale(self):
    if not self.sale_price:
        return False
    
    now = timezone.now()
    
    # Check if sale has started
    if self.sale_start_date and now < self.sale_start_date:
        return False
    
    # Check if sale has ended
    if self.sale_end_date and now > self.sale_end_date:
        return False
    
    return True
```

---

## 🔄 **Sale vs Promotion Codes**

| Feature | Sale Pricing | Promotion Codes |
|---------|-------------|-----------------|
| **Application** | Automatic | Requires code entry |
| **Visibility** | All users see it | Hidden until code entered |
| **Scope** | Per product | Can be order-wide or product-specific |
| **Time Control** | Start/end dates | Start/end dates |
| **Usage Limits** | No limits | Can set usage limits |
| **Minimum Order** | No minimum | Can set minimum order |

**Best Practice**: Use sale pricing for general discounts, promotion codes for special offers.

---

## ✅ **Best Practices**

1. **Sale Dates**:
   - Always set `sale_end_date` to avoid permanent sales
   - Use `sale_start_date` for scheduled sales

2. **Price Validation**:
   - Ensure `sale_price < base_price` (frontend validation)
   - Don't set negative sale prices

3. **Display**:
   - Show original price with strikethrough
   - Highlight sale price prominently
   - Display discount percentage

4. **Testing**:
   - Test with different date ranges
   - Verify cart calculations use sale prices
   - Check size modifiers work correctly

---

## 📋 **Summary**

The sale pricing system provides:

✅ **Automatic Discounts**: No code required  
✅ **Time-Based Control**: Start and end dates  
✅ **Visual Indicators**: Sale badges and price displays  
✅ **Cart Integration**: Automatic price calculation  
✅ **Size Support**: Works with all product sizes  
✅ **Admin Friendly**: Easy to manage in Django Admin  

This makes it easy to run sales and promotions that apply to all customers automatically! 🎉

