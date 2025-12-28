# orders/utils.py
import random
import string
from datetime import datetime
from decimal import Decimal
from .models import Order, OrderItem
from cart.models import Cart

def generate_order_number():
    """Generate unique order number"""
    # Format: ORD-YYYYMMDD-XXXX (e.g., ORD-20251208-A3B7)
    date_str = datetime.now().strftime('%Y%m%d')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    order_number = f"ORD-{date_str}-{random_str}"
    
    # Ensure uniqueness
    while Order.objects.filter(order_number=order_number).exists():
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        order_number = f"ORD-{date_str}-{random_str}"
    
    return order_number