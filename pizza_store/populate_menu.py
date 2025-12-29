#!/usr/bin/env python
"""
Script to populate the database with Marina Pizza & Pasta menu items
Run: python manage.py shell < populate_menu.py
Or: python populate_menu.py (if run from pizza_store directory)
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pizza_store.settings')
django.setup()

from decimal import Decimal
from products.models import Category, Product, Size, Ingredient, Topping
from django.utils.text import slugify

def get_or_create_category(name, description="", display_order=0):
    """Get or create a category"""
    category, created = Category.objects.get_or_create(
        name=name,
        defaults={
            'slug': slugify(name),
            'description': description,
            'display_order': display_order,
        }
    )
    if created:
        print(f"✓ Created category: {name}")
    return category

def get_or_create_size(category, name, display_order=0):
    """Get or create a size for a category"""
    size, created = Size.objects.get_or_create(
        category=category,
        name=name,
        defaults={'display_order': display_order}
    )
    if created:
        print(f"  ✓ Created size: {name}")
    return size

def get_or_create_ingredient(name):
    """Get or create an ingredient/topping"""
    ingredient, created = Ingredient.objects.get_or_create(
        name=name
    )
    return ingredient

def create_product(category, name, description, prices, sizes_dict, is_available=True):
    """Create a product with multiple sizes"""
    # Get base price (smallest size)
    if isinstance(prices, dict):
        base_price = Decimal(str(min(prices.values())))
    else:
        base_price = Decimal(str(prices))
        prices = {'Regular': prices}
    
    product, created = Product.objects.get_or_create(
        name=name,
        defaults={
            'category': category,
            'description': description,
            'base_price': base_price,
            'is_available': is_available,
            'slug': slugify(name),
        }
    )
    
    if created:
        print(f"  ✓ Created product: {name} (${base_price})")
    else:
        print(f"  - Product already exists: {name}")
        # Update if needed
        product.base_price = base_price
        product.description = description
        product.save()
    
    # Link sizes and set price modifiers
    if isinstance(prices, dict) and sizes_dict:
        product.available_sizes.clear()
        for size_name, price in prices.items():
            if size_name in sizes_dict:
                size = sizes_dict[size_name]
                # Calculate price modifier (difference from base price)
                price_modifier = Decimal(str(price)) - base_price
                size.price_modifier = price_modifier
                size.save()
                product.available_sizes.add(size)
    elif not sizes_dict:
        # No sizes for this product (single price)
        product.available_sizes.clear()
    
    return product

def parse_toppings(description):
    """Parse toppings from description text"""
    # Common separators
    separators = [', ', ' and ', ' with ', ' topped with ', ' in ']
    toppings = []
    
    # Remove common phrases
    text = description.lower()
    text = text.replace('topped with', '').replace('with', '').replace('in', '')
    
    # Split by common separators
    parts = []
    for sep in separators:
        if sep in text:
            parts = text.split(sep)
            break
    
    if not parts:
        parts = [text]
    
    # Clean up and extract ingredient names
    for part in parts:
        part = part.strip()
        # Remove common words
        for word in ['base', 'sauce', 'dressing', 'optional']:
            part = part.replace(word, '').strip()
        if part and len(part) > 2:
            toppings.append(part.title())
    
    return toppings

def main():
    print("=" * 60)
    print("Marina Pizza & Pasta - Menu Import")
    print("=" * 60)
    print()
    
    # Create Categories
    print("Creating categories...")
    meat_pizza_cat = get_or_create_category("Meat Pizzas", "Premium meat pizzas", 1)
    veg_pizza_cat = get_or_create_category("Vegetarian Pizzas", "Vegetarian options", 2)
    chicken_pizza_cat = get_or_create_category("Chicken Pizzas", "Chicken pizzas", 3)
    seafood_pizza_cat = get_or_create_category("Seafood Pizzas", "Seafood pizzas", 4)
    traditional_pizza_cat = get_or_create_category("Traditional Pizzas", "Classic pizzas", 5)
    pasta_cat = get_or_create_category("Pasta", "Pasta dishes", 6)
    parma_cat = get_or_create_category("Chicken Parmas", "Chicken parmigiana", 7)
    salad_cat = get_or_create_category("Salads", "Fresh salads", 8)
    sides_cat = get_or_create_category("Sides", "Side dishes", 9)
    dessert_cat = get_or_create_category("Dessert", "Desserts", 10)
    beverage_cat = get_or_create_category("Beverages", "Drinks", 11)
    print()
    
    # Create Sizes for Pizza categories
    print("Creating sizes...")
    pizza_sizes = {}
    for cat in [meat_pizza_cat, veg_pizza_cat, chicken_pizza_cat, seafood_pizza_cat, traditional_pizza_cat]:
        pizza_sizes[cat] = {
            'S': get_or_create_size(cat, 'Small', 1),
            'L': get_or_create_size(cat, 'Large', 2),
            'F': get_or_create_size(cat, 'Family', 3),
        }
    
    # Traditional pizza sizes (different prices)
    traditional_sizes = {
        'S': get_or_create_size(traditional_pizza_cat, 'Small', 1),
        'L': get_or_create_size(traditional_pizza_cat, 'Large', 2),
        'F': get_or_create_size(traditional_pizza_cat, 'Family', 3),
    }
    print()
    
    # MEAT PIZZAS
    print("Creating Meat Pizzas...")
    meat_pizzas = [
        ("Sundried Heat", "Hot salami, capsicum, Spanish onion, olives, sundried tomato, eggplant and cherry tomato", {'S': 14, 'L': 20, 'F': 23}),
        ("Aurora", "Hot salami, homemade meatballs, Spanish onion, cherry tomato and lemon wedge", {'S': 14, 'L': 20, 'F': 23}),
        ("Rock Star", "Hot salami, roasted capsicum, mushroom, anchovies, olives, feta and sundried tomato", {'S': 14, 'L': 20, 'F': 23}),
        ("Salami Supreme", "Hot Calabrese salami, pepperoni salami and olives", {'S': 14, 'L': 20, 'F': 23}),
        ("Prosciutto", "Prosciutto, bocconcini, cherry tomato, rocket, parmesan and Demi-glace", {'S': 14, 'L': 20, 'F': 23}),
        ("Chef's Special", "Shaved ham, hot salami, mushroom, Spanish onion, roasted capsicum, olives, feta and oregano", {'S': 14, 'L': 20, 'F': 23}),
        ("Lamb", "Marinated lamb, spinach, Spanish onion, roasted capsicum topped with tzatziki", {'S': 14, 'L': 20, 'F': 23}),
        ("Pumpkin Delight", "Pumpkin base, caramelized onion, pumpkin seeds, parmesan and pesto", {'S': 14, 'L': 20, 'F': 23}),
        ("Nacho's", "Salsa base, corn chips, roasted capsicum, Spanish onion, jalapenos and taco beef", {'S': 14, 'L': 20, 'F': 23}),
    ]
    
    for name, desc, prices in meat_pizzas:
        create_product(meat_pizza_cat, name, desc, prices, pizza_sizes[meat_pizza_cat])
    print()
    
    # VEGETARIAN PIZZAS
    print("Creating Vegetarian Pizzas...")
    veg_pizzas = [
        ("Queen Margherita", "Double cheese, cherry tomato, bocconcini topped with oregano", {'S': 14, 'L': 20, 'F': 23}),
        ("Wild Mushroom", "White sauce base, sautéed mushroom, Spanish onion, cherry tomato and topped with rocket", {'S': 14, 'L': 20, 'F': 23}),
        ("Mediterranean", "Spinach, mushroom, Spanish onion, olives, sundried tomato, cherry tomato and feta", {'S': 14, 'L': 20, 'F': 23}),
        ("Veggie Supreme", "Roasted capsicum, mushroom, artichokes, eggplant, Spanish onion, olives, cherry tomato and lemon wedge", {'S': 14, 'L': 20, 'F': 23}),
        ("Truffle", "Truffle base, mushroom, rosemary, bocconcini topped with rocket and truffle oil", {'S': 14, 'L': 20, 'F': 23}),
    ]
    
    for name, desc, prices in veg_pizzas:
        create_product(veg_pizza_cat, name, desc, prices, pizza_sizes[veg_pizza_cat])
    print()
    
    # CHICKEN PIZZAS
    print("Creating Chicken Pizzas...")
    chicken_pizzas = [
        ("Avocado Al Apollo", "Chicken breast, avocado, Spanish Onion and cherry tomato (sweet chilli optional)", {'S': 14, 'L': 20, 'F': 23}),
        ("Tandoori Chicken", "Tandoori marinated chicken, roasted capsicum, Spanish onion topped with seasoned yogurt", {'S': 14, 'L': 20, 'F': 23}),
        ("Peri Peri Chicken", "Chicken breast, Spanish onion, roasted capsicum topped with peri- peri sauce", {'S': 14, 'L': 20, 'F': 23}),
        ("Chicken Supreme", "Chicken breast, mushroom, roasted capsicum, Spanish onion and pineapple", {'S': 14, 'L': 20, 'F': 23}),
    ]
    
    for name, desc, prices in chicken_pizzas:
        create_product(chicken_pizza_cat, name, desc, prices, pizza_sizes[chicken_pizza_cat])
    print()
    
    # SEAFOOD PIZZAS
    print("Creating Seafood Pizzas...")
    seafood_pizzas = [
        ("Seafood Deluxe", "Mix of fresh seafood, anchovies, garlic and lemon wedge", {'S': 14, 'L': 20, 'F': 23}),
        ("Honey Glazed Prawn", "Marinated king prawns, bocconcini, garlic, herbs, cherry tomato and lemon wedge", {'S': 14, 'L': 20, 'F': 23}),
        ("Chilli Prawn", "Chilli prawns, spinach, roasted capsicum, Spanish onion and rocket on sweet chilli base", {'S': 14, 'L': 20, 'F': 23}),
    ]
    
    for name, desc, prices in seafood_pizzas:
        create_product(seafood_pizza_cat, name, desc, prices, pizza_sizes[seafood_pizza_cat])
    print()
    
    # TRADITIONAL PIZZAS
    print("Creating Traditional Pizzas...")
    traditional_pizzas = [
        ("Garlic", "Garlic, cheese and oregano", {'S': 10, 'L': 16, 'F': 21}),
        ("Margherita", "Tomato, mozzarella and oregano", {'S': 10, 'L': 16, 'F': 21}),
        ("Vegetarian", "Mushroom, capsicum, Spanish onion, oregano, olives and oregano", {'S': 10, 'L': 16, 'F': 21}),
        ("Napoletana", "Salami, olives, anchovies and garlic", {'S': 10, 'L': 16, 'F': 21}),
        ("Hawaiian", "Ham and pineapple with traditional pizza sauce", {'S': 10, 'L': 16, 'F': 21}),
        ("American", "Ham and hot salami with traditional pizza sauce and oregano", {'S': 10, 'L': 16, 'F': 21}),
        ("Pepperoni", "Mild salami with traditional pizza sauce and oregano", {'S': 10, 'L': 16, 'F': 21}),
        ("Mexican", "Hot salami, capsicum, Spanish onion, olives and oregano", {'S': 10, 'L': 16, 'F': 21}),
        ("Aussie", "Ham, bacon, Spanish onion and egg", {'S': 10, 'L': 16, 'F': 21}),
        ("Capricciosa", "Ham, mushroom and olives (anchovies optional)", {'S': 10, 'L': 16, 'F': 21}),
        ("Italian", "Hot salami, mushroom, olives and oregano", {'S': 10, 'L': 16, 'F': 21}),
        ("BBQ Chicken", "Chicken breast, pineapple and BBQ sauce", {'S': 10, 'L': 16, 'F': 21}),
        ("Meat Lovers", "Ham, hot salami, bacon and meatballs with BBQ sauce", {'S': 10, 'L': 16, 'F': 21}),
        ("Supreme", "Ham, salami, mushroom, Spanish onion, capsicum, pineapple, olives and oregano", {'S': 10, 'L': 16, 'F': 21}),
        ("House Special", "Hot salami, mushroom, Spanish onion, capsicum, feta and oregano", {'S': 10, 'L': 16, 'F': 21}),
        ("Marina Special", "Ham, mushroom, capsicum, anchovies and oregano", {'S': 10, 'L': 16, 'F': 21}),
    ]
    
    for name, desc, prices in traditional_pizzas:
        create_product(traditional_pizza_cat, name, desc, prices, traditional_sizes)
    print()
    
    # PASTA
    print("Creating Pasta dishes...")
    pasta_dishes = [
        ("Bolognese", "Traditional rich Napoli meat sauce and oregano", 15),
        ("Seafood Pasta", "Mixed seafood pan fried with garlic in Napoli sauce and lemon", 15),
        ("Red Hot", "Hot salami, capsicum, Spanish onion, olives and garlic in Napoli sauce", 15),
        ("Pesto Chicken", "Chicken, cherry tomato, olives, feta and pesto", 15),
        ("Pollo", "Chicken, mushroom, roasted capsicum and garlic in creamy white sauce", 15),
        ("Fungi", "Mushroom, bacon, chicken and garlic in creamy white sauce", 15),
        ("Carbonara", "Bacon, garlic, egg and parsley in creamy white sauce", 15),
        ("Chicken Avocado", "Chicken, mushroom and avocado in creamy white sauce", 15),
        ("Vegetarian Pasta", "Onion, roasted capsicum, mushroom and eggplant in Napoli sauce", 15),
    ]
    
    for name, desc, price in pasta_dishes:
        create_product(pasta_cat, name, desc, price, None)
    print()
    
    # CHICKEN PARMAS
    print("Creating Chicken Parmas...")
    parmas = [
        ("Parma", "Chicken breast schnitzel topped with Napoli sauce, shaved ham and mozzarella cheese (with chips and salad)", 25),
        ("Hawaiian Parma", "Chicken breast schnitzel topped with Napoli sauce, shaved ham, pineapple and mozzarella cheese (with chips and salad)", 25),
        ("Mexican Parma", "Chicken breast schnitzel topped with Napoli sauce, Spanish onion, roasted capsicum, jalapeno, and mozzarella cheese (with chips and salad)", 25),
    ]
    
    for name, desc, price in parmas:
        create_product(parma_cat, name, desc, price, None)
    print()
    
    # SALADS
    print("Creating Salads...")
    salads = [
        ("Garden Salad", "Mixed leaf salad with roasted capsicum, Spanish onion, cucumber and cherry tomato with French dressing", 11),
        ("Greek Salad", "Mixed leaves, roasted capsicum, Spanish onion, cucumber, cherry tomato, olives, feta and oregano with Greek dressing", 11),
        ("Chicken Salad", "Marinated chicken, mixed leaves, Spanish onion, cucumber, cherry tomato and avocado with Italian dressing", 15),
    ]
    
    for name, desc, price in salads:
        create_product(salad_cat, name, desc, price, None)
    print()
    
    # SIDES
    print("Creating Sides...")
    sides = [
        ("Chips", "Chips with tomato sauce", 7),
        ("Garlic Bread", "Garlic bread", 5),
        ("Potato Wedges", "Potato wedges with sour cream and sweet chilli sauce", 10),
        ("Mozzarella Sticks", "Mozzarella sticks with tomato sauce", 10),
        ("Calamari", "Calamari with tartare sauce, chips and lemon wedges", 15),
        ("Onion Rings", "Onion rings with aioli sauce and chips", 11),
    ]
    
    for name, desc, price in sides:
        create_product(sides_cat, name, desc, price, None)
    print()
    
    # DESSERT
    print("Creating Desserts...")
    desserts = [
        ("Nutella Pizza", "Nutella, fresh strawberries and icing sugar", {'S': 10, 'L': 15}),
        ("Donut", "Jam donut with cinnamon", 12),
    ]
    
    # Create sizes for dessert category
    dessert_sizes = {
        'S': get_or_create_size(dessert_cat, 'Small', 1),
        'L': get_or_create_size(dessert_cat, 'Large', 2),
    }
    
    for name, desc, prices in desserts:
        if isinstance(prices, dict):
            create_product(dessert_cat, name, desc, prices, dessert_sizes)
        else:
            create_product(dessert_cat, name, desc, prices, None)
    print()
    
    # BEVERAGES
    print("Creating Beverages...")
    beverages = [
        ("Soft Drink Can", "Soft drink can", 2.5),
        ("Soft Drink 1.25L", "Soft drink 1.25L bottle", 6),
    ]
    
    for name, desc, price in beverages:
        create_product(beverage_cat, name, desc, price, None)
    print()
    
    print("=" * 60)
    print("Menu import complete!")
    print("=" * 60)
    print()
    print("Summary:")
    print(f"  Categories: {Category.objects.count()}")
    print(f"  Products: {Product.objects.count()}")
    print(f"  Sizes: {Size.objects.count()}")
    print()
    print("You can now view products in the admin panel:")
    print("  https://api.marinapizzas.com.au/admin/")

if __name__ == '__main__':
    main()

