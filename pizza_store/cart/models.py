# cart/models.py
from django.db import models
from decimal import Decimal
from products.models import Product, Size, Topping

class Cart(models.Model):
    session_key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_total(self):
        """Calculate total cart price"""
        total = sum(item.get_subtotal() for item in self.items.all())
        return total if total else Decimal('0.00')
    
    def __str__(self):
        return f"Cart ({self.session_key[:8]}...) - {self.items.count()} items"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    selected_toppings = models.JSONField(default=list)  # Store toppings as list of dicts
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)  # Snapshot price
    
    # Combo option: allows customer to choose if they want included items
    include_combo_items = models.BooleanField(
        default=False,
        help_text="If True, includes combo items (chips, salad, etc.) with this product"
    )
    # Snapshot of included items at time of adding to cart
    selected_included_items = models.JSONField(
        default=list,
        help_text="Snapshot of included item names when combo option is selected"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']  # Newest items first
    
    def get_subtotal(self):
        """Calculate subtotal for this item"""
        # Convert all prices to Decimal for proper calculation
        toppings_total = sum(
            Decimal(str(t.get('price', 0))) for t in self.selected_toppings
        )
        return (self.unit_price + toppings_total) * Decimal(self.quantity)
    
    @property
    def is_combo_order(self):
        """Check if this cart item includes combo items"""
        return self.include_combo_items and self.product.is_combo
    
    def __str__(self):
        combo_label = " (Combo)" if self.is_combo_order else ""
        return f"{self.quantity}x {self.product.name}{combo_label} - ${self.get_subtotal()}"