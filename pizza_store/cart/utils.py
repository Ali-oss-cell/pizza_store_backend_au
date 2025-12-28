"""
Helper functions for cart operations
"""
from .models import Cart, CartItem
from products.models import Product, Size, Topping
from decimal import Decimal


def get_or_create_cart(request):
    """
    Get cart from session or create new one
    Returns: Cart object
    """
    # Ensure session exists
    if not request.session.session_key:
        request.session.create()
    
    session_key = request.session.session_key
    
    # Get or create cart
    cart, created = Cart.objects.get_or_create(session_key=session_key)
    
    return cart


def get_cart_from_request(request):
    """
    Helper to get cart from request (returns None if doesn't exist)
    Returns: Cart object or None
    """
    if not request.session.session_key:
        return None
    
    try:
        cart = Cart.objects.get(session_key=request.session.session_key)
        return cart
    except Cart.DoesNotExist:
        return None


def calculate_item_price(product, size=None, toppings=None):
    """
    Calculate price for a cart item with size and toppings
    Args:
        product: Product object
        size: Size object (optional)
        toppings: List of topping dicts with 'id' and 'price' keys (optional)
    Returns: Decimal price
    """
    # Start with base price
    price = product.base_price
    
    # Add size modifier if size is provided
    if size:
        # Verify size is available for this product
        if size in product.available_sizes.all():
            price += size.price_modifier
    
    # Add toppings prices
    if toppings:
        for topping_data in toppings:
            # If topping_data is a dict with 'price' key
            if isinstance(topping_data, dict) and 'price' in topping_data:
                # Convert price to Decimal (handles both string and numeric)
                price += Decimal(str(topping_data['price']))
            # If topping_data is a Topping object
            elif isinstance(topping_data, Topping):
                # Verify topping is available for this product
                if topping_data in product.available_toppings.all():
                    price += Decimal(str(topping_data.price))
    
    return price


def format_toppings_for_storage(toppings_input):
    """
    Format toppings input for JSON storage
    Converts list of IDs or dicts to standardized format
    Args:
        toppings_input: List of topping IDs or dicts with 'id' and 'price'
    Returns: List of dicts with 'id', 'name', 'price'
    """
    formatted_toppings = []
    
    if not toppings_input:
        return formatted_toppings
    
    for topping_input in toppings_input:
        if isinstance(topping_input, dict):
            # Already formatted, but ensure it has all fields
            topping_id = topping_input.get('id')
            if topping_id:
                try:
                    topping = Topping.objects.get(pk=topping_id)
                    formatted_toppings.append({
                        'id': str(topping.id),
                        'name': topping.name,
                        'price': str(topping.price)  # Store as string for JSON compatibility
                    })
                except Topping.DoesNotExist:
                    continue
        elif isinstance(topping_input, (int, str)):
            # Just an ID, fetch the topping
            try:
                topping = Topping.objects.get(pk=topping_input)
                formatted_toppings.append({
                    'id': str(topping.id),
                    'name': topping.name,
                    'price': str(topping.price)  # Store as string for JSON compatibility
                })
            except Topping.DoesNotExist:
                continue
    
    return formatted_toppings