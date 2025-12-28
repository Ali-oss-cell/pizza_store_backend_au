# 💰 Price Handling Documentation

This document explains where and how prices are calculated and handled throughout the system.

---

## 📍 **Price Calculation Locations**

### 1. **Cart Item Price Calculation**
**File:** `pizza_store/cart/utils.py`  
**Function:** `calculate_item_price(product, size=None, toppings=None)`

```python
def calculate_item_price(product, size=None, toppings=None):
    """
    Calculate price for a cart item with size and toppings
    Returns: Decimal price
    """
    # Start with base price
    price = product.base_price
    
    # Add size modifier if size is provided
    if size:
        if size in product.available_sizes.all():
            price += size.price_modifier
    
    # Add toppings prices
    if toppings:
        for topping_data in toppings:
            if isinstance(topping_data, dict) and 'price' in topping_data:
                price += Decimal(str(topping_data['price']))
            elif isinstance(topping_data, Topping):
                if topping_data in product.available_toppings.all():
                    price += Decimal(str(topping_data.price))
    
    return price
```

**Called from:**
- `cart/schema.py::AddToCart.mutate()` - When adding item to cart
- `cart/schema.py::UpdateCartItem.mutate()` - When updating cart item

---

### 2. **Cart Item Subtotal**
**File:** `pizza_store/cart/models.py`  
**Method:** `CartItem.get_subtotal()`

```python
def get_subtotal(self):
    """Calculate subtotal for this item"""
    toppings_total = sum(
        Decimal(str(t.get('price', 0))) for t in self.selected_toppings
    )
    return (self.unit_price + toppings_total) * Decimal(self.quantity)
```

**Used for:**
- Displaying item subtotal in cart
- Calculating cart total

---

### 3. **Cart Total**
**File:** `pizza_store/cart/models.py`  
**Method:** `Cart.get_total()`

```python
def get_total(self):
    """Calculate total cart price"""
    total = sum(item.get_subtotal() for item in self.items.all())
    return total if total else Decimal('0.00')
```

**Used for:**
- Displaying cart total
- Order subtotal calculation

---

### 4. **Order Total Calculation**
**File:** `pizza_store/orders/schema.py`  
**Function:** `CreateOrder.mutate()`

```python
# Calculate totals
subtotal = cart.get_total()
delivery_fee = Decimal(str(input.get('delivery_fee', 0))) if input.get('delivery_fee') else Decimal('0.00')

# Add delivery fee only for delivery orders
if order_type == 'pickup':
    delivery_fee = Decimal('0.00')

# Apply promotion code if provided
discount_amount = Decimal('0.00')
discount_code = None
promotion_code = input.get('promotion_code')

if promotion_code:
    promotion = Promotion.objects.get(code__iexact=promotion_code)
    if promotion.is_valid:
        discount_amount = promotion.calculate_discount(subtotal, delivery_fee)
        discount_code = promotion.code

total = subtotal + delivery_fee - discount_amount
```

**Used for:**
- Final order total at checkout
- Stored in `Order.total` field

---

### 5. **Order Item Subtotal (Snapshot)**
**File:** `pizza_store/orders/schema.py`  
**Function:** `CreateOrder.mutate()` (inside order item creation loop)

```python
# Calculate item subtotal (including toppings)
toppings_total = sum(
    D(str(t.get('price', 0))) for t in cart_item.selected_toppings
)
item_subtotal = (cart_item.unit_price + toppings_total) * D(cart_item.quantity)
```

**Used for:**
- Creating order item snapshot
- Historical record of item price at checkout

---

## 📊 **Price Fields in Models**

### Product Model
**File:** `pizza_store/products/models.py`

```python
class Product(models.Model):
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    # This is the base price for the smallest/default size
```

### Size Model
**File:** `pizza_store/products/models.py`

```python
class Size(models.Model):
    price_modifier = models.DecimalField(max_digits=10, decimal_places=2)
    # Can be positive (+$3.00) or negative (-$1.00)
    # Final price = base_price + price_modifier
```

### Topping Model
**File:** `pizza_store/products/models.py`

```python
class Topping(models.Model):
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # Individual topping price added to base price
```

### CartItem Model
**File:** `pizza_store/cart/models.py`

```python
class CartItem(models.Model):
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    # Snapshot of calculated price when item is added
    selected_toppings = models.JSONField(default=list)
    # Stores: [{"id": "1", "name": "Extra Cheese", "price": "2.00"}, ...]
    quantity = models.PositiveIntegerField(default=1)
```

### Order Model
**File:** `pizza_store/orders/models.py`

```python
class Order(models.Model):
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    # Cart total at checkout
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    # Delivery fee (only for delivery orders)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    # Discount from promotion code
    total = models.DecimalField(max_digits=10, decimal_places=2)
    # Final order total: subtotal + delivery_fee - discount_amount
```

### OrderItem Model
**File:** `pizza_store/orders/models.py`

```python
class OrderItem(models.Model):
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    # Snapshot of item price at checkout
    selected_toppings = models.JSONField(default=list)
    # Snapshot of toppings with prices
    quantity = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    # Snapshot of item subtotal at checkout
```

---

## 🔄 **Price Flow**

### Adding Item to Cart:
1. User selects product, size, and toppings
2. `calculate_item_price()` calculates: `basePrice + sizeModifier + sum(toppingPrices)`
3. Price is stored in `CartItem.unit_price` (snapshot)
4. Toppings stored in `CartItem.selected_toppings` as JSON with prices

### Viewing Cart:
1. `CartItem.get_subtotal()` calculates: `(unit_price + toppings_total) * quantity`
2. `Cart.get_total()` sums all item subtotals

### Checkout:
1. `Cart.get_total()` provides subtotal
2. Delivery fee added (if delivery order)
3. Promotion discount applied (if code provided)
4. Final total: `subtotal + deliveryFee - discountAmount`
5. All prices snapshotted in `Order` and `OrderItem` models

---

## ⚠️ **Important Notes**

### 1. **Decimal vs Float**
- **Always use `Decimal`** for prices (no floating point errors)
- Convert strings to Decimal: `Decimal(str(price))`
- Store prices as strings in JSON: `str(topping.price)`

### 2. **Price Snapshots**
- Cart item prices are **snapshotted** when added (prevents price changes affecting cart)
- Order prices are **snapshotted** at checkout (historical record)

### 3. **GraphQL Price Format**
- Prices in mutations must be **strings**: `"14.99"` not `14.99`
- GraphQL `Decimal` type expects string input

### 4. **JSON Storage**
- Topping prices in `selected_toppings` JSON are stored as **strings**
- Convert back to Decimal when calculating: `Decimal(str(t.get('price', 0)))`

### 5. **Price Calculation Formula**
```
Item Price = basePrice + sizeModifier + sum(toppingPrices)
Item Subtotal = (basePrice + sizeModifier + toppings) * quantity
Cart Total = sum(all_item_subtotals)
Order Total = cartTotal + deliveryFee - discountAmount
```

---

## 🧪 **Testing Price Calculations**

### Example Calculation:
```
Product: Margherita Pizza
Base Price: $14.99

Size: Large
Price Modifier: +$3.00

Toppings:
- Extra Cheese: +$2.00
- Mushrooms: +$1.50

Quantity: 2

Calculation:
unit_price = 14.99 + 3.00 + 2.00 + 1.50 = $21.49
subtotal = 21.49 * 2 = $42.98
```

### In Code:
```python
from decimal import Decimal
from products.models import Product, Size, Topping
from cart.utils import calculate_item_price

product = Product.objects.get(name="Margherita Pizza")
size = Size.objects.get(name="Large")
toppings = [
    {"id": "1", "name": "Extra Cheese", "price": "2.00"},
    {"id": "2", "name": "Mushrooms", "price": "1.50"}
]

unit_price = calculate_item_price(product, size, toppings)
# Returns: Decimal('21.49')

subtotal = (unit_price + Decimal('2.00') + Decimal('1.50')) * Decimal('2')
# Returns: Decimal('42.98')
```

---

## 📝 **Code References**

| Location | Purpose | Key Function/Method |
|----------|---------|-------------------|
| `cart/utils.py` | Calculate item price | `calculate_item_price()` |
| `cart/models.py` | Cart item subtotal | `CartItem.get_subtotal()` |
| `cart/models.py` | Cart total | `Cart.get_total()` |
| `cart/schema.py` | Add to cart | `AddToCart.mutate()` |
| `cart/schema.py` | Update cart item | `UpdateCartItem.mutate()` |
| `orders/schema.py` | Create order | `CreateOrder.mutate()` |
| `orders/models.py` | Order totals | `Order` model fields |

---

**All prices use `Decimal` for precision and are stored as strings in JSON fields!**

