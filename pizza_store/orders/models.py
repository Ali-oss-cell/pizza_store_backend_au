# orders/models.py
from django.db import models
from decimal import Decimal
from products.models import Product, Size

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        PREPARING = 'preparing', 'Preparing'
        READY = 'ready', 'Ready'
        DELIVERED = 'delivered', 'Delivered'
        PICKED_UP = 'picked_up', 'Picked Up'
        CANCELLED = 'cancelled', 'Cancelled'
    
    class OrderType(models.TextChoices):
        DELIVERY = 'delivery', 'Delivery'
        PICKUP = 'pickup', 'Pickup'
    
    # Order identification
    order_number = models.CharField(max_length=20, unique=True)
    
    # Customer info (no login required)
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    
    # Order details
    order_type = models.CharField(max_length=10, choices=OrderType.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    order_notes = models.TextField(blank=True, help_text="Special instructions for the order")
    
    # Delivery address (if delivery)
    delivery_address = models.TextField(blank=True, null=True)
    delivery_instructions = models.TextField(blank=True)
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount_code = models.CharField(max_length=50, blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Optional: Link to cart (for reference)
    cart_session_key = models.CharField(max_length=40, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{self.order_number} - {self.customer_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    
    # Product snapshot (product might be deleted later)
    product_name = models.CharField(max_length=255)
    product_id = models.PositiveIntegerField()  # Store ID for reference
    
    # Combo info snapshot
    is_combo = models.BooleanField(default=False)
    included_items = models.JSONField(default=list)  # List of included item names
    
    # Size snapshot
    size_name = models.CharField(max_length=50, blank=True, null=True)
    size_id = models.PositiveIntegerField(null=True, blank=True)
    
    # Toppings snapshot (stored as JSON)
    selected_toppings = models.JSONField(default=list)
    
    # Pricing snapshot
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity}x {self.product_name} - Order #{self.order.order_number}"