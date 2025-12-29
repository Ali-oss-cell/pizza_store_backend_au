# 📋 Menu Population Instructions

This guide explains how to run the script to populate your database with all menu items from Marina Pizza & Pasta.

---

## 🚀 Quick Start

### On Your Server

1. **SSH into your server**:
   ```bash
   ssh root@your-droplet-ip
   ```

2. **Navigate to the project directory**:
   ```bash
   cd /var/www/pizza-store-backend/pizza_store
   ```

3. **Activate virtual environment**:
   ```bash
   source ../venv/bin/activate
   ```

4. **Run the script**:
   ```bash
   python populate_menu.py
   ```

---

## 📝 What the Script Does

The script will:

1. ✅ Create all categories (Meat Pizzas, Vegetarian Pizzas, etc.)
2. ✅ Create sizes for each category (Small, Large, Family)
3. ✅ Create all products with correct pricing
4. ✅ Set up size-based pricing (base price + modifiers)
5. ✅ Link products to their categories and sizes

---

## 📊 Menu Items Included

### Pizzas
- **Meat Pizzas**: 9 items (S $14, L $20, F $23)
- **Vegetarian Pizzas**: 5 items (S $14, L $20, F $23)
- **Chicken Pizzas**: 4 items (S $14, L $20, F $23)
- **Seafood Pizzas**: 3 items (S $14, L $20, F $23)
- **Traditional Pizzas**: 16 items (S $10, L $16, F $21)

### Other Items
- **Pasta**: 9 dishes ($15 each)
- **Chicken Parmas**: 3 items ($25 each, includes chips and salad)
- **Salads**: 3 items ($11-$15)
- **Sides**: 6 items ($5-$15)
- **Desserts**: 2 items (Nutella Pizza: S $10/L $15, Donut: $12)
- **Beverages**: 2 items (Can $2.5, 1.25L $6)

**Total**: ~65 products

---

## 🔄 Running the Script Again

The script is **idempotent** - you can run it multiple times safely:

- ✅ Existing products won't be duplicated
- ✅ Existing categories won't be recreated
- ⚠️ Product prices and descriptions will be updated if changed

---

## 🛠️ Troubleshooting

### Error: "No module named 'products'"

Make sure you're in the `pizza_store` directory:
```bash
cd /var/www/pizza-store-backend/pizza_store
```

### Error: "Permission denied"

Make sure you're using the virtual environment:
```bash
source ../venv/bin/activate
```

### Products not showing up

1. Check if script ran successfully (look for "Menu import complete!")
2. Verify in admin panel: `https://api.marinapizzas.com.au/admin/`
3. Check database connection

---

## ✅ Verification

After running the script:

1. **Check the output** - Should see:
   ```
   Menu import complete!
   Summary:
     Categories: 11
     Products: ~65
     Sizes: ~15
   ```

2. **Verify in Admin Panel**:
   - Go to: `https://api.marinapizzas.com.au/admin/products/product/`
   - You should see all products listed

3. **Test via GraphQL**:
   ```bash
   curl -X POST https://api.marinapizzas.com.au/graphql/ \
     -H "Content-Type: application/json" \
     -d '{"query": "{ products { id name basePrice category { name } } }"}'
   ```

---

## 📝 Notes

- **Size Pricing**: The script sets base_price to the smallest size, then calculates price_modifier for larger sizes
- **Single Price Items**: Items like pasta and salads don't have sizes - they use base_price only
- **Descriptions**: All product descriptions are included from your menu

---

## 🔧 Customization

To modify the script:

1. Edit `/var/www/pizza-store-backend/pizza_store/populate_menu.py`
2. Make your changes
3. Run the script again

---

**Last Updated**: 2024-12-29

