# inventory/pos_schema.py
"""
POS-specific GraphQL queries and mutations
Optimized for Point of Sale interface
"""
import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal as D

from products.models import Product, Category, Size
from orders.models import Order, OrderItem
from inventory.models import StockItem
from inventory.utils import get_or_create_stock_item
from accounts.models import User


# POS-specific Types
class POSProductType(graphene.ObjectType):
    """Optimized product type for POS (includes stock info)"""
    id = graphene.ID()
    name = graphene.String()
    base_price = graphene.Decimal()
    current_price = graphene.Decimal()
    barcode = graphene.String()
    sku = graphene.String()
    stock_quantity = graphene.Int()
    is_in_stock = graphene.Boolean()
    is_low_stock = graphene.Boolean()
    category = graphene.String()
    image_url = graphene.String()
    track_inventory = graphene.Boolean()


class POSOrderType(graphene.ObjectType):
    """Simplified order type for POS"""
    id = graphene.ID()
    order_number = graphene.String()
    customer_name = graphene.String()
    total = graphene.Decimal()
    status = graphene.String()
    order_type = graphene.String()
    created_at = graphene.DateTime()
    item_count = graphene.Int()


class ReceiptItemType(graphene.ObjectType):
    """Receipt item for printing"""
    product_name = graphene.String()
    size = graphene.String()
    quantity = graphene.Int()
    unit_price = graphene.Decimal()
    subtotal = graphene.Decimal()
    toppings = graphene.List(graphene.String)


class ReceiptType(graphene.ObjectType):
    """Receipt data for printing"""
    order_number = graphene.String()
    date = graphene.String()
    time = graphene.String()
    customer_name = graphene.String()
    customer_phone = graphene.String()
    customer_email = graphene.String()
    items = graphene.List(ReceiptItemType)
    subtotal = graphene.Decimal()
    delivery_fee = graphene.Decimal()
    discount_amount = graphene.Decimal()
    total = graphene.Decimal()
    payment_method = graphene.String()
    order_type = graphene.String()
    delivery_address = graphene.String()


class DailySalesStatsType(graphene.ObjectType):
    """Daily sales statistics"""
    date = graphene.String()
    total_sales = graphene.Decimal()
    order_count = graphene.Int()
    average_order_value = graphene.Decimal()
    cash_sales = graphene.Decimal()
    card_sales = graphene.Decimal()
    delivery_orders = graphene.Int()
    pickup_orders = graphene.Int()
    top_products = graphene.List(graphene.JSONString)


class POSOrderItemInput(graphene.InputObjectType):
    """Input for a single order item"""
    productId = graphene.ID(required=True)  # Use camelCase for GraphQL
    quantity = graphene.Int(required=True)
    sizeId = graphene.ID()  # Use camelCase for GraphQL
    toppings = graphene.List(graphene.JSONString)


class POSOrderInput(graphene.InputObjectType):
    """Input for creating order from POS"""
    customer_name = graphene.String(required=True)
    customer_phone = graphene.String(required=True)
    customer_email = graphene.String()
    order_type = graphene.String(required=True)  # 'delivery' or 'pickup'
    delivery_address = graphene.String()
    delivery_instructions = graphene.String()
    order_notes = graphene.String()
    payment_method = graphene.String(required=True)  # 'cash', 'card', 'split'
    items = graphene.List(POSOrderItemInput, required=True)


# POS Queries
class POSQuery(graphene.ObjectType):
    """POS-specific GraphQL queries"""
    
    # Product queries
    pos_products = graphene.List(
        POSProductType,
        category_id=graphene.ID(),
        search=graphene.String(),
        in_stock_only=graphene.Boolean(default_value=False),
        description="Get products optimized for POS display"
    )
    
    pos_product = graphene.Field(
        POSProductType,
        product_id=graphene.ID(required=True),
        description="Get single product for POS"
    )
    
    # Barcode scanning
    scan_barcode = graphene.Field(
        POSProductType,
        barcode=graphene.String(required=True),
        description="Scan barcode and get product (for POS)"
    )
    
    # Order queries
    pos_recent_orders = graphene.List(
        POSOrderType,
        limit=graphene.Int(default_value=20),
        description="Get recent orders for POS display"
    )
    
    pos_order = graphene.Field(
        'orders.schema.OrderType',
        order_id=graphene.ID(required=True),
        description="Get order details for POS"
    )
    
    # Receipt generation
    receipt = graphene.Field(
        ReceiptType,
        order_id=graphene.ID(required=True),
        description="Generate receipt data for printing"
    )
    
    # Sales statistics
    pos_daily_stats = graphene.Field(
        DailySalesStatsType,
        date=graphene.String(),
        description="Get daily sales statistics (defaults to today)"
    )
    
    pos_today_stats = graphene.Field(
        DailySalesStatsType,
        description="Get today's sales statistics"
    )
    
    def resolve_pos_products(self, info, category_id=None, search=None, in_stock_only=False):
        """Get products optimized for POS"""
        user = info.context.user if info.context.user.is_authenticated else None
        
        # Check permissions (staff/admin only for POS)
        if not user or not (user.is_staff or user.is_superuser):
            raise GraphQLError("Permission denied. Staff access required for POS.")
        
        queryset = Product.objects.filter(is_available=True)
        
        # Filter by category
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Search filter
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(sku__icontains=search) |
                Q(barcode__icontains=search)
            )
        
        # Filter by stock availability
        if in_stock_only:
            # Only products that are in stock or don't track inventory
            products = []
            for product in queryset:
                if not product.track_inventory or product.is_in_stock:
                    products.append(product)
            queryset = Product.objects.filter(id__in=[p.id for p in products])
        
        # Convert to POS format
        pos_products = []
        for product in queryset:
            pos_products.append(POSQuery._product_to_pos(product, info))
        
        return pos_products
    
    def resolve_pos_product(self, info, product_id):
        """Get single product for POS"""
        if not info or not hasattr(info, 'context') or not info.context:
            raise GraphQLError("Invalid request context")
        user = info.context.user if hasattr(info.context, 'user') and info.context.user.is_authenticated else None
        
        if not user or not (user.is_staff or user.is_superuser):
            raise GraphQLError("Permission denied. Staff access required for POS.")
        
        try:
            product = Product.objects.get(id=product_id, is_available=True)
            return POSQuery._product_to_pos(product, info)
        except Product.DoesNotExist:
            raise GraphQLError("Product not found")
    
    def resolve_scan_barcode(self, info, barcode):
        """Scan barcode and return product"""
        if not info or not hasattr(info, 'context') or not info.context:
            raise GraphQLError("Invalid request context")
        user = info.context.user if hasattr(info.context, 'user') and info.context.user.is_authenticated else None
        
        if not user or not (user.is_staff or user.is_superuser):
            raise GraphQLError("Permission denied. Staff access required for POS.")
        
        try:
            product = Product.objects.get(barcode=barcode, is_available=True)
            return POSQuery._product_to_pos(product, info)
        except Product.DoesNotExist:
            raise GraphQLError(f"Product with barcode '{barcode}' not found")
        except Product.MultipleObjectsReturned:
            raise GraphQLError(f"Multiple products found with barcode '{barcode}'")
    
    def resolve_pos_recent_orders(self, info, limit=20):
        """Get recent orders for POS display"""
        user = info.context.user if info.context.user.is_authenticated else None
        
        if not user or not (user.is_staff or user.is_superuser):
            raise GraphQLError("Permission denied. Staff access required for POS.")
        
        orders = Order.objects.all().order_by('-created_at')[:limit]
        
        pos_orders = []
        for order in orders:
            pos_orders.append(POSOrderType(
                id=order.id,
                order_number=order.order_number,
                customer_name=order.customer_name,
                total=order.total,
                status=order.status,
                order_type=order.order_type,
                created_at=order.created_at,
                item_count=order.items.count()
            ))
        
        return pos_orders
    
    def resolve_pos_order(self, info, order_id):
        """Get order details for POS"""
        user = info.context.user if info.context.user.is_authenticated else None
        
        if not user or not (user.is_staff or user.is_superuser):
            raise GraphQLError("Permission denied. Staff access required for POS.")
        
        try:
            return Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise GraphQLError("Order not found")
    
    def resolve_receipt(self, info, order_id):
        """Generate receipt data for printing"""
        user = info.context.user if info.context.user.is_authenticated else None
        
        if not user or not (user.is_staff or user.is_superuser):
            raise GraphQLError("Permission denied. Staff access required for POS.")
        
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise GraphQLError("Order not found")
        
        # Format receipt items
        receipt_items = []
        for item in order.items.all():
            toppings = [t.get('name', '') for t in item.selected_toppings]
            receipt_items.append(ReceiptItemType(
                product_name=item.product_name,
                size=item.size_name or '',
                quantity=item.quantity,
                unit_price=item.unit_price,
                subtotal=item.subtotal,
                toppings=toppings
            ))
        
        # Format date and time
        order_date = order.created_at
        date_str = order_date.strftime('%Y-%m-%d')
        time_str = order_date.strftime('%H:%M:%S')
        
        return ReceiptType(
            order_number=order.order_number,
            date=date_str,
            time=time_str,
            customer_name=order.customer_name,
            customer_phone=order.customer_phone,
            customer_email=order.customer_email,
            items=receipt_items,
            subtotal=order.subtotal,
            delivery_fee=order.delivery_fee,
            discount_amount=order.discount_amount,
            total=order.total,
            payment_method='',  # Not stored in Order model yet
            order_type=order.order_type,
            delivery_address=order.delivery_address or ''
        )
    
    def resolve_pos_daily_stats(self, info, date=None):
        """Get daily sales statistics"""
        user = info.context.user if info.context.user.is_authenticated else None
        
        if not user or not (user.is_staff or user.is_superuser):
            raise GraphQLError("Permission denied. Staff access required for POS.")
        
        # Parse date or use today
        if date:
            try:
                target_date = datetime.strptime(date, '%Y-%m-%d').date()
            except ValueError:
                raise GraphQLError("Invalid date format. Use YYYY-MM-DD")
        else:
            target_date = timezone.now().date()
        
        # Get orders for the day
        start_datetime = timezone.make_aware(datetime.combine(target_date, datetime.min.time()))
        end_datetime = start_datetime + timedelta(days=1)
        
        orders = Order.objects.filter(
            created_at__gte=start_datetime,
            created_at__lt=end_datetime
        )
        
        # Calculate statistics
        total_sales = orders.aggregate(Sum('total'))['total__sum'] or D('0.00')
        order_count = orders.count()
        average_order_value = total_sales / order_count if order_count > 0 else D('0.00')
        
        # Payment method breakdown (placeholder - not stored yet)
        cash_sales = D('0.00')
        card_sales = D('0.00')
        
        # Order type breakdown
        delivery_orders = orders.filter(order_type='delivery').count()
        pickup_orders = orders.filter(order_type='pickup').count()
        
        # Top products
        top_products = OrderItem.objects.filter(
            order__in=orders
        ).values('product_name').annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('subtotal')
        ).order_by('-total_quantity')[:5]
        
        return DailySalesStatsType(
            date=target_date.strftime('%Y-%m-%d'),
            total_sales=total_sales,
            order_count=order_count,
            average_order_value=average_order_value,
            cash_sales=cash_sales,
            card_sales=card_sales,
            delivery_orders=delivery_orders,
            pickup_orders=pickup_orders,
            top_products=[dict(p) for p in top_products]
        )
    
    def resolve_pos_today_stats(self, info):
        """Get today's sales statistics"""
        return POSQuery.resolve_pos_daily_stats(self, info, date=None)
    
    @staticmethod
    def _product_to_pos(product, info):
        """Convert Product to POSProductType"""
        # Get image URL
        image_url = None
        if product.image:
            if info and info.context:
                request = info.context
                if hasattr(request, 'build_absolute_uri'):
                    image_url = request.build_absolute_uri(product.image.url)
                else:
                    image_url = product.image.url
            else:
                image_url = product.image.url
        
        return POSProductType(
            id=product.id,
            name=product.name,
            base_price=product.base_price,
            current_price=product.get_current_base_price(),
            barcode=product.barcode,
            sku=product.sku,
            stock_quantity=product.stock_quantity,
            is_in_stock=product.is_in_stock,
            is_low_stock=product.is_low_stock,
            category=product.category.name,
            image_url=image_url,
            track_inventory=product.track_inventory
        )


# POS Mutations
class CreatePOSOrder(graphene.Mutation):
    """Create order directly from POS (without cart)"""
    
    class Arguments:
        input = POSOrderInput(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    order = graphene.Field('orders.schema.OrderType')
    
    @staticmethod
    def mutate(root, info, input):
        user = info.context.user if info.context.user.is_authenticated else None
        
        # Check permissions
        if not user or not (user.is_staff or user.is_superuser):
            raise GraphQLError("Permission denied. Staff access required for POS.")
        
        # Validate order type
        order_type = input['order_type'].lower()
        if order_type not in ['delivery', 'pickup']:
            raise GraphQLError("Order type must be 'delivery' or 'pickup'")
        
        # Validate delivery address
        if order_type == 'delivery' and not input.get('delivery_address'):
            raise GraphQLError("Delivery address is required for delivery orders")
        
        # Validate items
        items = input['items']
        if not items or len(items) == 0:
            raise GraphQLError("Order must have at least one item")
        
        # Calculate totals
        from orders.utils import generate_order_number
        from decimal import Decimal as D
        
        subtotal = D('0.00')
        delivery_fee = D(input.get('delivery_fee', 0)) if input.get('delivery_fee') else D('0.00')
        
        if order_type == 'pickup':
            delivery_fee = D('0.00')
        
        # Process items and calculate subtotal
        order_items_data = []
        for item in items:
            try:
                product = Product.objects.get(id=item['productId'], is_available=True)
            except Product.DoesNotExist:
                raise GraphQLError(f"Product with ID {item['productId']} not found")
            
            quantity = int(item.get('quantity', 1))
            if quantity <= 0:
                raise GraphQLError("Item quantity must be greater than 0")
            
            # Get size if provided
            size = None
            if item.get('sizeId'):
                try:
                    size = Size.objects.get(id=item['sizeId'])
                except Size.DoesNotExist:
                    raise GraphQLError(f"Size with ID {item['sizeId']} not found")
            
            # Calculate unit price
            if size:
                unit_price = product.get_price_for_size(size)
            else:
                unit_price = product.get_current_base_price()
            
            # Add topping prices
            toppings_total = D('0.00')
            selected_toppings = []
            if item.get('toppings'):
                for topping_data in item['toppings']:
                    if isinstance(topping_data, dict) and 'price' in topping_data:
                        toppings_total += D(str(topping_data['price']))
                        selected_toppings.append(topping_data)
            
            item_subtotal = (unit_price + toppings_total) * D(quantity)
            subtotal += item_subtotal
            
            order_items_data.append({
                'product': product,
                'product_name': product.name,
                'product_id': product.id,
                'size': size,
                'size_name': size.name if size else None,
                'size_id': size.id if size else None,
                'quantity': quantity,
                'unit_price': unit_price,
                'toppings': selected_toppings,
                'subtotal': item_subtotal,
                'is_combo': product.is_combo,
                'included_items': [item.name for item in product.included_items.all()]
            })
        
        # Generate order number
        from orders.utils import generate_order_number
        order_number = generate_order_number()
        
        # Create order
        order = Order.objects.create(
            order_number=order_number,
            customer_name=input['customer_name'],
            customer_email=input.get('customer_email', ''),
            customer_phone=input['customer_phone'],
            order_type=order_type,
            order_notes=input.get('order_notes', ''),
            delivery_address=input.get('delivery_address', ''),
            delivery_instructions=input.get('delivery_instructions', ''),
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            discount_amount=D('0.00'),
            total=subtotal + delivery_fee,
            status=Order.Status.CONFIRMED
        )
        
        # Create order items and deduct stock
        from inventory.utils import sell_stock
        
        for item_data in order_items_data:
            OrderItem.objects.create(
                order=order,
                product_name=item_data['product_name'],
                product_id=item_data['product_id'],
                is_combo=item_data['is_combo'],
                included_items=item_data['included_items'],
                size_name=item_data['size_name'],
                size_id=item_data['size_id'],
                selected_toppings=item_data['toppings'],
                unit_price=item_data['unit_price'],
                quantity=item_data['quantity'],
                subtotal=item_data['subtotal']
            )
            
            # Deduct stock if tracking inventory
            if item_data['product'].track_inventory:
                try:
                    sell_stock(
                        product=item_data['product'],
                        quantity=item_data['quantity'],
                        order_number=order_number,
                        user=user
                    )
                except Exception as e:
                    # Log error but don't fail order creation
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Failed to deduct stock for product {item_data['product'].id}: {str(e)}")
        
        return CreatePOSOrder(
            success=True,
            message=f"Order created successfully! Order number: {order_number}",
            order=order
        )


class POSMutations(graphene.ObjectType):
    """POS-specific GraphQL mutations"""
    create_pos_order = CreatePOSOrder.Field()

