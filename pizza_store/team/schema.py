import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from django.utils import timezone
from decimal import Decimal
from .models import StoreSettings, Promotion


# ==================== GraphQL Types ====================

class StoreSettingsType(DjangoObjectType):
    """GraphQL type for Store Settings"""
    business_hours = graphene.JSONString()
    
    class Meta:
        model = StoreSettings
        fields = (
            'store_name', 'store_phone', 'store_email', 'store_address',
            'business_hours', 'delivery_enabled', 'pickup_enabled',
            'delivery_fee', 'free_delivery_threshold', 'minimum_order_amount',
            'delivery_radius_km', 'estimated_delivery_time', 'estimated_pickup_time',
            'tax_rate', 'tax_included_in_prices', 'accept_orders', 'order_notes_enabled'
        )


class PromotionType(DjangoObjectType):
    """GraphQL type for Promotion"""
    is_valid = graphene.Boolean()
    discount_display = graphene.String()
    applicable_products = graphene.List('products.schema.ProductType')
    
    class Meta:
        model = Promotion
        fields = (
            'id', 'code', 'name', 'description', 'discount_type',
            'discount_value', 'minimum_order_amount', 'maximum_discount',
            'usage_limit', 'times_used', 'is_active', 'valid_from', 'valid_until',
            'applicable_products', 'apply_to_base_price', 'apply_to_toppings',
            'apply_to_included_items', 'apply_to_entire_order'
        )
    
    def resolve_is_valid(self, info):
        return self.is_valid
    
    def resolve_discount_display(self, info):
        if self.discount_type == 'percentage':
            return f"{self.discount_value}% off"
        elif self.discount_type == 'fixed':
            return f"${self.discount_value} off"
        else:
            return "Free Delivery"
    
    def resolve_applicable_products(self, info):
        return self.applicable_products.all()


class PromotionValidationResult(graphene.ObjectType):
    """Result of validating a promotion code"""
    valid = graphene.Boolean()
    promotion = graphene.Field(PromotionType)
    discount_amount = graphene.Decimal()
    message = graphene.String()


# ==================== Input Types ====================

class StoreSettingsInput(graphene.InputObjectType):
    store_name = graphene.String()
    store_phone = graphene.String()
    store_email = graphene.String()
    store_address = graphene.String()
    business_hours = graphene.JSONString()
    delivery_enabled = graphene.Boolean()
    pickup_enabled = graphene.Boolean()
    delivery_fee = graphene.Decimal()
    free_delivery_threshold = graphene.Decimal()
    minimum_order_amount = graphene.Decimal()
    delivery_radius_km = graphene.Decimal()
    estimated_delivery_time = graphene.Int()
    estimated_pickup_time = graphene.Int()
    tax_rate = graphene.Decimal()
    tax_included_in_prices = graphene.Boolean()
    accept_orders = graphene.Boolean()
    order_notes_enabled = graphene.Boolean()


class PromotionInput(graphene.InputObjectType):
    code = graphene.String(required=True)
    name = graphene.String(required=True)
    description = graphene.String()
    discount_type = graphene.String(required=True)
    discount_value = graphene.Decimal(required=True)
    minimum_order_amount = graphene.Decimal()
    maximum_discount = graphene.Decimal()
    usage_limit = graphene.Int()
    is_active = graphene.Boolean(required=True)
    valid_from = graphene.DateTime(required=True)
    valid_until = graphene.DateTime(required=True)
    # Product-specific fields
    applicable_product_ids = graphene.List(graphene.ID, description="Product IDs this promotion applies to. Empty = all products")
    apply_to_base_price = graphene.Boolean(description="Apply discount to product base price")
    apply_to_toppings = graphene.Boolean(description="Apply discount to toppings/add-ons")
    apply_to_included_items = graphene.Boolean(description="Apply discount to included items (e.g., chips, salad)")
    apply_to_entire_order = graphene.Boolean(description="If True, applies to entire order. If False, only selected products.")


# ==================== Queries ====================

class TeamQuery(graphene.ObjectType):
    """Store settings and promotions queries"""
    
    store_settings = graphene.Field(
        StoreSettingsType,
        description="Get store settings (public)"
    )
    
    # Promotion queries
    validate_promotion = graphene.Field(
        PromotionValidationResult,
        code=graphene.String(required=True),
        subtotal=graphene.Decimal(required=True),
        delivery_fee=graphene.Decimal(),
        description="Validate a promotion code for an order"
    )
    
    all_promotions = graphene.List(
        PromotionType,
        active_only=graphene.Boolean(),
        description="Get all promotions (admin only)"
    )
    
    promotion = graphene.Field(
        PromotionType,
        id=graphene.ID(),
        code=graphene.String(),
        description="Get promotion by ID or code (admin only)"
    )
    
    def resolve_store_settings(self, info):
        """Get store settings - public access"""
        return StoreSettings.get_settings()
    
    def resolve_validate_promotion(self, info, code, subtotal, delivery_fee=None):
        """Validate a promotion code"""
        try:
            promotion = Promotion.objects.get(code__iexact=code)
        except Promotion.DoesNotExist:
            return PromotionValidationResult(
                valid=False,
                promotion=None,
                discount_amount=Decimal('0.00'),
                message="Invalid promotion code"
            )
        
        if not promotion.is_valid:
            now = timezone.now()
            if now < promotion.valid_from:
                message = "This promotion hasn't started yet"
            elif now > promotion.valid_until:
                message = "This promotion has expired"
            elif promotion.usage_limit and promotion.times_used >= promotion.usage_limit:
                message = "This promotion has reached its usage limit"
            else:
                message = "This promotion is not active"
            
            return PromotionValidationResult(
                valid=False,
                promotion=promotion,
                discount_amount=Decimal('0.00'),
                message=message
            )
        
        # Check minimum order amount
        if promotion.minimum_order_amount and subtotal < promotion.minimum_order_amount:
            return PromotionValidationResult(
                valid=False,
                promotion=promotion,
                discount_amount=Decimal('0.00'),
                message=f"Minimum order amount is ${promotion.minimum_order_amount}"
            )
        
        # Calculate discount
        delivery = Decimal(str(delivery_fee)) if delivery_fee else Decimal('0.00')
        discount_amount = promotion.calculate_discount(Decimal(str(subtotal)), delivery)
        
        return PromotionValidationResult(
            valid=True,
            promotion=promotion,
            discount_amount=discount_amount,
            message=f"Code applied! You save ${discount_amount}"
        )
    
    def resolve_all_promotions(self, info, active_only=None):
        """Get all promotions (admin only)"""
        user = info.context.user
        
        if not user.is_authenticated:
            raise GraphQLError("Authentication required")
        
        if not user.has_promotion_permission():
            raise GraphQLError("You don't have permission to view promotions")
        
        queryset = Promotion.objects.all()
        
        if active_only:
            now = timezone.now()
            queryset = queryset.filter(
                is_active=True,
                valid_from__lte=now,
                valid_until__gte=now
            )
        
        return queryset
    
    def resolve_promotion(self, info, id=None, code=None):
        """Get promotion by ID or code"""
        user = info.context.user
        
        if not user.is_authenticated:
            raise GraphQLError("Authentication required")
        
        if not user.has_promotion_permission():
            raise GraphQLError("You don't have permission to view promotion details")
        
        if id:
            try:
                return Promotion.objects.get(pk=id)
            except Promotion.DoesNotExist:
                return None
        
        if code:
            try:
                return Promotion.objects.get(code__iexact=code)
            except Promotion.DoesNotExist:
                return None
        
        return None


# ==================== Mutations ====================

class UpdateStoreSettings(graphene.Mutation):
    """Update store settings (admin only)"""
    class Arguments:
        input = StoreSettingsInput(required=True)
    
    settings = graphene.Field(StoreSettingsType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, input):
        user = info.context.user
        
        if not user.is_authenticated or not user.is_admin:
            raise GraphQLError("Only admins can update store settings")
        
        settings = StoreSettings.get_settings()
        
        # Update fields if provided
        for field, value in input.items():
            if value is not None:
                setattr(settings, field, value)
        
        settings.save()
        
        return UpdateStoreSettings(
            settings=settings,
            success=True,
            message="Store settings updated successfully"
        )


class CreatePromotion(graphene.Mutation):
    """Create a new promotion (admin only)"""
    class Arguments:
        input = PromotionInput(required=True)
    
    promotion = graphene.Field(PromotionType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, input):
        user = info.context.user
        
        if not user.is_authenticated or not user.has_promotion_permission():
            raise GraphQLError("You don't have permission to create promotions")
        
        # Check if code already exists
        if Promotion.objects.filter(code__iexact=input.get('code')).exists():
            raise GraphQLError("A promotion with this code already exists")
        
        # Validate discount type
        valid_types = ['percentage', 'fixed', 'free_delivery']
        if input.get('discount_type') not in valid_types:
            raise GraphQLError(f"Invalid discount type. Must be one of: {', '.join(valid_types)}")
        
        from products.models import Product
        
        promotion = Promotion.objects.create(
            code=input.get('code').upper(),
            name=input.get('name'),
            description=input.get('description', ''),
            discount_type=input.get('discount_type'),
            discount_value=input.get('discount_value'),
            minimum_order_amount=input.get('minimum_order_amount'),
            maximum_discount=input.get('maximum_discount'),
            usage_limit=input.get('usage_limit'),
            is_active=input.get('is_active', True),
            valid_from=input.get('valid_from'),
            valid_until=input.get('valid_until'),
            apply_to_base_price=input.get('apply_to_base_price', True),
            apply_to_toppings=input.get('apply_to_toppings', False),
            apply_to_included_items=input.get('apply_to_included_items', False),
            apply_to_entire_order=input.get('apply_to_entire_order', True)
        )
        
        # Set applicable products
        product_ids = input.get('applicable_product_ids', [])
        if product_ids:
            products = Product.objects.filter(pk__in=product_ids)
            promotion.applicable_products.set(products)
        
        return CreatePromotion(
            promotion=promotion,
            success=True,
            message="Promotion created successfully"
        )


class UpdatePromotion(graphene.Mutation):
    """Update a promotion (admin only)"""
    class Arguments:
        id = graphene.ID(required=True)
        input = PromotionInput(required=True)
    
    promotion = graphene.Field(PromotionType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, id, input):
        user = info.context.user
        
        if not user.is_authenticated or not user.has_promotion_permission():
            raise GraphQLError("You don't have permission to update promotions")
        
        try:
            promotion = Promotion.objects.get(pk=id)
        except Promotion.DoesNotExist:
            raise GraphQLError("Promotion not found")
        
        from products.models import Product
        
        # Handle product IDs separately (ManyToMany)
        product_ids = input.pop('applicable_product_ids', None)
        
        # Update fields
        for field, value in input.items():
            if value is not None:
                if field == 'code':
                    value = value.upper()
                setattr(promotion, field, value)
        
        promotion.save()
        
        # Update applicable products if provided
        if product_ids is not None:
            if product_ids:
                products = Product.objects.filter(pk__in=product_ids)
                promotion.applicable_products.set(products)
            else:
                # Empty list means clear all products (apply to all)
                promotion.applicable_products.clear()
        
        return UpdatePromotion(
            promotion=promotion,
            success=True,
            message="Promotion updated successfully"
        )


class DeletePromotion(graphene.Mutation):
    """Delete a promotion (admin only)"""
    class Arguments:
        id = graphene.ID(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, id):
        user = info.context.user
        
        if not user.is_authenticated or not user.has_promotion_permission():
            raise GraphQLError("You don't have permission to delete promotions")
        
        try:
            promotion = Promotion.objects.get(pk=id)
            promotion.delete()
            return DeletePromotion(success=True, message="Promotion deleted successfully")
        except Promotion.DoesNotExist:
            raise GraphQLError("Promotion not found")


class TeamMutation(graphene.ObjectType):
    """Store settings and promotions mutations"""
    update_store_settings = UpdateStoreSettings.Field()
    create_promotion = CreatePromotion.Field()
    update_promotion = UpdatePromotion.Field()
    delete_promotion = DeletePromotion.Field()

