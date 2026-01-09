import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from django.db.models import Q
from django.core.files.base import ContentFile
import base64
import uuid
from .models import Category, Product, Size, Topping, Tag, IncludedItem, Ingredient, ProductReview
from .search import search_products as fuzzy_search_products, get_search_suggestions, get_popular_searches


# ==================== Helper Functions ====================

def save_base64_image(product, base64_string):
    """
    Save a base64 encoded image to the product's image field.
    Expected format: data:image/png;base64,iVBORw0KGgo... or just the base64 string
    """
    if not base64_string:
        return
    
    try:
        # Handle data URI format (data:image/png;base64,...)
        if ',' in base64_string:
            header, encoded = base64_string.split(',', 1)
            # Extract file extension from header
            if 'image/png' in header:
                ext = 'png'
            elif 'image/jpeg' in header or 'image/jpg' in header:
                ext = 'jpg'
            elif 'image/gif' in header:
                ext = 'gif'
            elif 'image/webp' in header:
                ext = 'webp'
            else:
                ext = 'png'  # default
        else:
            # Assume it's just base64 string, default to png
            encoded = base64_string
            ext = 'png'
        
        # Decode base64
        image_data = base64.b64decode(encoded)
        
        # Generate unique filename
        filename = f"{uuid.uuid4()}.{ext}"
        
        # Save to product image field
        product.image.save(filename, ContentFile(image_data), save=False)
    except Exception as e:
        raise GraphQLError(f"Error processing image: {str(e)}")


# ==================== GraphQL Types ====================

class TagType(DjangoObjectType):
    """GraphQL type for Tag"""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', 'color')


class IncludedItemType(DjangoObjectType):
    """GraphQL type for IncludedItem"""
    class Meta:
        model = IncludedItem
        fields = ('id', 'name')


class IngredientType(DjangoObjectType):
    """GraphQL type for Ingredient"""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'icon')


class CategoryType(DjangoObjectType):
    """GraphQL type for Category"""
    products = graphene.List('products.schema.ProductType')
    product_count = graphene.Int()
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'display_order', 'created_at', 'updated_at')
    
    def resolve_products(self, info):
        """Get all available products in this category"""
        return self.products.filter(is_available=True)
    
    def resolve_product_count(self, info):
        """Get count of available products in this category"""
        return self.products.filter(is_available=True).count()


class SizeType(DjangoObjectType):
    """GraphQL type for Size"""
    category = graphene.Field(CategoryType)
    
    class Meta:
        model = Size
        fields = ('id', 'name', 'category', 'price_modifier', 'display_order')
    
    def resolve_category(self, info):
        """Return the category object"""
        return self.category


class ToppingType(DjangoObjectType):
    """GraphQL type for Topping"""
    class Meta:
        model = Topping
        fields = ('id', 'name', 'price', 'created_at', 'updated_at')


class ProductReviewType(DjangoObjectType):
    """GraphQL type for ProductReview"""
    product = graphene.Field('products.schema.ProductType')
    rating_display = graphene.String()
    
    class Meta:
        model = ProductReview
        fields = ('id', 'customer_name', 'customer_email', 'rating', 'comment', 'is_approved', 'created_at', 'updated_at')
    
    def resolve_product(self, info):
        """Return the product for this review"""
        return self.product
    
    def resolve_rating_display(self, info):
        """Return rating as stars"""
        return '★' * self.rating + '☆' * (5 - self.rating)


# ==================== Search Types ====================

class SearchSuggestionItemType(graphene.ObjectType):
    """Single search suggestion item"""
    type = graphene.String(description="Type of suggestion: 'product', 'category', or 'tag'")
    id = graphene.ID(description="ID of the suggested item")
    text = graphene.String(description="Display text for the suggestion")
    category = graphene.String(description="Category name (for products only)")
    slug = graphene.String(description="Slug (for categories and tags)")
    score = graphene.Int(description="Relevance score")


class SearchSuggestionsType(graphene.ObjectType):
    """Search suggestions response with grouped results"""
    query = graphene.String(description="Original search query")
    suggestions = graphene.List(SearchSuggestionItemType, description="List of suggestions")
    products = graphene.List(SearchSuggestionItemType, description="Product suggestions only")
    categories = graphene.List(SearchSuggestionItemType, description="Category suggestions only")
    tags = graphene.List(SearchSuggestionItemType, description="Tag suggestions only")
    total_count = graphene.Int(description="Total number of suggestions")


class PopularSearchType(graphene.ObjectType):
    """Popular search term"""
    text = graphene.String(description="Search term text")
    type = graphene.String(description="Type: 'category' or 'tag'")
    slug = graphene.String(description="Slug for the search term")


class SearchResultType(graphene.ObjectType):
    """Search results with metadata"""
    query = graphene.String(description="Original search query")
    results = graphene.List('products.schema.ProductType', description="Matching products")
    total_count = graphene.Int(description="Total number of results")
    suggestions = graphene.List(SearchSuggestionItemType, description="Related suggestions")


class ProductType(DjangoObjectType):
    """GraphQL type for Product"""
    image_url = graphene.String()
    category = graphene.Field(CategoryType)
    tags = graphene.List(TagType)
    ingredients = graphene.List(IngredientType)
    included_items = graphene.List(IncludedItemType)
    available_sizes = graphene.List(SizeType)
    available_toppings = graphene.List(ToppingType)
    reviews = graphene.List(ProductReviewType)
    prep_time_display = graphene.String()
    is_on_sale = graphene.Boolean()
    current_price = graphene.Decimal(description="Current price (sale price if on sale, otherwise base price)")
    discount_percentage = graphene.Int(description="Discount percentage when on sale")
    # Inventory fields
    stock_quantity = graphene.Int(description="Current stock quantity (null if not tracking inventory)")
    is_in_stock = graphene.Boolean(description="Whether product is in stock")
    is_low_stock = graphene.Boolean(description="Whether product has low stock")
    stock_item = graphene.Field('inventory.schema.StockItemType', description="Stock item details")
    
    class Meta:
        model = Product
        fields = (
            'id', 'name', 'slug', 'short_description', 'description', 'base_price', 
            'sale_price', 'sale_start_date', 'sale_end_date',
            'category', 'tags', 'image', 'is_available', 'is_featured',
            'is_combo', 'included_items', 'ingredients',
            'prep_time_min', 'prep_time_max', 'average_rating', 'rating_count',
            'calories', 'available_sizes', 'available_toppings',
            'barcode', 'sku', 'track_inventory', 'reorder_level',
            'created_at', 'updated_at'
        )
    
    def resolve_is_on_sale(self, info):
        """Check if product is currently on sale"""
        return self.is_on_sale
    
    def resolve_current_price(self, info):
        """Get current price (sale price if on sale, otherwise base price)"""
        return self.get_current_base_price()
    
    def resolve_discount_percentage(self, info):
        """Get discount percentage when on sale"""
        return int(self.discount_percentage)
    
    def resolve_image_url(self, info):
        """Return full URL for product image"""
        if self.image:
            request = info.context
            if request:
                return request.build_absolute_uri(self.image.url)
            return self.image.url
        return None
    
    def resolve_stock_quantity(self, info):
        """Get current stock quantity"""
        return self.stock_quantity
    
    def resolve_is_in_stock(self, info):
        """Check if product is in stock"""
        return self.is_in_stock
    
    def resolve_is_low_stock(self, info):
        """Check if product has low stock"""
        return self.is_low_stock
    
    def resolve_stock_item(self, info):
        """Get stock item if tracking inventory"""
        if self.track_inventory:
            from inventory.utils import get_or_create_stock_item
            return get_or_create_stock_item(self)
        return None
    
    def resolve_tags(self, info):
        return self.tags.all()
    
    def resolve_ingredients(self, info):
        return self.ingredients.all()
    
    def resolve_included_items(self, info):
        return self.included_items.all()
    
    def resolve_available_sizes(self, info):
        """Return list of available sizes"""
        return self.available_sizes.all()
    
    def resolve_available_toppings(self, info):
        """Return list of available toppings"""
        return self.available_toppings.all()
    
    def resolve_reviews(self, info):
        """Return approved reviews only"""
        return self.reviews.filter(is_approved=True)
    
    def resolve_prep_time_display(self, info):
        """Return formatted prep time"""
        return f"{self.prep_time_min}-{self.prep_time_max} min"


# ==================== Input Types for Mutations ====================

class CategoryInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    slug = graphene.String()
    description = graphene.String()


class TagInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    slug = graphene.String()
    color = graphene.String()


class SizeInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    category_id = graphene.ID(required=True)  # ForeignKey to Category
    price_modifier = graphene.Decimal()
    display_order = graphene.Int()


class ToppingInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)


class IncludedItemInput(graphene.InputObjectType):
    name = graphene.String(required=True)


class IngredientInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    icon = graphene.String()


class ProductReviewInput(graphene.InputObjectType):
    product_id = graphene.ID(required=True)
    customer_name = graphene.String(required=True)
    customer_email = graphene.String(required=True)
    rating = graphene.Int(required=True)
    comment = graphene.String()


class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    short_description = graphene.String()
    description = graphene.String()
    base_price = graphene.Decimal(required=True)
    category_id = graphene.ID(required=True)
    tag_ids = graphene.List(graphene.ID)
    ingredient_ids = graphene.List(graphene.ID)
    is_available = graphene.Boolean()
    is_featured = graphene.Boolean()
    is_combo = graphene.Boolean()
    included_item_ids = graphene.List(graphene.ID)
    size_ids = graphene.List(graphene.ID)
    topping_ids = graphene.List(graphene.ID)
    prep_time_min = graphene.Int()
    prep_time_max = graphene.Int()
    calories = graphene.Int()
    image = graphene.String(description="Base64 encoded image data (data:image/png;base64,...)")
    # Sale pricing
    sale_price = graphene.Decimal(description="Sale price (applies to all users when active)")
    sale_start_date = graphene.DateTime(description="When the sale starts (leave empty to start immediately)")
    sale_end_date = graphene.DateTime(description="When the sale ends (leave empty for no end date)")


# ==================== Queries ====================

class ProductsQuery(graphene.ObjectType):
    """All product-related queries"""
    
    # Single product
    product = graphene.Field(
        ProductType,
        id=graphene.ID(required=True),
        description="Get a single product by ID"
    )
    
    # List all products
    all_products = graphene.List(
        ProductType,
        description="Get all products"
    )
    
    # Products by category
    products_by_category = graphene.List(
        ProductType,
        category_id=graphene.ID(),
        category_name=graphene.String(),
        category_slug=graphene.String(),
        description="Get products filtered by category"
    )
    
    # Products by tag
    products_by_tag = graphene.List(
        ProductType,
        tag_id=graphene.ID(),
        tag_name=graphene.String(),
        tag_slug=graphene.String(),
        description="Get products filtered by tag"
    )
    
    # Search products (basic)
    search_products = graphene.List(
        ProductType,
        search=graphene.String(required=True),
        description="Search products by name or description (basic search)"
    )
    
    # Fuzzy search products (advanced)
    fuzzy_search = graphene.List(
        ProductType,
        query=graphene.String(required=True),
        limit=graphene.Int(default_value=20),
        include_unavailable=graphene.Boolean(default_value=False),
        description="Advanced fuzzy search for products with relevance scoring"
    )
    
    # Search suggestions/autocomplete
    search_suggestions = graphene.Field(
        'products.schema.SearchSuggestionsType',
        query=graphene.String(required=True),
        limit=graphene.Int(default_value=10),
        description="Get search suggestions for autocomplete"
    )
    
    # Popular searches
    popular_searches = graphene.List(
        'products.schema.PopularSearchType',
        description="Get popular/trending search terms"
    )
    
    # Available products only
    available_products = graphene.List(
        ProductType,
        description="Get only available products"
    )
    
    # Categories
    all_categories = graphene.List(
        CategoryType,
        description="Get all categories"
    )
    
    category = graphene.Field(
        CategoryType,
        id=graphene.ID(),
        slug=graphene.String(),
        description="Get a single category by ID or slug"
    )
    
    # Tags
    all_tags = graphene.List(
        TagType,
        description="Get all tags"
    )
    
    # Sizes
    all_sizes = graphene.List(
        SizeType,
        category_id=graphene.ID(),
        category_slug=graphene.String(),
        description="Get all sizes (filterable by category ID or slug)"
    )
    
    size = graphene.Field(
        SizeType,
        id=graphene.ID(required=True),
        description="Get a single size by ID"
    )
    
    # Toppings
    all_toppings = graphene.List(
        ToppingType,
        description="Get all toppings"
    )
    
    topping = graphene.Field(
        ToppingType,
        id=graphene.ID(required=True),
        description="Get a single topping by ID"
    )
    
    # Included Items
    all_included_items = graphene.List(
        IncludedItemType,
        description="Get all included items for combos"
    )
    
    included_item = graphene.Field(
        IncludedItemType,
        id=graphene.ID(required=True),
        description="Get a single included item by ID"
    )
    
    # Ingredients
    all_ingredients = graphene.List(
        IngredientType,
        description="Get all ingredients"
    )
    
    ingredient = graphene.Field(
        IngredientType,
        id=graphene.ID(required=True),
        description="Get a single ingredient by ID"
    )
    
    # Featured products
    featured_products = graphene.List(
        ProductType,
        limit=graphene.Int(),
        description="Get featured products"
    )
    
    # Top rated products
    top_rated_products = graphene.List(
        ProductType,
        limit=graphene.Int(),
        description="Get top rated products"
    )
    
    # Product reviews
    product_reviews = graphene.List(
        ProductReviewType,
        product_id=graphene.ID(required=True),
        approved_only=graphene.Boolean(default_value=True),
        description="Get reviews for a product"
    )
    
    # Review management queries (admin/staff only)
    all_reviews = graphene.List(
        ProductReviewType,
        approved_only=graphene.Boolean(),
        product_id=graphene.ID(),
        rating=graphene.Int(),
        description="Get all reviews (admin/staff only)"
    )
    
    pending_reviews = graphene.List(
        ProductReviewType,
        description="Get pending reviews awaiting approval (admin/staff only)"
    )
    
    review = graphene.Field(
        ProductReviewType,
        id=graphene.ID(required=True),
        description="Get a single review by ID (admin/staff only)"
    )
    
    # Resolvers
    def resolve_product(self, info, id):
        """Get single product by ID"""
        try:
            return Product.objects.get(pk=id, is_available=True)
        except Product.DoesNotExist:
            return None
    
    def resolve_all_products(self, info, **kwargs):
        """Get all products"""
        return Product.objects.all()
    
    def resolve_products_by_category(self, info, category_id=None, category_name=None, category_slug=None):
        """Get products by category"""
        filters = {'is_available': True}
        if category_id:
            filters['category_id'] = category_id
        elif category_name:
            filters['category__name__icontains'] = category_name
        elif category_slug:
            filters['category__slug'] = category_slug
        return Product.objects.filter(**filters)
    
    def resolve_products_by_tag(self, info, tag_id=None, tag_name=None, tag_slug=None):
        """Get products by tag"""
        filters = {'is_available': True}
        if tag_id:
            filters['tags__id'] = tag_id
        elif tag_name:
            filters['tags__name__icontains'] = tag_name
        elif tag_slug:
            filters['tags__slug'] = tag_slug
        return Product.objects.filter(**filters)
    
    def resolve_search_products(self, info, search):
        """Search products by name or description (basic search)"""
        return Product.objects.filter(
            Q(name__icontains=search) | Q(description__icontains=search),
            is_available=True
        ).distinct()
    
    def resolve_fuzzy_search(self, info, query, limit=20, include_unavailable=False):
        """Advanced fuzzy search with relevance scoring"""
        return fuzzy_search_products(query, limit=limit, include_unavailable=include_unavailable)
    
    def resolve_search_suggestions(self, info, query, limit=10):
        """Get search suggestions for autocomplete"""
        suggestions = get_search_suggestions(query, limit=limit)
        
        # Group suggestions by type
        products = [s for s in suggestions if s['type'] == 'product']
        categories = [s for s in suggestions if s['type'] == 'category']
        tags = [s for s in suggestions if s['type'] == 'tag']
        
        return SearchSuggestionsType(
            query=query,
            suggestions=[SearchSuggestionItemType(**s) for s in suggestions],
            products=[SearchSuggestionItemType(**s) for s in products],
            categories=[SearchSuggestionItemType(**s) for s in categories],
            tags=[SearchSuggestionItemType(**s) for s in tags],
            total_count=len(suggestions)
        )
    
    def resolve_popular_searches(self, info):
        """Get popular/trending search terms"""
        popular = get_popular_searches()
        return [PopularSearchType(**p) for p in popular]
    
    def resolve_available_products(self, info):
        """Get only available products"""
        return Product.objects.filter(is_available=True)
    
    def resolve_all_categories(self, info):
        """Get all categories"""
        return Category.objects.all()
    
    def resolve_category(self, info, id=None, slug=None):
        """Get single category by ID or slug"""
        if id:
            return Category.objects.filter(pk=id).first()
        if slug:
            return Category.objects.filter(slug=slug).first()
            return None
    
    def resolve_all_tags(self, info):
        """Get all tags"""
        return Tag.objects.all()
    
    def resolve_all_sizes(self, info, category_id=None, category_slug=None):
        """Get all sizes, optionally filtered by category"""
        if category_id:
            return Size.objects.filter(category_id=category_id)
        if category_slug:
            return Size.objects.filter(category__slug=category_slug)
        return Size.objects.all()
    
    def resolve_size(self, info, id):
        """Get single size by ID"""
        try:
            return Size.objects.get(pk=id)
        except Size.DoesNotExist:
            return None
    
    def resolve_all_toppings(self, info):
        """Get all toppings"""
        return Topping.objects.all()
    
    def resolve_topping(self, info, id):
        """Get single topping by ID"""
        try:
            return Topping.objects.get(pk=id)
        except Topping.DoesNotExist:
            return None
    
    def resolve_all_included_items(self, info):
        """Get all included items"""
        return IncludedItem.objects.all()
    
    def resolve_included_item(self, info, id):
        """Get single included item by ID"""
        try:
            return IncludedItem.objects.get(pk=id)
        except IncludedItem.DoesNotExist:
            return None
    
    def resolve_all_ingredients(self, info):
        """Get all ingredients"""
        return Ingredient.objects.all()
    
    def resolve_ingredient(self, info, id):
        """Get single ingredient by ID"""
        try:
            return Ingredient.objects.get(pk=id)
        except Ingredient.DoesNotExist:
            return None
    
    def resolve_featured_products(self, info, limit=10):
        """Get featured products"""
        return Product.objects.filter(is_featured=True, is_available=True)[:limit]
    
    def resolve_top_rated_products(self, info, limit=10):
        """Get top rated products"""
        return Product.objects.filter(
            is_available=True, 
            rating_count__gt=0
        ).order_by('-average_rating')[:limit]
    
    def resolve_product_reviews(self, info, product_id, approved_only=True):
        """Get reviews for a product"""
        queryset = ProductReview.objects.filter(product_id=product_id)
        if approved_only:
            queryset = queryset.filter(is_approved=True)
        return queryset.order_by('-created_at')
    
    def resolve_all_reviews(self, info, approved_only=None, product_id=None, rating=None):
        """Get all reviews (admin/staff only)"""
        user = info.context.user
        if not user.is_authenticated or not user.has_review_permission():
            raise GraphQLError("You don't have permission to view all reviews")
        
        queryset = ProductReview.objects.all()
        
        if approved_only is not None:
            queryset = queryset.filter(is_approved=approved_only)
        
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        if rating:
            queryset = queryset.filter(rating=rating)
        
        return queryset.order_by('-created_at')
    
    def resolve_pending_reviews(self, info):
        """Get pending reviews awaiting approval (admin/staff only)"""
        user = info.context.user
        if not user.is_authenticated or not user.has_review_permission():
            raise GraphQLError("You don't have permission to view pending reviews")
        
        return ProductReview.objects.filter(is_approved=False).order_by('-created_at')
    
    def resolve_review(self, info, id):
        """Get a single review by ID (admin/staff only)"""
        user = info.context.user
        if not user.is_authenticated or not user.has_review_permission():
            raise GraphQLError("You don't have permission to view review details")
        
        try:
            return ProductReview.objects.get(pk=id)
        except ProductReview.DoesNotExist:
            return None


# ==================== Mutations ====================

class CreateCategory(graphene.Mutation):
    """Create a new category (Admin only)"""
    class Arguments:
        input = CategoryInput(required=True)
    
    category = graphene.Field(CategoryType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, input):
        from django.utils.text import slugify
        
        # Check if user is admin
        user = info.context.user
        if not user.is_authenticated or not user.has_category_permission():
            raise GraphQLError("You don't have permission to create categories")
        
        name = input.get('name')
        slug = input.get('slug') or slugify(name)
        
        # Check if category already exists
        if Category.objects.filter(name__iexact=name).exists():
            raise GraphQLError("A category with this name already exists")
        
        category = Category.objects.create(
            name=name,
            slug=slug,
            description=input.get('description', '')
        )
        return CreateCategory(category=category, success=True, message="Category created successfully")


class UpdateCategory(graphene.Mutation):
    """Update a category (Admin only)"""
    class Arguments:
        id = graphene.ID(required=True)
        input = CategoryInput(required=True)
    
    category = graphene.Field(CategoryType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, id, input):
        from django.utils.text import slugify
        
        user = info.context.user
        if not user.is_authenticated or not user.has_category_permission():
            raise GraphQLError("You don't have permission to update categories")
        
        try:
            category = Category.objects.get(pk=id)
            if input.get('name'):
                category.name = input.get('name')
                if not input.get('slug'):
                    category.slug = slugify(input.get('name'))
            if input.get('slug'):
                category.slug = input.get('slug')
            if input.get('description') is not None:
                category.description = input.get('description')
            category.save()
            return UpdateCategory(category=category, success=True, message="Category updated successfully")
        except Category.DoesNotExist:
            raise GraphQLError("Category not found")


class DeleteCategory(graphene.Mutation):
    """Delete a category (Admin only)"""
    class Arguments:
        id = graphene.ID(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, id):
        user = info.context.user
        if not user.is_authenticated or not user.has_category_permission():
            raise GraphQLError("You don't have permission to delete categories")
        
        try:
            category = Category.objects.get(pk=id)
            category.delete()
            return DeleteCategory(success=True, message="Category deleted successfully")
        except Category.DoesNotExist:
            raise GraphQLError("Category not found")


class CreateTag(graphene.Mutation):
    """Create a new tag (Admin only)"""
    class Arguments:
        input = TagInput(required=True)
    
    tag = graphene.Field(TagType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, input):
        user = info.context.user
        if not user.is_authenticated or not user.has_product_permission():
            raise GraphQLError("You don't have permission to create tags")
        
        tag = Tag.objects.create(
            name=input.get('name'),
            slug=input.get('slug', ''),
            color=input.get('color', '#000000')
        )
        return CreateTag(tag=tag, success=True, message="Tag created successfully")


class UpdateTag(graphene.Mutation):
    """Update a tag (Admin only)"""
    class Arguments:
        id = graphene.ID(required=True)
        input = TagInput(required=True)
    
    tag = graphene.Field(TagType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, id, input):
        user = info.context.user
        if not user.is_authenticated or not user.has_product_permission():
            raise GraphQLError("You don't have permission to update tags")
        
        try:
            tag = Tag.objects.get(pk=id)
            tag.name = input.get('name', tag.name)
            tag.slug = input.get('slug', tag.slug)
            tag.color = input.get('color', tag.color)
            tag.save()
            return UpdateTag(tag=tag, success=True, message="Tag updated successfully")
        except Tag.DoesNotExist:
            raise GraphQLError("Tag not found")


class DeleteTag(graphene.Mutation):
    """Delete a tag (Admin only)"""
    class Arguments:
        id = graphene.ID(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, id):
        user = info.context.user
        if not user.is_authenticated or not user.has_product_permission():
            raise GraphQLError("You don't have permission to delete tags")
        
        try:
            tag = Tag.objects.get(pk=id)
            tag.delete()
            return DeleteTag(success=True, message="Tag deleted successfully")
        except Tag.DoesNotExist:
            raise GraphQLError("Tag not found")


class CreateProduct(graphene.Mutation):
    """Create a new product (Admin only)"""
    class Arguments:
        input = ProductInput(required=True)
    
    product = graphene.Field(ProductType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, input):
        user = info.context.user
        if not user.is_authenticated or not user.has_product_permission():
            raise GraphQLError("You don't have permission to create products")
        
        try:
            category = Category.objects.get(pk=input.get('category_id'))
            product = Product.objects.create(
                name=input.get('name'),
                short_description=input.get('short_description', ''),
                description=input.get('description', ''),
                base_price=input.get('base_price'),
                category=category,
                is_available=input.get('is_available', True),
                is_featured=input.get('is_featured', False),
                is_combo=input.get('is_combo', False),
                prep_time_min=input.get('prep_time_min', 15),
                prep_time_max=input.get('prep_time_max', 20),
                calories=input.get('calories'),
                sale_price=input.get('sale_price'),
                sale_start_date=input.get('sale_start_date'),
                sale_end_date=input.get('sale_end_date')
            )
            
            # Handle image upload if provided
            if input.get('image'):
                save_base64_image(product, input.get('image'))
                product.save()
            
            # Add tags if provided
            if input.get('tag_ids'):
                tags = Tag.objects.filter(pk__in=input.get('tag_ids'))
                product.tags.set(tags)
            
            # Add ingredients if provided
            if input.get('ingredient_ids'):
                ingredients = Ingredient.objects.filter(pk__in=input.get('ingredient_ids'))
                product.ingredients.set(ingredients)
            
            # Add included items if provided
            if input.get('included_item_ids'):
                items = IncludedItem.objects.filter(pk__in=input.get('included_item_ids'))
                product.included_items.set(items)
            
            # Add sizes if provided
            if input.get('size_ids'):
                sizes = Size.objects.filter(pk__in=input.get('size_ids'))
                product.available_sizes.set(sizes)
            
            # Add toppings if provided
            if input.get('topping_ids'):
                toppings = Topping.objects.filter(pk__in=input.get('topping_ids'))
                product.available_toppings.set(toppings)
            
            return CreateProduct(product=product, success=True, message="Product created successfully")
        except Category.DoesNotExist:
            raise GraphQLError("Category not found")


class UpdateProduct(graphene.Mutation):
    """Update a product (Admin only)"""
    class Arguments:
        id = graphene.ID(required=True)
        input = ProductInput(required=True)
    
    product = graphene.Field(ProductType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, id, input):
        user = info.context.user
        if not user.is_authenticated or not user.has_product_permission():
            raise GraphQLError("You don't have permission to update products")
        
        try:
            product = Product.objects.get(pk=id)
            
            # Update basic fields
            if input.get('name'):
                product.name = input.get('name')
            if input.get('short_description') is not None:
                product.short_description = input.get('short_description')
            if input.get('description') is not None:
                product.description = input.get('description')
            if input.get('base_price'):
                product.base_price = input.get('base_price')
            if input.get('is_available') is not None:
                product.is_available = input.get('is_available')
            if input.get('is_featured') is not None:
                product.is_featured = input.get('is_featured')
            if input.get('is_combo') is not None:
                product.is_combo = input.get('is_combo')
            if input.get('prep_time_min') is not None:
                product.prep_time_min = input.get('prep_time_min')
            if input.get('prep_time_max') is not None:
                product.prep_time_max = input.get('prep_time_max')
            if input.get('calories') is not None:
                product.calories = input.get('calories')
            if input.get('category_id'):
                category = Category.objects.get(pk=input.get('category_id'))
                product.category = category
            
            # Handle sale pricing
            if input.get('sale_price') is not None:
                product.sale_price = input.get('sale_price')
            if input.get('sale_start_date') is not None:
                product.sale_start_date = input.get('sale_start_date')
            if input.get('sale_end_date') is not None:
                product.sale_end_date = input.get('sale_end_date')
            
            # Handle image upload if provided
            if input.get('image'):
                save_base64_image(product, input.get('image'))
            
            product.save()
            
            # Update tags if provided
            if input.get('tag_ids') is not None:
                tags = Tag.objects.filter(pk__in=input.get('tag_ids'))
                product.tags.set(tags)
            
            # Update ingredients if provided
            if input.get('ingredient_ids') is not None:
                ingredients = Ingredient.objects.filter(pk__in=input.get('ingredient_ids'))
                product.ingredients.set(ingredients)
            
            # Update included items if provided
            if input.get('included_item_ids') is not None:
                items = IncludedItem.objects.filter(pk__in=input.get('included_item_ids'))
                product.included_items.set(items)
            
            # Update sizes if provided
            if input.get('size_ids') is not None:
                sizes = Size.objects.filter(pk__in=input.get('size_ids'))
                product.available_sizes.set(sizes)
            
            # Update toppings if provided
            if input.get('topping_ids') is not None:
                toppings = Topping.objects.filter(pk__in=input.get('topping_ids'))
                product.available_toppings.set(toppings)
            
            return UpdateProduct(product=product, success=True, message="Product updated successfully")
        except Product.DoesNotExist:
            raise GraphQLError("Product not found")
        except Category.DoesNotExist:
            raise GraphQLError("Category not found")


class DeleteProduct(graphene.Mutation):
    """Delete a product (Admin only)"""
    class Arguments:
        id = graphene.ID(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, id):
        user = info.context.user
        if not user.is_authenticated or not user.has_product_permission():
            raise GraphQLError("You don't have permission to delete products")
        
        try:
            product = Product.objects.get(pk=id)
            product.delete()
            return DeleteProduct(success=True, message="Product deleted successfully")
        except Product.DoesNotExist:
            raise GraphQLError("Product not found")


# ==================== Size Mutations ====================

class CreateSize(graphene.Mutation):
    """Create a new size (Admin only)"""
    class Arguments:
        input = SizeInput(required=True)
    
    size = graphene.Field(SizeType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, input):
        user = info.context.user
        if not user.is_authenticated or not user.has_product_permission():
            raise GraphQLError("You don't have permission to create sizes")
        
        name = input.get('name')
        category_id = input.get('category_id')
        
        # Validate category exists
        try:
            category = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            raise GraphQLError("Category not found")
        
        # Check if size already exists for this category
        if Size.objects.filter(name__iexact=name, category=category).exists():
            raise GraphQLError(f"A size '{name}' already exists for {category.name}")
        
        size = Size.objects.create(
            name=name,
            category=category,
            price_modifier=input.get('price_modifier', 0),
            display_order=input.get('display_order', 0)
        )
        return CreateSize(size=size, success=True, message="Size created successfully")


class UpdateSize(graphene.Mutation):
    """Update a size (Admin only)"""
    class Arguments:
        id = graphene.ID(required=True)
        input = SizeInput(required=True)
    
    size = graphene.Field(SizeType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, id, input):
        user = info.context.user
        if not user.is_authenticated or not user.has_product_permission():
            raise GraphQLError("You don't have permission to update sizes")
        
        try:
            size = Size.objects.get(pk=id)
            if input.get('name'):
                size.name = input.get('name')
            if input.get('category_id'):
                try:
                    category = Category.objects.get(pk=input.get('category_id'))
                    size.category = category
                except Category.DoesNotExist:
                    raise GraphQLError("Category not found")
            if input.get('price_modifier') is not None:
                size.price_modifier = input.get('price_modifier')
            if input.get('display_order') is not None:
                size.display_order = input.get('display_order')
            size.save()
            return UpdateSize(size=size, success=True, message="Size updated successfully")
        except Size.DoesNotExist:
            raise GraphQLError("Size not found")


class DeleteSize(graphene.Mutation):
    """Delete a size (Admin only)"""
    class Arguments:
        id = graphene.ID(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, id):
        user = info.context.user
        if not user.is_authenticated or not user.has_product_permission():
            raise GraphQLError("You don't have permission to delete sizes")
        
        try:
            size = Size.objects.get(pk=id)
            size.delete()
            return DeleteSize(success=True, message="Size deleted successfully")
        except Size.DoesNotExist:
            raise GraphQLError("Size not found")


# ==================== Topping Mutations ====================

class CreateTopping(graphene.Mutation):
    """Create a new topping (Admin only)"""
    class Arguments:
        input = ToppingInput(required=True)
    
    topping = graphene.Field(ToppingType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, input):
        user = info.context.user
        if not user.is_authenticated or not user.has_product_permission():
            raise GraphQLError("You don't have permission to create toppings")
        
        name = input.get('name')
        
        # Check if topping already exists
        if Topping.objects.filter(name__iexact=name).exists():
            raise GraphQLError("A topping with this name already exists")
        
        topping = Topping.objects.create(
            name=name,
            price=input.get('price')
        )
        return CreateTopping(topping=topping, success=True, message="Topping created successfully")


class UpdateTopping(graphene.Mutation):
    """Update a topping (Admin only)"""
    class Arguments:
        id = graphene.ID(required=True)
        input = ToppingInput(required=True)
    
    topping = graphene.Field(ToppingType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, id, input):
        user = info.context.user
        if not user.is_authenticated or not user.has_product_permission():
            raise GraphQLError("You don't have permission to update toppings")
        
        try:
            topping = Topping.objects.get(pk=id)
            if input.get('name'):
                topping.name = input.get('name')
            if input.get('price') is not None:
                topping.price = input.get('price')
            topping.save()
            return UpdateTopping(topping=topping, success=True, message="Topping updated successfully")
        except Topping.DoesNotExist:
            raise GraphQLError("Topping not found")


class DeleteTopping(graphene.Mutation):
    """Delete a topping (Admin only)"""
    class Arguments:
        id = graphene.ID(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, id):
        user = info.context.user
        if not user.is_authenticated or not user.has_product_permission():
            raise GraphQLError("You don't have permission to delete toppings")
        
        try:
            topping = Topping.objects.get(pk=id)
            topping.delete()
            return DeleteTopping(success=True, message="Topping deleted successfully")
        except Topping.DoesNotExist:
            raise GraphQLError("Topping not found")


# ==================== Included Item Mutations ====================

class CreateIncludedItem(graphene.Mutation):
    """Create a new included item for combos (Admin only)"""
    class Arguments:
        input = IncludedItemInput(required=True)
    
    included_item = graphene.Field(IncludedItemType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, input):
        user = info.context.user
        if not user.is_authenticated or not user.has_product_permission():
            raise GraphQLError("You don't have permission to create included items")
        
        name = input.get('name')
        
        # Check if item already exists
        if IncludedItem.objects.filter(name__iexact=name).exists():
            raise GraphQLError("An included item with this name already exists")
        
        item = IncludedItem.objects.create(name=name)
        return CreateIncludedItem(included_item=item, success=True, message="Included item created successfully")


class UpdateIncludedItem(graphene.Mutation):
    """Update an included item (Admin only)"""
    class Arguments:
        id = graphene.ID(required=True)
        input = IncludedItemInput(required=True)
    
    included_item = graphene.Field(IncludedItemType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, id, input):
        user = info.context.user
        if not user.is_authenticated or not user.has_product_permission():
            raise GraphQLError("You don't have permission to update included items")
        
        try:
            item = IncludedItem.objects.get(pk=id)
            if input.get('name'):
                item.name = input.get('name')
            item.save()
            return UpdateIncludedItem(included_item=item, success=True, message="Included item updated successfully")
        except IncludedItem.DoesNotExist:
            raise GraphQLError("Included item not found")


class DeleteIncludedItem(graphene.Mutation):
    """Delete an included item (Admin only)"""
    class Arguments:
        id = graphene.ID(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, id):
        user = info.context.user
        if not user.is_authenticated or not user.has_product_permission():
            raise GraphQLError("You don't have permission to delete included items")
        
        try:
            item = IncludedItem.objects.get(pk=id)
            item.delete()
            return DeleteIncludedItem(success=True, message="Included item deleted successfully")
        except IncludedItem.DoesNotExist:
            raise GraphQLError("Included item not found")


# ==================== Ingredient Mutations ====================

class CreateIngredient(graphene.Mutation):
    """Create a new ingredient (Admin only)"""
    class Arguments:
        input = IngredientInput(required=True)
    
    ingredient = graphene.Field(IngredientType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, input):
        user = info.context.user
        if not user.is_authenticated or not user.has_product_permission():
            raise GraphQLError("You don't have permission to create ingredients")
        
        name = input.get('name')
        
        if Ingredient.objects.filter(name__iexact=name).exists():
            raise GraphQLError("An ingredient with this name already exists")
        
        ingredient = Ingredient.objects.create(
            name=name,
            icon=input.get('icon', '')
        )
        return CreateIngredient(ingredient=ingredient, success=True, message="Ingredient created successfully")


class UpdateIngredient(graphene.Mutation):
    """Update an ingredient (Admin only)"""
    class Arguments:
        id = graphene.ID(required=True)
        input = IngredientInput(required=True)
    
    ingredient = graphene.Field(IngredientType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, id, input):
        user = info.context.user
        if not user.is_authenticated or not user.has_product_permission():
            raise GraphQLError("You don't have permission to update ingredients")
        
        try:
            ingredient = Ingredient.objects.get(pk=id)
            if input.get('name'):
                ingredient.name = input.get('name')
            if input.get('icon') is not None:
                ingredient.icon = input.get('icon')
            ingredient.save()
            return UpdateIngredient(ingredient=ingredient, success=True, message="Ingredient updated successfully")
        except Ingredient.DoesNotExist:
            raise GraphQLError("Ingredient not found")


class DeleteIngredient(graphene.Mutation):
    """Delete an ingredient (Admin only)"""
    class Arguments:
        id = graphene.ID(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, id):
        user = info.context.user
        if not user.is_authenticated or not user.has_product_permission():
            raise GraphQLError("You don't have permission to delete ingredients")
        
        try:
            ingredient = Ingredient.objects.get(pk=id)
            ingredient.delete()
            return DeleteIngredient(success=True, message="Ingredient deleted successfully")
        except Ingredient.DoesNotExist:
            raise GraphQLError("Ingredient not found")


# ==================== Product Review Mutations ====================

class SubmitReview(graphene.Mutation):
    """Submit a product review (public - requires approval)"""
    class Arguments:
        input = ProductReviewInput(required=True)
    
    review = graphene.Field(ProductReviewType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, input):
        product_id = input.get('product_id')
        rating = input.get('rating')
        
        # Validate product exists
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            raise GraphQLError("Product not found")
        
        # Validate rating
        if rating < 1 or rating > 5:
            raise GraphQLError("Rating must be between 1 and 5")
        
        review = ProductReview.objects.create(
            product=product,
            customer_name=input.get('customer_name'),
            customer_email=input.get('customer_email'),
            rating=rating,
            comment=input.get('comment', ''),
            is_approved=False  # Requires admin approval
        )
        
        return SubmitReview(
            review=review,
            success=True,
            message="Review submitted successfully. It will be visible after approval."
        )


class ApproveReview(graphene.Mutation):
    """Approve a product review (Admin only)"""
    class Arguments:
        id = graphene.ID(required=True)
        approve = graphene.Boolean(required=True)
    
    review = graphene.Field(ProductReviewType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, id, approve):
        user = info.context.user
        if not user.is_authenticated or not user.has_review_permission():
            raise GraphQLError("You don't have permission to approve reviews")
        
        try:
            review = ProductReview.objects.get(pk=id)
            review.is_approved = approve
            review.save()
            
            # Update product rating
            review.product.update_rating()
            
            status = "approved" if approve else "rejected"
            return ApproveReview(review=review, success=True, message=f"Review {status}")
        except ProductReview.DoesNotExist:
            raise GraphQLError("Review not found")


class DeleteReview(graphene.Mutation):
    """Delete a product review (Admin only)"""
    class Arguments:
        id = graphene.ID(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, id):
        user = info.context.user
        if not user.is_authenticated or not user.has_review_permission():
            raise GraphQLError("You don't have permission to delete reviews")
        
        try:
            review = ProductReview.objects.get(pk=id)
            product = review.product
            review.delete()
            
            # Update product rating
            product.update_rating()
            
            return DeleteReview(success=True, message="Review deleted successfully")
        except ProductReview.DoesNotExist:
            raise GraphQLError("Review not found")


class ProductsMutation(graphene.ObjectType):
    """All product-related mutations"""
    # Category management
    create_category = CreateCategory.Field()
    update_category = UpdateCategory.Field()
    delete_category = DeleteCategory.Field()
    
    # Tag management
    create_tag = CreateTag.Field()
    update_tag = UpdateTag.Field()
    delete_tag = DeleteTag.Field()
    
    # Size management
    create_size = CreateSize.Field()
    update_size = UpdateSize.Field()
    delete_size = DeleteSize.Field()
    
    # Topping management
    create_topping = CreateTopping.Field()
    update_topping = UpdateTopping.Field()
    delete_topping = DeleteTopping.Field()
    
    # Ingredient management
    create_ingredient = CreateIngredient.Field()
    update_ingredient = UpdateIngredient.Field()
    delete_ingredient = DeleteIngredient.Field()
    
    # Included item management
    create_included_item = CreateIncludedItem.Field()
    update_included_item = UpdateIncludedItem.Field()
    delete_included_item = DeleteIncludedItem.Field()
    
    # Product management
    create_product = CreateProduct.Field()
    update_product = UpdateProduct.Field()
    delete_product = DeleteProduct.Field()
    
    # Review management
    submit_review = SubmitReview.Field()
    approve_review = ApproveReview.Field()
    delete_review = DeleteReview.Field()