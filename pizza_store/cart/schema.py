import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from decimal import Decimal
from .models import Cart, CartItem
from products.models import Product, Size, Topping
from products.schema import ProductType, SizeType
from .utils import get_or_create_cart, get_cart_from_request, calculate_item_price, format_toppings_for_storage, find_matching_cart_item, format_included_items_for_storage


# ==================== GraphQL Types ====================

class ToppingSelectionType(graphene.ObjectType):
    """GraphQL type for a selected topping in cart item"""
    id = graphene.ID()
    name = graphene.String()
    price = graphene.Decimal()


class IncludedItemSelectionType(graphene.ObjectType):
    """GraphQL type for an included item in combo"""
    id = graphene.ID()
    name = graphene.String()


class CartItemType(DjangoObjectType):
    """GraphQL type for CartItem"""
    product = graphene.Field(ProductType)
    size = graphene.Field(SizeType)
    subtotal = graphene.Decimal()
    selected_toppings = graphene.JSONString()
    toppings = graphene.List(ToppingSelectionType, description="Selected toppings as structured list")
    unit_price_with_toppings = graphene.Decimal(description="Unit price including toppings")
    
    # Combo-related fields
    include_combo_items = graphene.Boolean(description="Whether combo items are included")
    is_combo_order = graphene.Boolean(description="Whether this is a combo order (product is combo AND combo items selected)")
    included_items = graphene.List(IncludedItemSelectionType, description="Included items for this combo")
    combo_available = graphene.Boolean(description="Whether this product can be ordered as a combo")
    
    class Meta:
        model = CartItem
        fields = (
            'id', 'product', 'size', 'quantity', 
            'selected_toppings', 'unit_price', 'include_combo_items',
            'selected_included_items', 'created_at'
        )
    
    def resolve_subtotal(self, info):
        """Calculate and return subtotal for this item"""
        return self.get_subtotal()
    
    def resolve_selected_toppings(self, info):
        """Return selected toppings as JSON (for backward compatibility)"""
        return self.selected_toppings
    
    def resolve_toppings(self, info):
        """Return selected toppings as structured list"""
        if not self.selected_toppings:
            return []
        
        toppings_list = []
        for topping_data in self.selected_toppings:
            toppings_list.append(ToppingSelectionType(
                id=topping_data.get('id'),
                name=topping_data.get('name', ''),
                price=Decimal(str(topping_data.get('price', 0)))
            ))
        return toppings_list
    
    def resolve_unit_price_with_toppings(self, info):
        """Return unit price including toppings"""
        toppings_total = sum(
            Decimal(str(t.get('price', 0))) for t in (self.selected_toppings or [])
        )
        return self.unit_price + toppings_total
    
    def resolve_is_combo_order(self, info):
        """Check if this is a combo order"""
        return self.include_combo_items and self.product.is_combo
    
    def resolve_included_items(self, info):
        """Return included items for this combo order"""
        if not self.include_combo_items or not self.product.is_combo:
            return []
        
        # Return snapshot if available
        if self.selected_included_items:
            return [
                IncludedItemSelectionType(id=item.get('id'), name=item.get('name'))
                for item in self.selected_included_items
            ]
        
        # Fallback to current product's included items
        return [
            IncludedItemSelectionType(id=str(item.id), name=item.name)
            for item in self.product.included_items.all()
        ]
    
    def resolve_combo_available(self, info):
        """Check if this product can be ordered as a combo"""
        return self.product.is_combo


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
    include_combo_items = graphene.Boolean(
        default_value=False,
        description="If True and product is a combo, includes combo items (chips, salad, etc.)"
    )


class UpdateCartItemInput(graphene.InputObjectType):
    item_id = graphene.ID(required=True)
    quantity = graphene.Int()
    size_id = graphene.ID()
    topping_ids = graphene.List(graphene.ID)
    include_combo_items = graphene.Boolean(
        description="If True and product is a combo, includes combo items"
    )


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
        
        # Handle combo items option
        include_combo = input.get('include_combo_items', False)
        
        # Only allow combo option if product is actually a combo
        if include_combo and not product.is_combo:
            include_combo = False  # Silently ignore for non-combo products
        
        # Calculate price
        unit_price = calculate_item_price(product, size, formatted_toppings)
        
        # Check if same item already exists (same product, size, toppings, AND combo option)
        existing_item = find_matching_cart_item(cart, product, size, formatted_toppings, include_combo)
        
        if existing_item:
            # Merge quantities - add new quantity to existing
            new_quantity = input.get('quantity', 1)
            existing_item.quantity += new_quantity
            # Recalculate unit price in case product price changed (sale, etc.)
            existing_item.unit_price = unit_price
            existing_item.save()
            cart_item = existing_item
            message = f"Quantity updated. Total quantity: {existing_item.quantity}"
        else:
            # Snapshot included items if combo option selected
            included_items_snapshot = []
            if include_combo and product.is_combo:
                included_items_snapshot = format_included_items_for_storage(product)
            
            # Create new cart item
            cart_item = CartItem.objects.create(
                cart=cart,
                product=product,
                size=size,
                quantity=input.get('quantity', 1),
                selected_toppings=formatted_toppings,
                unit_price=unit_price,
                include_combo_items=include_combo,
                selected_included_items=included_items_snapshot
            )
            combo_text = " as combo" if include_combo else ""
            message = f"Item added to cart{combo_text} successfully"
        
        return AddToCart(
            cart_item=cart_item,
            cart=cart,
            success=True,
            message=message
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
        
        # Update combo option if provided
        if input.get('include_combo_items') is not None:
            include_combo = input.get('include_combo_items')
            # Only allow combo option if product is actually a combo
            if include_combo and product.is_combo:
                cart_item.include_combo_items = True
                cart_item.selected_included_items = format_included_items_for_storage(product)
            else:
                cart_item.include_combo_items = False
                cart_item.selected_included_items = []
        
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