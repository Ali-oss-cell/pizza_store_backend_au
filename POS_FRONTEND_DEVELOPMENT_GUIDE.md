# POS Frontend Development Guide

## 🎯 Overview

This guide helps you build the POS frontend that integrates with your existing React dashboard. The POS can be:
1. **Separate app** (recommended) - New React app at `/pos` route or separate subdomain
2. **Integrated into dashboard** - Add POS section to existing admin dashboard

---

## 📋 What You Need

### **Existing Setup:**
- ✅ React dashboard (already have)
- ✅ React website (already have)
- ✅ GraphQL client setup (Apollo Client or similar)

### **What to Build:**
- POS interface (touch-optimized)
- Barcode scanning integration
- Cart management
- Order creation
- Receipt printing
- Inventory display

---

## 🏗️ Architecture Options

### **Option 1: Separate POS App (Recommended)**

**Structure:**
```
your-frontend-project/
├── src/
│   ├── dashboard/        # Your existing admin dashboard
│   ├── website/          # Your existing customer website
│   └── pos/              # NEW: POS application
│       ├── components/
│       ├── pages/
│       ├── hooks/
│       └── utils/
```

**Benefits:**
- Clean separation
- Different UI/UX optimized for POS
- Can deploy separately
- Easier to maintain

### **Option 2: Integrated into Dashboard**

**Structure:**
```
your-frontend-project/
├── src/
│   ├── dashboard/
│   │   ├── pages/
│   │   │   ├── orders/
│   │   │   ├── products/
│   │   │   └── pos/      # NEW: POS section
```

**Benefits:**
- Single codebase
- Shared components
- Same authentication

---

## 🚀 Recommended: Separate POS App

### **Step 1: Create POS Route/Module**

If using React Router:

```javascript
// src/App.js or src/routes.js
import POSApp from './pos/App';

<Route path="/pos/*" element={<POSApp />} />
```

Or create separate entry point:

```javascript
// src/pos/index.js
import React from 'react';
import ReactDOM from 'react-dom/client';
import POSApp from './App';
import './styles/pos.css';

const root = ReactDOM.createRoot(document.getElementById('pos-root'));
root.render(<POSApp />);
```

---

## 📁 POS Component Structure

```
pos/
├── App.js                 # Main POS app component
├── pages/
│   ├── Login.js          # POS login (can reuse dashboard login)
│   ├── POSMain.js        # Main POS interface
│   ├── Inventory.js     # Inventory management
│   └── Reports.js        # Daily sales reports
├── components/
│   ├── BarcodeScanner.js # Barcode input & scanning
│   ├── ProductGrid.js    # Product display grid
│   ├── ProductCard.js     # Single product card
│   ├── Cart.js           # Shopping cart
│   ├── CartItem.js       # Cart item component
│   ├── Checkout.js       # Checkout form
│   ├── Receipt.js        # Receipt display/print
│   └── StatsCard.js      # Statistics card
├── hooks/
│   ├── usePOSProducts.js # Fetch POS products
│   ├── useBarcodeScan.js  # Barcode scanning hook
│   ├── usePOSCart.js      # POS cart management
│   └── usePOSOrders.js    # POS order operations
├── utils/
│   ├── graphql.js        # GraphQL queries/mutations
│   ├── receipt.js         # Receipt formatting
│   └── printer.js         # Print utilities
└── styles/
    └── pos.css           # POS-specific styles
```

---

## 🔧 GraphQL Setup

### **1. POS Queries & Mutations**

Create `pos/utils/graphql.js`:

```javascript
import { gql } from '@apollo/client';

// ==================== QUERIES ====================

export const POS_PRODUCTS = gql`
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
`;

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
      imageUrl
    }
  }
`;

export const POS_RECENT_ORDERS = gql`
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
`;

export const RECEIPT = gql`
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
`;

export const POS_TODAY_STATS = gql`
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
`;

// ==================== MUTATIONS ====================

export const CREATE_POS_ORDER = gql`
  mutation CreatePOSOrder($input: POSOrderInput!) {
    createPosOrder(input: $input) {
      success
      message
      order {
        id
        orderNumber
        total
        status
      }
    }
  }
`;
```

---

## 🎨 Core Components

### **1. Barcode Scanner Component**

```javascript
// pos/components/BarcodeScanner.js
import React, { useRef, useEffect } from 'react';
import { useLazyQuery } from '@apollo/client';
import { SCAN_BARCODE } from '../utils/graphql';

const BarcodeScanner = ({ onProductScanned }) => {
  const inputRef = useRef(null);
  const [scanBarcode, { data, loading, error }] = useLazyQuery(SCAN_BARCODE);

  // Auto-focus on mount (for barcode scanner)
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleBarcodeInput = (e) => {
    const barcode = e.target.value.trim();
    
    // When barcode is entered (scanner types it automatically)
    if (barcode.length >= 8) { // Minimum barcode length
      scanBarcode({ variables: { barcode } });
      e.target.value = ''; // Clear for next scan
    }
  };

  // Handle scanned product
  useEffect(() => {
    if (data?.scanBarcode) {
      onProductScanned(data.scanBarcode);
    }
  }, [data, onProductScanned]);

  return (
    <div className="barcode-scanner">
      <input
        ref={inputRef}
        type="text"
        placeholder="Scan barcode or enter manually"
        onInput={handleBarcodeInput}
        className="barcode-input"
        autoFocus
      />
      {loading && <div>Scanning...</div>}
      {error && <div className="error">Product not found</div>}
    </div>
  );
};

export default BarcodeScanner;
```

### **2. Product Grid Component**

```javascript
// pos/components/ProductGrid.js
import React from 'react';
import ProductCard from './ProductCard';

const ProductGrid = ({ products, onAddToCart, loading }) => {
  if (loading) return <div>Loading products...</div>;

  return (
    <div className="product-grid">
      {products.map(product => (
        <ProductCard
          key={product.id}
          product={product}
          onAddToCart={onAddToCart}
        />
      ))}
    </div>
  );
};

export default ProductGrid;
```

### **3. Product Card Component**

```javascript
// pos/components/ProductCard.js
import React from 'react';

const ProductCard = ({ product, onAddToCart }) => {
  const handleAddToCart = () => {
    onAddToCart({
      productId: product.id,
      quantity: 1,
      price: product.currentPrice
    });
  };

  return (
    <div className={`product-card ${!product.isInStock ? 'out-of-stock' : ''}`}>
      {product.imageUrl && (
        <img src={product.imageUrl} alt={product.name} />
      )}
      <div className="product-info">
        <h3>{product.name}</h3>
        <p className="price">${product.currentPrice}</p>
        {product.trackInventory && (
          <div className="stock-info">
            <span className={product.isLowStock ? 'low-stock' : ''}>
              Stock: {product.stockQuantity}
            </span>
          </div>
        )}
        <button
          onClick={handleAddToCart}
          disabled={product.trackInventory && !product.isInStock}
          className="add-to-cart-btn"
        >
          {product.trackInventory && !product.isInStock ? 'Out of Stock' : 'Add'}
        </button>
      </div>
    </div>
  );
};

export default ProductCard;
```

### **4. POS Cart Component**

```javascript
// pos/components/Cart.js
import React from 'react';
import CartItem from './CartItem';

const Cart = ({ items, onUpdateQuantity, onRemoveItem, onClear, subtotal }) => {
  return (
    <div className="pos-cart">
      <div className="cart-header">
        <h2>Cart</h2>
        <button onClick={onClear} className="clear-btn">Clear</button>
      </div>
      
      <div className="cart-items">
        {items.length === 0 ? (
          <p>Cart is empty</p>
        ) : (
          items.map(item => (
            <CartItem
              key={item.id}
              item={item}
              onUpdateQuantity={onUpdateQuantity}
              onRemove={onRemoveItem}
            />
          ))
        )}
      </div>
      
      <div className="cart-footer">
        <div className="subtotal">
          <strong>Subtotal: ${subtotal.toFixed(2)}</strong>
        </div>
      </div>
    </div>
  );
};

export default Cart;
```

### **5. Checkout Component**

```javascript
// pos/components/Checkout.js
import React, { useState } from 'react';
import { useMutation } from '@apollo/client';
import { CREATE_POS_ORDER } from '../utils/graphql';

const Checkout = ({ cartItems, onOrderCreated, onCancel }) => {
  const [formData, setFormData] = useState({
    customerName: '',
    customerPhone: '',
    customerEmail: '',
    orderType: 'pickup',
    deliveryAddress: '',
    paymentMethod: 'cash'
  });

  const [createOrder, { loading }] = useMutation(CREATE_POS_ORDER, {
    onCompleted: (data) => {
      if (data.createPosOrder.success) {
        onOrderCreated(data.createPosOrder.order);
      }
    }
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Convert cart items to POS order format
    const items = cartItems.map(item => ({
      productId: item.productId,
      quantity: item.quantity,
      sizeId: item.sizeId || null,
      toppings: item.toppings || []
    }));

    createOrder({
      variables: {
        input: {
          ...formData,
          items
        }
      }
    });
  };

  return (
    <form onSubmit={handleSubmit} className="checkout-form">
      <h2>Checkout</h2>
      
      <div className="form-group">
        <label>Customer Name *</label>
        <input
          type="text"
          value={formData.customerName}
          onChange={(e) => setFormData({...formData, customerName: e.target.value})}
          required
        />
      </div>

      <div className="form-group">
        <label>Phone *</label>
        <input
          type="tel"
          value={formData.customerPhone}
          onChange={(e) => setFormData({...formData, customerPhone: e.target.value})}
          required
        />
      </div>

      <div className="form-group">
        <label>Email</label>
        <input
          type="email"
          value={formData.customerEmail}
          onChange={(e) => setFormData({...formData, customerEmail: e.target.value})}
        />
      </div>

      <div className="form-group">
        <label>Order Type *</label>
        <select
          value={formData.orderType}
          onChange={(e) => setFormData({...formData, orderType: e.target.value})}
        >
          <option value="pickup">Pickup</option>
          <option value="delivery">Delivery</option>
        </select>
      </div>

      {formData.orderType === 'delivery' && (
        <div className="form-group">
          <label>Delivery Address *</label>
          <textarea
            value={formData.deliveryAddress}
            onChange={(e) => setFormData({...formData, deliveryAddress: e.target.value})}
            required
          />
        </div>
      )}

      <div className="form-group">
        <label>Payment Method *</label>
        <select
          value={formData.paymentMethod}
          onChange={(e) => setFormData({...formData, paymentMethod: e.target.value})}
        >
          <option value="cash">Cash</option>
          <option value="card">Card</option>
          <option value="split">Split</option>
        </select>
      </div>

      <div className="checkout-actions">
        <button type="button" onClick={onCancel}>Cancel</button>
        <button type="submit" disabled={loading}>
          {loading ? 'Processing...' : 'Create Order'}
        </button>
      </div>
    </form>
  );
};

export default Checkout;
```

### **6. Main POS Interface**

```javascript
// pos/pages/POSMain.js
import React, { useState } from 'react';
import { useQuery } from '@apollo/client';
import BarcodeScanner from '../components/BarcodeScanner';
import ProductGrid from '../components/ProductGrid';
import Cart from '../components/Cart';
import Checkout from '../components/Checkout';
import Receipt from '../components/Receipt';
import { POS_PRODUCTS } from '../utils/graphql';

const POSMain = () => {
  const [cart, setCart] = useState([]);
  const [showCheckout, setShowCheckout] = useState(false);
  const [completedOrder, setCompletedOrder] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  const { data, loading, refetch } = useQuery(POS_PRODUCTS, {
    variables: { search: searchTerm }
  });

  const handleProductScanned = (product) => {
    addToCart(product);
  };

  const addToCart = (product) => {
    const existingItem = cart.find(item => item.productId === product.id);
    
    if (existingItem) {
      updateCartItem(existingItem.id, existingItem.quantity + 1);
    } else {
      setCart([...cart, {
        id: Date.now(),
        productId: product.id,
        productName: product.name,
        quantity: 1,
        unitPrice: parseFloat(product.currentPrice),
        stockQuantity: product.stockQuantity,
        isInStock: product.isInStock
      }]);
    }
  };

  const updateCartItem = (itemId, quantity) => {
    if (quantity <= 0) {
      removeCartItem(itemId);
    } else {
      setCart(cart.map(item =>
        item.id === itemId ? { ...item, quantity } : item
      ));
    }
  };

  const removeCartItem = (itemId) => {
    setCart(cart.filter(item => item.id !== itemId));
  };

  const clearCart = () => {
    setCart([]);
  };

  const subtotal = cart.reduce((sum, item) => sum + (item.unitPrice * item.quantity), 0);

  const handleOrderCreated = (order) => {
    setCompletedOrder(order);
    setShowCheckout(false);
    setCart([]);
  };

  const handlePrintReceipt = () => {
    // Print receipt logic
    window.print();
  };

  const handleNewOrder = () => {
    setCompletedOrder(null);
    setCart([]);
  };

  if (completedOrder) {
    return (
      <div className="pos-container">
        <Receipt orderId={completedOrder.id} onPrint={handlePrintReceipt} onNewOrder={handleNewOrder} />
      </div>
    );
  }

  return (
    <div className="pos-container">
      <div className="pos-header">
        <h1>Point of Sale</h1>
        <div className="pos-stats">
          {/* Today's stats can go here */}
        </div>
      </div>

      <div className="pos-main">
        <div className="pos-left">
          <BarcodeScanner onProductScanned={handleProductScanned} />
          
          <div className="search-bar">
            <input
              type="text"
              placeholder="Search products..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <ProductGrid
            products={data?.posProducts || []}
            onAddToCart={addToCart}
            loading={loading}
          />
        </div>

        <div className="pos-right">
          {showCheckout ? (
            <Checkout
              cartItems={cart}
              onOrderCreated={handleOrderCreated}
              onCancel={() => setShowCheckout(false)}
            />
          ) : (
            <Cart
              items={cart}
              onUpdateQuantity={updateCartItem}
              onRemoveItem={removeCartItem}
              onClear={clearCart}
              subtotal={subtotal}
            />
          )}

          {!showCheckout && cart.length > 0 && (
            <button
              className="checkout-btn"
              onClick={() => setShowCheckout(true)}
            >
              Checkout
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default POSMain;
```

---

## 🎨 CSS Styles (Touch-Optimized)

```css
/* pos/styles/pos.css */

.pos-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f5f5;
}

.pos-header {
  background: #2c3e50;
  color: white;
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pos-main {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.pos-left {
  flex: 2;
  padding: 1rem;
  overflow-y: auto;
}

.pos-right {
  flex: 1;
  background: white;
  border-left: 2px solid #ddd;
  padding: 1rem;
  display: flex;
  flex-direction: column;
}

/* Barcode Scanner */
.barcode-scanner {
  margin-bottom: 1rem;
}

.barcode-input {
  width: 100%;
  padding: 1rem;
  font-size: 1.5rem;
  border: 2px solid #3498db;
  border-radius: 8px;
}

/* Product Grid */
.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.product-card {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  cursor: pointer;
  transition: transform 0.2s;
}

.product-card:hover {
  transform: scale(1.05);
}

.product-card.out-of-stock {
  opacity: 0.5;
}

.product-card img {
  width: 100%;
  height: 150px;
  object-fit: cover;
  border-radius: 4px;
}

.add-to-cart-btn {
  width: 100%;
  padding: 0.75rem;
  font-size: 1.1rem;
  background: #27ae60;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 0.5rem;
  min-height: 48px; /* Touch-friendly */
}

.add-to-cart-btn:disabled {
  background: #95a5a6;
  cursor: not-allowed;
}

/* Cart */
.pos-cart {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.cart-items {
  flex: 1;
  overflow-y: auto;
  margin: 1rem 0;
}

.cart-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  border-bottom: 1px solid #eee;
}

.quantity-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.quantity-btn {
  width: 40px;
  height: 40px;
  font-size: 1.2rem;
  border: 1px solid #ddd;
  background: white;
  cursor: pointer;
  border-radius: 4px;
}

.checkout-btn {
  width: 100%;
  padding: 1rem;
  font-size: 1.2rem;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  margin-top: 1rem;
  min-height: 60px; /* Large touch target */
}

/* Touch-optimized buttons */
button {
  min-height: 44px; /* Minimum touch target size */
  min-width: 44px;
  font-size: 1rem;
}

/* Responsive for tablets */
@media (max-width: 1024px) {
  .pos-main {
    flex-direction: column;
  }
  
  .pos-left {
    flex: 1;
  }
  
  .pos-right {
    flex: 0 0 300px;
  }
}
```

---

## 🔌 Integration Steps

### **Option A: Add to Existing Dashboard**

1. **Create POS folder in your dashboard:**
```bash
cd your-frontend-project/src/dashboard
mkdir -p pages/pos components/pos
```

2. **Add POS route:**
```javascript
// In your dashboard routes
import POSMain from './pages/pos/POSMain';

<Route path="/dashboard/pos" element={<POSMain />} />
```

3. **Add POS link to dashboard menu:**
```javascript
<NavLink to="/dashboard/pos">Point of Sale</NavLink>
```

### **Option B: Separate POS App**

1. **Create new React app or module:**
```bash
# If separate app
npx create-react-app pos-frontend
cd pos-frontend

# Or create in existing project
mkdir -p src/pos
```

2. **Set up GraphQL client:**
```javascript
// Use same Apollo Client setup as dashboard
import { ApolloClient, InMemoryCache, createHttpLink } from '@apollo/client';

const httpLink = createHttpLink({
  uri: 'https://api.marinapizzas.com.au/graphql/',
  credentials: 'include' // For session-based auth
});

const client = new ApolloClient({
  link: httpLink,
  cache: new InMemoryCache()
});
```

---

## 🖨️ Receipt Printing

### **Browser Print API**

```javascript
// pos/utils/printer.js
export const printReceipt = (receiptData) => {
  const printWindow = window.open('', '_blank');
  
  printWindow.document.write(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>Receipt - ${receiptData.orderNumber}</title>
      <style>
        @media print {
          @page { size: 80mm auto; margin: 0; }
        }
        body {
          font-family: monospace;
          font-size: 12px;
          width: 80mm;
          padding: 10px;
        }
        .header { text-align: center; margin-bottom: 10px; }
        .item { margin: 5px 0; }
        .total { font-weight: bold; margin-top: 10px; border-top: 1px solid #000; padding-top: 5px; }
      </style>
    </head>
    <body>
      <div class="header">
        <h2>Marina Pizzas</h2>
        <p>Order: ${receiptData.orderNumber}</p>
        <p>${receiptData.date} ${receiptData.time}</p>
      </div>
      
      <div class="customer">
        <p><strong>${receiptData.customerName}</strong></p>
        <p>${receiptData.customerPhone}</p>
        ${receiptData.deliveryAddress ? `<p>${receiptData.deliveryAddress}</p>` : ''}
      </div>
      
      <div class="items">
        ${receiptData.items.map(item => `
          <div class="item">
            ${item.quantity}x ${item.productName} ${item.size ? `(${item.size})` : ''}
            $${item.subtotal.toFixed(2)}
          </div>
        `).join('')}
      </div>
      
      <div class="total">
        <p>Subtotal: $${receiptData.subtotal.toFixed(2)}</p>
        ${receiptData.deliveryFee > 0 ? `<p>Delivery: $${receiptData.deliveryFee.toFixed(2)}</p>` : ''}
        ${receiptData.discountAmount > 0 ? `<p>Discount: -$${receiptData.discountAmount.toFixed(2)}</p>` : ''}
        <p><strong>Total: $${receiptData.total.toFixed(2)}</strong></p>
        <p>Payment: ${receiptData.paymentMethod}</p>
      </div>
      
      <div class="footer" style="text-align: center; margin-top: 20px;">
        <p>Thank you for your order!</p>
      </div>
    </body>
    </html>
  `);
  
  printWindow.document.close();
  printWindow.print();
};
```

---

## 📱 Barcode Scanner Integration

### **How It Works:**

1. **USB Scanner Setup:**
   - Scanner works as "keyboard wedge"
   - Types barcode automatically when scanned
   - No special code needed!

2. **Implementation:**
```javascript
// Auto-focus on barcode input
useEffect(() => {
  barcodeInputRef.current?.focus();
}, []);

// Scanner types barcode → triggers onInput → calls GraphQL query
```

3. **Test Without Scanner:**
   - Just type barcode manually in input field
   - Works the same way

---

## 🎯 Next Steps

1. **Choose integration method** (separate app or dashboard section)
2. **Create POS folder structure**
3. **Set up GraphQL client** (reuse from dashboard)
4. **Build core components** (BarcodeScanner, ProductGrid, Cart, Checkout)
5. **Add POS route** to your app
6. **Style for touch** (large buttons, touch-friendly)
7. **Test with barcode scanner** (when hardware arrives)
8. **Add receipt printing**

---

## 📝 Quick Start Checklist

- [ ] Create POS folder/module in your React project
- [ ] Copy GraphQL queries from this guide
- [ ] Create BarcodeScanner component
- [ ] Create ProductGrid component
- [ ] Create Cart component
- [ ] Create Checkout component
- [ ] Create main POS page
- [ ] Add POS route
- [ ] Style for touch (min 44px buttons)
- [ ] Test with GraphQL API
- [ ] Add receipt printing
- [ ] Deploy to subdomain (pos.marinapizzas.com.au)

---

## 🚀 Deployment

### **Option 1: Same Domain**
- Deploy to: `https://marinapizzas.com.au/pos`
- Share authentication with dashboard

### **Option 2: Subdomain (Recommended)**
- Deploy to: `https://pos.marinapizzas.com.au`
- Separate deployment
- Can use same authentication

---

**Ready to start building!** 🎉

