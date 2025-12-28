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
    
    def calculate_discount(self, order_subtotal, delivery_fee=Decimal('0.00')):
        """Calculate the discount amount for an order"""
        if not self.is_valid:
            return Decimal('0.00')
        
        # Check minimum order amount
        if self.minimum_order_amount and order_subtotal < self.minimum_order_amount:
            return Decimal('0.00')
        
        if self.discount_type == self.DiscountType.PERCENTAGE:
            discount = order_subtotal * (self.discount_value / Decimal('100'))
            if self.maximum_discount:
                discount = min(discount, self.maximum_discount)
            return discount
        
        elif self.discount_type == self.DiscountType.FIXED:
            return min(self.discount_value, order_subtotal)
        
        elif self.discount_type == self.DiscountType.FREE_DELIVERY:
            return delivery_fee
        
        return Decimal('0.00')
