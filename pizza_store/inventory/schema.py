# inventory/schema.py
import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from django.db.models import Q
from decimal import Decimal as D

from .models import StockItem, StockMovement, StockAlert
from products.models import Product
from accounts.models import User
from .utils import (
    adjust_stock, sell_stock, receive_stock, return_stock,
    get_low_stock_items, get_out_of_stock_items, get_or_create_stock_item
)


# GraphQL Types
class StockItemType(DjangoObjectType):
    """Stock item GraphQL type"""
    is_low_stock = graphene.Boolean()
    is_out_of_stock = graphene.Boolean()
    
    class Meta:
        model = StockItem
        fields = (
            'id', 'product', 'quantity', 'reorder_level', 
            'reorder_quantity', 'last_restocked', 'created_at', 'updated_at'
        )
    
    def resolve_is_low_stock(self, info):
        return self.is_low_stock
    
    def resolve_is_out_of_stock(self, info):
        return self.is_out_of_stock


class StockMovementType(DjangoObjectType):
    """Stock movement GraphQL type"""
    
    class Meta:
        model = StockMovement
        fields = (
            'id', 'stock_item', 'movement_type', 'quantity_change',
            'quantity_before', 'quantity_after', 'reference', 'notes',
            'created_by', 'created_at'
        )


class StockAlertType(DjangoObjectType):
    """Stock alert GraphQL type"""
    
    class Meta:
        model = StockAlert
        fields = (
            'id', 'stock_item', 'status', 'message',
            'created_at', 'acknowledged_at', 'resolved_at'
        )


# Input Types
class AdjustStockInput(graphene.InputObjectType):
    """Input for adjusting stock"""
    product_id = graphene.ID(required=True)
    quantity_change = graphene.Int(required=True, description="Positive for increase, negative for decrease")
    movement_type = graphene.String(required=True)
    reference = graphene.String()
    notes = graphene.String()


class ReceiveStockInput(graphene.InputObjectType):
    """Input for receiving stock"""
    product_id = graphene.ID(required=True)
    quantity = graphene.Int(required=True)
    notes = graphene.String()


class ReturnStockInput(graphene.InputObjectType):
    """Input for returning stock"""
    product_id = graphene.ID(required=True)
    quantity = graphene.Int(required=True)
    reference = graphene.String()
    notes = graphene.String()


# Queries
class InventoryQuery(graphene.ObjectType):
    """Inventory GraphQL queries"""
    
    # Stock Items
    all_stock_items = graphene.List(StockItemType)
    stock_item = graphene.Field(StockItemType, id=graphene.ID())
    stock_item_by_product = graphene.Field(StockItemType, product_id=graphene.ID())
    
    # Low Stock
    low_stock_items = graphene.List(StockItemType)
    out_of_stock_items = graphene.List(StockItemType)
    
    # Stock Movements
    all_stock_movements = graphene.List(StockMovementType)
    stock_movements_by_product = graphene.List(
        StockMovementType,
        product_id=graphene.ID(required=True)
    )
    
    # Stock Alerts
    all_stock_alerts = graphene.List(StockAlertType)
    active_stock_alerts = graphene.List(StockAlertType)
    
    # Product by barcode
    product_by_barcode = graphene.Field(
        'products.schema.ProductType',
        barcode=graphene.String(required=True)
    )
    
    # Product by SKU
    product_by_sku = graphene.Field(
        'products.schema.ProductType',
        sku=graphene.String(required=True)
    )
    
    def resolve_all_stock_items(self, info):
        """Get all stock items"""
        return StockItem.objects.all()
    
    def resolve_stock_item(self, info, id):
        """Get single stock item by ID"""
        return StockItem.objects.get(id=id)
    
    def resolve_stock_item_by_product(self, info, product_id):
        """Get stock item for a specific product"""
        try:
            product = Product.objects.get(id=product_id)
            if not product.track_inventory:
                return None
            return get_or_create_stock_item(product)
        except Product.DoesNotExist:
            return None
    
    def resolve_low_stock_items(self, info):
        """Get all products with low stock"""
        return get_low_stock_items()
    
    def resolve_out_of_stock_items(self, info):
        """Get all products that are out of stock"""
        return get_out_of_stock_items()
    
    def resolve_all_stock_movements(self, info):
        """Get all stock movements"""
        return StockMovement.objects.all()
    
    def resolve_stock_movements_by_product(self, info, product_id):
        """Get stock movements for a specific product"""
        try:
            product = Product.objects.get(id=product_id)
            if not product.track_inventory:
                return StockMovement.objects.none()
            stock_item = get_or_create_stock_item(product)
            if stock_item:
                return StockMovement.objects.filter(stock_item=stock_item)
            return StockMovement.objects.none()
        except Product.DoesNotExist:
            return StockMovement.objects.none()
    
    def resolve_all_stock_alerts(self, info):
        """Get all stock alerts"""
        return StockAlert.objects.all()
    
    def resolve_active_stock_alerts(self, info):
        """Get all active stock alerts"""
        return StockAlert.objects.filter(status=StockAlert.AlertStatus.ACTIVE)
    
    def resolve_product_by_barcode(self, info, barcode):
        """Find product by barcode"""
        try:
            return Product.objects.get(barcode=barcode)
        except Product.DoesNotExist:
            return None
    
    def resolve_product_by_sku(self, info, sku):
        """Find product by SKU"""
        try:
            return Product.objects.get(sku=sku)
        except Product.DoesNotExist:
            return None


# Mutations
class AdjustStock(graphene.Mutation):
    """Manually adjust stock (increase or decrease)"""
    
    class Arguments:
        input = AdjustStockInput(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    stock_movement = graphene.Field(StockMovementType)
    stock_item = graphene.Field(StockItemType)
    
    @staticmethod
    def mutate(root, info, input):
        user = info.context.user if info.context.user.is_authenticated else None
        
        # Check permissions (admin or staff only)
        if not user or not (user.is_staff or user.is_superuser):
            raise GraphQLError("Permission denied. Admin or staff access required.")
        
        try:
            product = Product.objects.get(id=input['product_id'])
        except Product.DoesNotExist:
            raise GraphQLError("Product not found")
        
        if not product.track_inventory:
            raise GraphQLError("This product does not track inventory")
        
        # Validate movement type
        valid_types = [choice[0] for choice in StockMovement.MovementType.choices]
        if input['movement_type'] not in valid_types:
            raise GraphQLError(f"Invalid movement type. Must be one of: {', '.join(valid_types)}")
        
        movement = adjust_stock(
            product=product,
            quantity_change=input['quantity_change'],
            movement_type=input['movement_type'],
            reference=input.get('reference', ''),
            notes=input.get('notes', ''),
            user=user
        )
        
        if movement:
            stock_item = movement.stock_item
            return AdjustStock(
                success=True,
                message=f"Stock adjusted successfully. New quantity: {stock_item.quantity}",
                stock_movement=movement,
                stock_item=stock_item
            )
        else:
            raise GraphQLError("Failed to adjust stock")


class ReceiveStock(graphene.Mutation):
    """Receive stock from supplier"""
    
    class Arguments:
        input = ReceiveStockInput(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    stock_movement = graphene.Field(StockMovementType)
    stock_item = graphene.Field(StockItemType)
    
    @staticmethod
    def mutate(root, info, input):
        user = info.context.user if info.context.user.is_authenticated else None
        
        # Check permissions
        if not user or not (user.is_staff or user.is_superuser):
            raise GraphQLError("Permission denied. Admin or staff access required.")
        
        try:
            product = Product.objects.get(id=input['product_id'])
        except Product.DoesNotExist:
            raise GraphQLError("Product not found")
        
        if not product.track_inventory:
            raise GraphQLError("This product does not track inventory")
        
        if input['quantity'] <= 0:
            raise GraphQLError("Quantity must be greater than 0")
        
        movement = receive_stock(
            product=product,
            quantity=input['quantity'],
            notes=input.get('notes', ''),
            user=user
        )
        
        if movement:
            stock_item = movement.stock_item
            return ReceiveStock(
                success=True,
                message=f"Stock received successfully. New quantity: {stock_item.quantity}",
                stock_movement=movement,
                stock_item=stock_item
            )
        else:
            raise GraphQLError("Failed to receive stock")


class ReturnStock(graphene.Mutation):
    """Return stock (e.g., customer return)"""
    
    class Arguments:
        input = ReturnStockInput(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    stock_movement = graphene.Field(StockMovementType)
    stock_item = graphene.Field(StockItemType)
    
    @staticmethod
    def mutate(root, info, input):
        user = info.context.user if info.context.user.is_authenticated else None
        
        # Check permissions
        if not user or not (user.is_staff or user.is_superuser):
            raise GraphQLError("Permission denied. Admin or staff access required.")
        
        try:
            product = Product.objects.get(id=input['product_id'])
        except Product.DoesNotExist:
            raise GraphQLError("Product not found")
        
        if not product.track_inventory:
            raise GraphQLError("This product does not track inventory")
        
        if input['quantity'] <= 0:
            raise GraphQLError("Quantity must be greater than 0")
        
        movement = return_stock(
            product=product,
            quantity=input['quantity'],
            reference=input.get('reference', ''),
            notes=input.get('notes', ''),
            user=user
        )
        
        if movement:
            stock_item = movement.stock_item
            return ReturnStock(
                success=True,
                message=f"Stock returned successfully. New quantity: {stock_item.quantity}",
                stock_movement=movement,
                stock_item=stock_item
            )
        else:
            raise GraphQLError("Failed to return stock")


class AcknowledgeStockAlert(graphene.Mutation):
    """Acknowledge a stock alert"""
    
    class Arguments:
        alert_id = graphene.ID(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    alert = graphene.Field(StockAlertType)
    
    @staticmethod
    def mutate(root, info, alert_id):
        user = info.context.user if info.context.user.is_authenticated else None
        
        # Check permissions
        if not user or not (user.is_staff or user.is_superuser):
            raise GraphQLError("Permission denied. Admin or staff access required.")
        
        try:
            alert = StockAlert.objects.get(id=alert_id)
        except StockAlert.DoesNotExist:
            raise GraphQLError("Stock alert not found")
        
        if alert.status != StockAlert.AlertStatus.ACTIVE:
            raise GraphQLError("Only active alerts can be acknowledged")
        
        from django.utils import timezone
        alert.status = StockAlert.AlertStatus.ACKNOWLEDGED
        alert.acknowledged_at = timezone.now()
        alert.save()
        
        return AcknowledgeStockAlert(
            success=True,
            message="Stock alert acknowledged",
            alert=alert
        )


class InventoryMutations(graphene.ObjectType):
    """Inventory GraphQL mutations"""
    adjust_stock = AdjustStock.Field()
    receive_stock = ReceiveStock.Field()
    return_stock = ReturnStock.Field()
    acknowledge_stock_alert = AcknowledgeStockAlert.Field()
    # Barcode mutations
    from .barcode_mutations import GenerateBarcode, GenerateSKU, GenerateAllBarcodes
    generate_barcode = GenerateBarcode.Field()
    generate_sku = GenerateSKU.Field()
    generate_all_barcodes = GenerateAllBarcodes.Field()

