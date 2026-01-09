# inventory/utils.py
from django.db import transaction
from django.utils import timezone
from .models import StockItem, StockMovement, StockAlert
from products.models import Product


def get_or_create_stock_item(product):
    """Get or create a StockItem for a product"""
    if not product.track_inventory:
        return None
    
    stock_item, created = StockItem.objects.get_or_create(
        product=product,
        defaults={
            'quantity': 0,
            'reorder_level': product.reorder_level,
            'reorder_quantity': 50,
        }
    )
    return stock_item


def adjust_stock(product, quantity_change, movement_type, reference='', notes='', user=None):
    """
    Adjust stock for a product
    
    Args:
        product: Product instance
        quantity_change: Integer (positive for increase, negative for decrease)
        movement_type: StockMovement.MovementType choice
        reference: Reference string (e.g., order number)
        notes: Additional notes
        user: User who made the change (optional)
    
    Returns:
        StockMovement instance or None
    """
    if not product.track_inventory:
        return None
    
    with transaction.atomic():
        stock_item = get_or_create_stock_item(product)
        if not stock_item:
            return None
        
        quantity_before = stock_item.quantity
        quantity_after = max(0, quantity_before + quantity_change)  # Ensure non-negative
        
        # Create movement record
        movement = StockMovement.objects.create(
            stock_item=stock_item,
            movement_type=movement_type,
            quantity_change=quantity_change,
            quantity_before=quantity_before,
            quantity_after=quantity_after,
            reference=reference,
            notes=notes,
            created_by=user
        )
        
        # Update stock quantity
        stock_item.quantity = quantity_after
        stock_item.updated_at = timezone.now()
        
        # Update last_restocked if receiving stock
        if movement_type == StockMovement.MovementType.RECEIPT:
            stock_item.last_restocked = timezone.now()
        
        stock_item.save()
        
        # Check for low stock and create alert if needed
        check_low_stock(stock_item)
        
        return movement


def sell_stock(product, quantity, order_number='', user=None):
    """Deduct stock when a product is sold"""
    return adjust_stock(
        product=product,
        quantity_change=-quantity,
        movement_type=StockMovement.MovementType.SALE,
        reference=order_number,
        notes=f'Sold {quantity} units',
        user=user
    )


def receive_stock(product, quantity, notes='', user=None):
    """Add stock when receiving from supplier"""
    return adjust_stock(
        product=product,
        quantity_change=quantity,
        movement_type=StockMovement.MovementType.RECEIPT,
        reference='',
        notes=notes or f'Received {quantity} units',
        user=user
    )


def return_stock(product, quantity, reference='', notes='', user=None):
    """Return stock (e.g., customer return)"""
    return adjust_stock(
        product=product,
        quantity_change=quantity,
        movement_type=StockMovement.MovementType.RETURN,
        reference=reference,
        notes=notes or f'Returned {quantity} units',
        user=user
    )


def check_low_stock(stock_item):
    """Check if stock is low and create alert if needed"""
    if stock_item.is_low_stock:
        # Check if there's already an active alert
        existing_alert = StockAlert.objects.filter(
            stock_item=stock_item,
            status=StockAlert.AlertStatus.ACTIVE
        ).first()
        
        if not existing_alert:
            # Create new alert
            StockAlert.objects.create(
                stock_item=stock_item,
                status=StockAlert.AlertStatus.ACTIVE,
                message=f"{stock_item.product.name} has low stock ({stock_item.quantity} units remaining). Reorder level: {stock_item.reorder_level}"
            )
    else:
        # Resolve any active alerts if stock is now above reorder level
        StockAlert.objects.filter(
            stock_item=stock_item,
            status=StockAlert.AlertStatus.ACTIVE
        ).update(
            status=StockAlert.AlertStatus.RESOLVED,
            resolved_at=timezone.now()
        )


def get_low_stock_items():
    """Get all products with low stock"""
    from django.db.models import F
    return StockItem.objects.filter(
        quantity__lte=F('reorder_level')
    ).select_related('product')


def get_out_of_stock_items():
    """Get all products that are out of stock"""
    return StockItem.objects.filter(quantity=0).select_related('product')

