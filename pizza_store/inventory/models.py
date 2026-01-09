# inventory/models.py
from django.db import models
from django.core.validators import MinValueValidator
from products.models import Product
from accounts.models import User


class StockItem(models.Model):
    """Tracks inventory for a product"""
    product = models.OneToOneField(
        Product, 
        on_delete=models.CASCADE, 
        related_name='stock',
        help_text="Product this stock item belongs to"
    )
    quantity = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Current stock quantity"
    )
    reorder_level = models.PositiveIntegerField(
        default=10,
        validators=[MinValueValidator(0)],
        help_text="Alert when stock falls below this level"
    )
    reorder_quantity = models.PositiveIntegerField(
        default=50,
        validators=[MinValueValidator(1)],
        help_text="Quantity to order when restocking"
    )
    last_restocked = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['product__name']
        verbose_name = "Stock Item"
        verbose_name_plural = "Stock Items"
    
    def __str__(self):
        return f"{self.product.name} - {self.quantity} in stock"
    
    @property
    def is_low_stock(self):
        """Check if stock is below reorder level"""
        return self.quantity <= self.reorder_level
    
    @property
    def is_out_of_stock(self):
        """Check if product is out of stock"""
        return self.quantity == 0


class StockMovement(models.Model):
    """Tracks all stock changes (sales, adjustments, receipts, etc.)"""
    
    class MovementType(models.TextChoices):
        SALE = 'sale', 'Sale'
        ADJUSTMENT = 'adjustment', 'Manual Adjustment'
        RECEIPT = 'receipt', 'Stock Receipt'
        RETURN = 'return', 'Return/Refund'
        DAMAGED = 'damaged', 'Damaged/Expired'
        TRANSFER = 'transfer', 'Transfer'
    
    stock_item = models.ForeignKey(
        StockItem, 
        on_delete=models.CASCADE, 
        related_name='movements',
        help_text="Stock item this movement affects"
    )
    movement_type = models.CharField(
        max_length=20, 
        choices=MovementType.choices,
        help_text="Type of stock movement"
    )
    quantity_change = models.IntegerField(
        help_text="Change in quantity (positive for increase, negative for decrease)"
    )
    quantity_before = models.PositiveIntegerField(
        help_text="Stock quantity before this movement"
    )
    quantity_after = models.PositiveIntegerField(
        help_text="Stock quantity after this movement"
    )
    reference = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Reference number (e.g., order number, adjustment ID)"
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about this movement"
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        related_name='stock_movements',
        help_text="User who created this movement"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Stock Movement"
        verbose_name_plural = "Stock Movements"
    
    def __str__(self):
        return f"{self.stock_item.product.name} - {self.movement_type} ({self.quantity_change:+d})"


class StockAlert(models.Model):
    """Alerts for low stock items"""
    
    class AlertStatus(models.TextChoices):
        ACTIVE = 'active', 'Active'
        ACKNOWLEDGED = 'acknowledged', 'Acknowledged'
        RESOLVED = 'resolved', 'Resolved'
    
    stock_item = models.ForeignKey(
        StockItem,
        on_delete=models.CASCADE,
        related_name='alerts',
        help_text="Stock item with low stock"
    )
    status = models.CharField(
        max_length=20,
        choices=AlertStatus.choices,
        default=AlertStatus.ACTIVE,
        help_text="Alert status"
    )
    message = models.TextField(
        help_text="Alert message"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Stock Alert"
        verbose_name_plural = "Stock Alerts"
    
    def __str__(self):
        return f"Alert: {self.stock_item.product.name} - {self.status}"
