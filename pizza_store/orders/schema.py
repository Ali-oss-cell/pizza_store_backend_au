import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from decimal import Decimal
from datetime import datetime
from .models import Order, OrderItem
from cart.models import Cart, CartItem
from cart.utils import get_cart_from_request
from .utils import generate_order_number


# ==================== GraphQL Types ====================

class OrderItemType(DjangoObjectType):
    """GraphQL type for OrderItem"""
    selected_toppings = graphene.JSONString()
    included_items = graphene.JSONString()
    
    class Meta:
        model = OrderItem
        fields = (
            'id', 'product_name', 'product_id', 'is_combo', 'included_items',
            'size_name', 'size_id', 'selected_toppings', 'unit_price', 
            'quantity', 'subtotal'
        )
    
    def resolve_selected_toppings(self, info):
        """Return selected toppings as JSON"""
        return self.selected_toppings
    
    def resolve_included_items(self, info):
        """Return included items as JSON"""
        return self.included_items


class OrderType(DjangoObjectType):
    """GraphQL type for Order"""
    items = graphene.List(OrderItemType)
    status_display = graphene.String()
    order_type_display = graphene.String()
    
    class Meta:
        model = Order
        fields = (
            'id', 'order_number', 'customer_name', 'customer_email', 
            'customer_phone', 'order_type', 'status', 'order_notes',
            'delivery_address', 'delivery_instructions', 
            'subtotal', 'delivery_fee', 'discount_amount', 'discount_code', 'total',
            'created_at', 'updated_at', 'completed_at', 'cart_session_key'
        )
    
    def resolve_items(self, info):
        """Return all order items"""
        return self.items.all()
    
    def resolve_status_display(self, info):
        """Return human-readable status"""
        return self.get_status_display()
    
    def resolve_order_type_display(self, info):
        """Return human-readable order type"""
        return self.get_order_type_display()


# ==================== Input Types ====================

class CreateOrderInput(graphene.InputObjectType):
    customer_name = graphene.String(required=True)
    customer_email = graphene.String(required=True)
    customer_phone = graphene.String(required=True)
    order_type = graphene.String(required=True)  # 'delivery' or 'pickup'
    delivery_address = graphene.String()
    delivery_instructions = graphene.String()
    delivery_fee = graphene.Decimal()
    order_notes = graphene.String()
    promotion_code = graphene.String()  # Optional promotion/discount code


class UpdateOrderStatusInput(graphene.InputObjectType):
    order_id = graphene.ID(required=True)
    status = graphene.String(required=True)


# ==================== Queries ====================

class OrderStatsType(graphene.ObjectType):
    """Statistics for orders"""
    total_orders = graphene.Int()
    pending_orders = graphene.Int()
    preparing_orders = graphene.Int()
    ready_orders = graphene.Int()
    completed_orders = graphene.Int()
    cancelled_orders = graphene.Int()
    total_revenue = graphene.Decimal()
    today_orders = graphene.Int()
    today_revenue = graphene.Decimal()


class OrdersQuery(graphene.ObjectType):
    """All order-related queries"""
    
    order = graphene.Field(
        OrderType,
        order_number=graphene.String(),
        order_id=graphene.ID(),
        description="Get order by order number or ID"
    )
    
    orders = graphene.List(
        OrderType,
        status=graphene.String(),
        order_type=graphene.String(),
        date_from=graphene.Date(),
        date_to=graphene.Date(),
        limit=graphene.Int(),
        description="Get all orders (staff/admin only, filterable)"
    )
    
    recent_orders = graphene.List(
        OrderType,
        limit=graphene.Int(),
        description="Get recent orders (staff/admin only)"
    )
    
    order_stats = graphene.Field(
        OrderStatsType,
        description="Get order statistics (staff/admin only)"
    )
    
    def resolve_order(self, info, order_number=None, order_id=None):
        """Get order by order number or ID"""
        if order_number:
            try:
                return Order.objects.get(order_number=order_number)
            except Order.DoesNotExist:
                return None
        
        if order_id:
            try:
                return Order.objects.get(pk=order_id)
            except Order.DoesNotExist:
                return None
        
        return None
    
    def resolve_orders(self, info, status=None, order_type=None, date_from=None, date_to=None, limit=None):
        """Get all orders (staff/admin only)"""
        user = info.context.user
        
        # Check if user is authenticated and is staff/admin
        if not user.is_authenticated:
            raise GraphQLError("Authentication required")
        
        if not user.has_order_permission():
            raise GraphQLError("You don't have permission to view orders")
        
        queryset = Order.objects.all()
        
        if status:
            queryset = queryset.filter(status=status)
        if order_type:
            queryset = queryset.filter(order_type=order_type)
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        if limit:
            queryset = queryset[:limit]
        
        return queryset
    
    def resolve_recent_orders(self, info, limit=10):
        """Get recent orders (staff/admin only)"""
        user = info.context.user
        
        if not user.is_authenticated:
            raise GraphQLError("Authentication required")
        
        if not user.has_order_permission():
            raise GraphQLError("You don't have permission to view orders")
        
        return Order.objects.all()[:limit]
    
    def resolve_order_stats(self, info):
        """Get order statistics"""
        user = info.context.user
        
        if not user.is_authenticated:
            raise GraphQLError("Authentication required")
        
        if not user.has_report_permission():
            raise GraphQLError("You don't have permission to view statistics")
        
        from django.db.models import Sum, Count
        from django.utils import timezone
        today = timezone.now().date()
        
        total_orders = Order.objects.count()
        pending = Order.objects.filter(status='pending').count()
        preparing = Order.objects.filter(status='preparing').count()
        ready = Order.objects.filter(status='ready').count()
        completed = Order.objects.filter(status__in=['delivered', 'picked_up']).count()
        cancelled = Order.objects.filter(status='cancelled').count()
        
        revenue = Order.objects.exclude(status='cancelled').aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
        
        today_orders = Order.objects.filter(created_at__date=today).count()
        today_revenue = Order.objects.filter(
            created_at__date=today
        ).exclude(status='cancelled').aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
        
        return OrderStatsType(
            total_orders=total_orders,
            pending_orders=pending,
            preparing_orders=preparing,
            ready_orders=ready,
            completed_orders=completed,
            cancelled_orders=cancelled,
            total_revenue=revenue,
            today_orders=today_orders,
            today_revenue=today_revenue
        )


# ==================== Mutations ====================

class CreateOrder(graphene.Mutation):
    """Create order from cart (checkout)"""
    class Arguments:
        input = CreateOrderInput(required=True)
    
    order = graphene.Field(OrderType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, input):
        # Get cart from session
        cart = get_cart_from_request(info.context)
        
        if not cart:
            raise GraphQLError("Cart is empty. Add items to cart first.")
        
        # Check if cart has items
        cart_items = cart.items.all()
        if not cart_items.exists():
            raise GraphQLError("Cart is empty. Add items to cart first.")
        
        # Validate order type
        order_type = input.get('order_type').lower()
        if order_type not in ['delivery', 'pickup']:
            raise GraphQLError("Order type must be 'delivery' or 'pickup'")
        
        # Validate delivery address for delivery orders
        if order_type == 'delivery' and not input.get('delivery_address'):
            raise GraphQLError("Delivery address is required for delivery orders")
        
        # Calculate totals
        subtotal = cart.get_total()
        delivery_fee = Decimal(str(input.get('delivery_fee', 0))) if input.get('delivery_fee') else Decimal('0.00')
        
        # Add delivery fee only for delivery orders
        if order_type == 'pickup':
            delivery_fee = Decimal('0.00')
        
        # Generate unique order number
        order_number = generate_order_number()
        # Ensure uniqueness
        while Order.objects.filter(order_number=order_number).exists():
            order_number = generate_order_number()
        
        # Create order first (we'll update discount after calculating with order items)
        order = Order.objects.create(
            order_number=order_number,
            customer_name=input.get('customer_name'),
            customer_email=input.get('customer_email'),
            customer_phone=input.get('customer_phone'),
            order_type=order_type,
            order_notes=input.get('order_notes', ''),
            delivery_address=input.get('delivery_address', ''),
            delivery_instructions=input.get('delivery_instructions', ''),
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            discount_amount=Decimal('0.00'),
            discount_code=None,
            total=subtotal + delivery_fee,
            cart_session_key=cart.session_key,
            status=Order.Status.PENDING
        )
        
        # Create order items from cart items
        order_items = []
        for cart_item in cart_items:
            # Calculate item subtotal (including toppings)
            from decimal import Decimal as D
            toppings_total = sum(
                D(str(t.get('price', 0))) for t in cart_item.selected_toppings
            )
            item_subtotal = (cart_item.unit_price + toppings_total) * D(cart_item.quantity)
            
            # Get included item names for snapshot
            included_names = [item.name for item in cart_item.product.included_items.all()]
            
            order_item = OrderItem.objects.create(
                order=order,
                product_name=cart_item.product.name,
                product_id=cart_item.product.id,
                is_combo=cart_item.product.is_combo,
                included_items=included_names,
                size_name=cart_item.size.name if cart_item.size else None,
                size_id=cart_item.size.id if cart_item.size else None,
                selected_toppings=cart_item.selected_toppings,
                unit_price=cart_item.unit_price,
                quantity=cart_item.quantity,
                subtotal=item_subtotal
            )
            order_items.append(order_item)
        
        # Apply promotion code if provided (now with order items for product-specific discounts)
        discount_amount = Decimal('0.00')
        discount_code = None
        promotion_code = input.get('promotion_code')
        
        if promotion_code:
            from team.models import Promotion
            try:
                promotion = Promotion.objects.get(code__iexact=promotion_code)
                if promotion.is_valid:
                    if promotion.minimum_order_amount and subtotal < promotion.minimum_order_amount:
                        # Delete order and items if validation fails
                        order.delete()
                        raise GraphQLError(f"Minimum order amount for this code is ${promotion.minimum_order_amount}")
                    
                    # Calculate discount with order items for product-specific discounts
                    discount_amount = promotion.calculate_discount(subtotal, delivery_fee, order_items)
                    discount_code = promotion.code
                    
                    # Increment usage count
                    promotion.times_used += 1
                    promotion.save()
                else:
                    # Delete order and items if validation fails
                    order.delete()
                    raise GraphQLError("This promotion code is no longer valid")
            except Promotion.DoesNotExist:
                # Delete order and items if validation fails
                order.delete()
                raise GraphQLError("Invalid promotion code")
        
        # Update order with discount
        total = subtotal + delivery_fee - discount_amount
        order.discount_amount = discount_amount
        order.discount_code = discount_code
        order.total = total
        order.save()
        
        # Clear cart after order creation
        cart.items.all().delete()
        
        return CreateOrder(
            order=order,
            success=True,
            message=f"Order created successfully! Order number: {order_number}"
        )


class UpdateOrderStatus(graphene.Mutation):
    """Update order status (staff/admin only)"""
    class Arguments:
        input = UpdateOrderStatusInput(required=True)
    
    order = graphene.Field(OrderType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, input):
        user = info.context.user
        
        # Check if user is authenticated and is staff/admin
        if not user.is_authenticated:
            raise GraphQLError("Authentication required")
        
        if not user.has_order_permission():
            raise GraphQLError("You don't have permission to update order status")
        
        # Get order
        try:
            order = Order.objects.get(pk=input.get('order_id'))
        except Order.DoesNotExist:
            raise GraphQLError("Order not found")
        
        # Validate status
        new_status = input.get('status').lower()
        valid_statuses = [choice[0] for choice in Order.Status.choices]
        
        if new_status not in valid_statuses:
            raise GraphQLError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        # Update status
        old_status = order.status
        order.status = new_status
        
        # Set completed_at if order is delivered or picked up
        if new_status in [Order.Status.DELIVERED, Order.Status.PICKED_UP]:
            if not order.completed_at:
                order.completed_at = datetime.now()
        else:
            order.completed_at = None
        
        order.save()
        
        return UpdateOrderStatus(
            order=order,
            success=True,
            message=f"Order status updated from {old_status} to {new_status}"
        )


class OrdersMutation(graphene.ObjectType):
    """All order-related mutations"""
    create_order = CreateOrder.Field()
    update_order_status = UpdateOrderStatus.Field()