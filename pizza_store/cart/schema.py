import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from decimal import Decimal
from .models import Cart, CartItem
from products.models import Product, Size, Topping
from products.schema import ProductType, SizeType
from .utils import get_or_create_cart, get_cart_from_request, calculate_item_price, format_toppings_for_storage


# ==================== GraphQL Types ====================

class CartItemType(DjangoObjectType):
    """GraphQL type for CartItem"""
    product = graphene.Field(ProductType)
    size = graphene.Field(SizeType)
    subtotal = graphene.Decimal()
    selected_toppings = graphene.JSONString()
    
    class Meta:
        model = CartItem
        fields = (
            'id', 'product', 'size', 'quantity', 
            'selected_toppings', 'unit_price', 'created_at'
        )
    
    def resolve_subtotal(self, info):
        """Calculate and return subtotal for this item"""
        return self.get_subtotal()
    
    def resolve_selected_toppings(self, info):
        """Return selected toppings as JSON"""
        return self.selected_toppings


class CartType(DjangoObjectType):
    """GraphQL type for Cart"""
    items = graphene.List(CartItemType)
    total = graphene.Decimal()
    item_count = graphene.Int()
    
    class Meta:
        model = Cart
        fields = ('id', 'session_key', 'created_at', 'updated_at')
    
    def resolve_items(self, info):
        """Return all cart items"""
        return self.items.all()
    
    def resolve_total(self, info):
        """Calculate and return total cart price"""
        return self.get_total()
    
    def resolve_item_count(self, info):
        """Return total number of items in cart"""
        return self.items.count()


# ==================== Input Types ====================

class AddToCartInput(graphene.InputObjectType):
    product_id = graphene.ID(required=True)
    quantity = graphene.Int(default_value=1)
    size_id = graphene.ID()
    topping_ids = graphene.List(graphene.ID)


class UpdateCartItemInput(graphene.InputObjectType):
    item_id = graphene.ID(required=True)
    quantity = graphene.Int()
    size_id = graphene.ID()
    topping_ids = graphene.List(graphene.ID)


# ==================== Queries ====================

class CartQuery(graphene.ObjectType):
    """All cart-related queries"""
    
    cart = graphene.Field(
        CartType,
        description="Get current user's cart (session-based)"
    )
    
    def resolve_cart(self, info):
        """Get cart from session"""
        cart = get_cart_from_request(info.context)
        return cart


# ==================== Mutations ====================

class AddToCart(graphene.Mutation):
    """Add product to cart"""
    class Arguments:
        input = AddToCartInput(required=True)
    
    cart_item = graphene.Field(CartItemType)
    cart = graphene.Field(CartType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, input):
        # Get or create cart
        cart = get_or_create_cart(info.context)
        
        # Get product
        try:
            product = Product.objects.get(pk=input.get('product_id'))
        except Product.DoesNotExist:
            raise GraphQLError("Product not found")
        
        if not product.is_available:
            raise GraphQLError("Product is not available")
        
        # Get size if provided
        size = None
        if input.get('size_id'):
            try:
                size = Size.objects.get(pk=input.get('size_id'))
                # Verify size is available for product
                if size not in product.available_sizes.all():
                    raise GraphQLError(f"Size '{size.name}' is not available for this product")
            except Size.DoesNotExist:
                raise GraphQLError("Size not found")
        
        # Format toppings
        topping_ids = input.get('topping_ids', [])
        formatted_toppings = format_toppings_for_storage(topping_ids)
        
        # Verify toppings are available for product
        for topping_data in formatted_toppings:
            try:
                topping = Topping.objects.get(pk=topping_data['id'])
                if topping not in product.available_toppings.all():
                    raise GraphQLError(f"Topping '{topping.name}' is not available for this product")
            except Topping.DoesNotExist:
                raise GraphQLError("Topping not found")
        
        # Calculate price
        unit_price = calculate_item_price(product, size, formatted_toppings)
        
        # Check if same item already exists (same product, size, and toppings)
        # For simplicity, we'll create a new item each time
        # You could add logic to merge items if needed
        
        # Create cart item
        cart_item = CartItem.objects.create(
            cart=cart,
            product=product,
            size=size,
            quantity=input.get('quantity', 1),
            selected_toppings=formatted_toppings,
            unit_price=unit_price
        )
        
        return AddToCart(
            cart_item=cart_item,
            cart=cart,
            success=True,
            message="Item added to cart successfully"
        )


class UpdateCartItem(graphene.Mutation):
    """Update cart item (quantity, size, or toppings)"""
    class Arguments:
        input = UpdateCartItemInput(required=True)
    
    cart_item = graphene.Field(CartItemType)
    cart = graphene.Field(CartType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, input):
        # Get cart
        cart = get_cart_from_request(info.context)
        if not cart:
            raise GraphQLError("Cart not found")
        
        # Get cart item
        try:
            cart_item = CartItem.objects.get(pk=input.get('item_id'), cart=cart)
        except CartItem.DoesNotExist:
            raise GraphQLError("Cart item not found")
        
        product = cart_item.product
        
        # Update quantity if provided
        if input.get('quantity') is not None:
            quantity = input.get('quantity')
            if quantity <= 0:
                raise GraphQLError("Quantity must be greater than 0")
            cart_item.quantity = quantity
        
        # Update size if provided
        if input.get('size_id') is not None:
            if input.get('size_id'):
                try:
                    size = Size.objects.get(pk=input.get('size_id'))
                    if size not in product.available_sizes.all():
                        raise GraphQLError(f"Size '{size.name}' is not available for this product")
                    cart_item.size = size
                except Size.DoesNotExist:
                    raise GraphQLError("Size not found")
            else:
                cart_item.size = None
        
        # Update toppings if provided
        if input.get('topping_ids') is not None:
            formatted_toppings = format_toppings_for_storage(input.get('topping_ids', []))
            # Verify toppings
            for topping_data in formatted_toppings:
                try:
                    topping = Topping.objects.get(pk=topping_data['id'])
                    if topping not in product.available_toppings.all():
                        raise GraphQLError(f"Topping '{topping.name}' is not available for this product")
                except Topping.DoesNotExist:
                    raise GraphQLError("Topping not found")
            cart_item.selected_toppings = formatted_toppings
        
        # Recalculate price if size or toppings changed
        if input.get('size_id') is not None or input.get('topping_ids') is not None:
            cart_item.unit_price = calculate_item_price(
                product, 
                cart_item.size, 
                cart_item.selected_toppings
            )
        
        cart_item.save()
        
        return UpdateCartItem(
            cart_item=cart_item,
            cart=cart,
            success=True,
            message="Cart item updated successfully"
        )


class RemoveFromCart(graphene.Mutation):
    """Remove item from cart"""
    class Arguments:
        item_id = graphene.ID(required=True)
    
    cart = graphene.Field(CartType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, item_id):
        # Get cart
        cart = get_cart_from_request(info.context)
        if not cart:
            raise GraphQLError("Cart not found")
        
        # Get and delete cart item
        try:
            cart_item = CartItem.objects.get(pk=item_id, cart=cart)
            cart_item.delete()
        except CartItem.DoesNotExist:
            raise GraphQLError("Cart item not found")
        
        return RemoveFromCart(
            cart=cart,
            success=True,
            message="Item removed from cart successfully"
        )


class ClearCart(graphene.Mutation):
    """Clear entire cart"""
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info):
        # Get cart
        cart = get_cart_from_request(info.context)
        if not cart:
            raise GraphQLError("Cart not found")
        
        # Delete all items
        cart.items.all().delete()
        
        return ClearCart(
            success=True,
            message="Cart cleared successfully"
        )


class CartMutation(graphene.ObjectType):
    """All cart-related mutations"""
    add_to_cart = AddToCart.Field()
    update_cart_item = UpdateCartItem.Field()
    remove_from_cart = RemoveFromCart.Field()
    clear_cart = ClearCart.Field()