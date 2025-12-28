from django.db import models
from decimal import Decimal


class StoreSettings(models.Model):
    """Store configuration settings (singleton model)"""
    
    # Store Info
    store_name = models.CharField(max_length=255, default="Marina Pizza & Pasta")
    store_phone = models.CharField(max_length=20, default="")
    store_email = models.EmailField(default="")
    store_address = models.TextField(default="")
    
    # Business Hours (JSON field for flexibility)
    business_hours = models.JSONField(default=dict, help_text="Store hours by day")
    
    # Delivery Settings
    delivery_enabled = models.BooleanField(default=True)
    pickup_enabled = models.BooleanField(default=True)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('5.00'))
    free_delivery_threshold = models.DecimalField(
        max_digits=10, decimal_places=2, 
        default=Decimal('50.00'),
        help_text="Free delivery for orders over this amount"
    )
    minimum_order_amount = models.DecimalField(
        max_digits=10, decimal_places=2, 
        default=Decimal('15.00')
    )
    delivery_radius_km = models.DecimalField(
        max_digits=5, decimal_places=2, 
        default=Decimal('10.00')
    )
    estimated_delivery_time = models.PositiveIntegerField(
        default=45,
        help_text="Estimated delivery time in minutes"
    )
    estimated_pickup_time = models.PositiveIntegerField(
        default=20,
        help_text="Estimated pickup time in minutes"
    )
    
    # Tax Settings
    tax_rate = models.DecimalField(
        max_digits=5, decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Tax rate as percentage (e.g., 10 for 10%)"
    )
    tax_included_in_prices = models.BooleanField(default=True)
    
    # Order Settings
    accept_orders = models.BooleanField(default=True, help_text="Master switch for accepting orders")
    order_notes_enabled = models.BooleanField(default=True)
    
    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Store Settings"
        verbose_name_plural = "Store Settings"
    
    def __str__(self):
        return self.store_name
    
    def save(self, *args, **kwargs):
        """Ensure only one instance exists"""
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get or create the singleton settings instance"""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Promotion(models.Model):
    """Promotions and discount codes"""
    
    class DiscountType(models.TextChoices):
        PERCENTAGE = 'percentage', 'Percentage'
        FIXED = 'fixed', 'Fixed Amount'
        FREE_DELIVERY = 'free_delivery', 'Free Delivery'
    
    # Basic Info
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Discount Details
    discount_type = models.CharField(max_length=20, choices=DiscountType.choices)
    discount_value = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Percentage (e.g., 10 for 10%) or fixed amount"
    )
    
    # Product-Specific Discount Settings
    applicable_products = models.ManyToManyField(
        'products.Product',
        blank=True,
        related_name='promotions',
        help_text="Specific products this promotion applies to. Leave empty to apply to all products."
    )
    apply_to_base_price = models.BooleanField(
        default=True,
        help_text="Apply discount to product base price"
    )
    apply_to_toppings = models.BooleanField(
        default=False,
        help_text="Apply discount to toppings/add-ons"
    )
    apply_to_included_items = models.BooleanField(
        default=False,
        help_text="Apply discount to included items (e.g., chips, salad in combos)"
    )
    apply_to_entire_order = models.BooleanField(
        default=True,
        help_text="If True, applies to entire order. If False, only applies to selected products."
    )
    
    # Conditions
    minimum_order_amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        help_text="Minimum order amount to apply this promotion"
    )
    maximum_discount = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        help_text="Maximum discount amount (for percentage discounts)"
    )
    
    # Usage Limits
    usage_limit = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Total number of times this code can be used"
    )
    times_used = models.PositiveIntegerField(default=0)
    
    # Validity
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def is_valid(self):
        """Check if promotion is currently valid"""
        from django.utils import timezone
        now = timezone.now()
        
        if not self.is_active:
            return False
        if now < self.valid_from or now > self.valid_until:
            return False
        if self.usage_limit and self.times_used >= self.usage_limit:
            return False
        return True
    
    def calculate_discount(self, order_subtotal, delivery_fee=Decimal('0.00'), order_items=None):
        """
        Calculate the discount amount for an order.
        
        Args:
            order_subtotal: Total order subtotal
            delivery_fee: Delivery fee amount
            order_items: List of OrderItem objects (optional, for product-specific discounts)
        
        Returns:
            Decimal: Discount amount
        """
        if not self.is_valid:
            return Decimal('0.00')
        
        # Check minimum order amount
        if self.minimum_order_amount and order_subtotal < self.minimum_order_amount:
            return Decimal('0.00')
        
        # Free delivery discount
        if self.discount_type == self.DiscountType.FREE_DELIVERY:
            return delivery_fee
        
        # Product-specific discount calculation
        if order_items and not self.apply_to_entire_order:
            # Only apply to selected products
            applicable_product_ids = set(self.applicable_products.values_list('id', flat=True))
            if not applicable_product_ids:
                # If no products selected, apply to all (fallback)
                discountable_amount = order_subtotal
            else:
                # Calculate discount only on applicable products
                discountable_amount = Decimal('0.00')
                for item in order_items:
                    if item.product_id in applicable_product_ids:
                        item_discountable = Decimal('0.00')
                        
                        # Base price
                        if self.apply_to_base_price:
                            # Use unit_price per item (already includes size modifier)
                            base_price = item.unit_price
                            item_discountable += base_price * item.quantity
                        
                        # Toppings
                        if self.apply_to_toppings and item.selected_toppings:
                            for topping in item.selected_toppings:
                                if isinstance(topping, dict) and 'price' in topping:
                                    item_discountable += Decimal(str(topping['price'])) * item.quantity
                        
                        # Included items (for combos)
                        if self.apply_to_included_items and item.is_combo:
                            # Included items are typically free, but if they have prices, add here
                            pass
                        
                        discountable_amount += item_discountable
        else:
            # Apply to entire order
            discountable_amount = order_subtotal
        
        # Calculate discount based on type
        if self.discount_type == self.DiscountType.PERCENTAGE:
            discount = discountable_amount * (self.discount_value / Decimal('100'))
            if self.maximum_discount:
                discount = min(discount, self.maximum_discount)
            return discount
        
        elif self.discount_type == self.DiscountType.FIXED:
            return min(self.discount_value, discountable_amount)
        
        return Decimal('0.00')
