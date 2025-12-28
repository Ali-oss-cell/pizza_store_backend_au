from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, Size, Topping, Tag, IncludedItem, Ingredient, ProductReview


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'product_count', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color_preview', 'product_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    
    def color_preview(self, obj):
        return format_html(
            '<span style="background-color: {}; padding: 2px 10px; border-radius: 3px;">{}</span>',
            obj.color, obj.color
        )
    color_preview.short_description = 'Color'
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


@admin.register(IncludedItem)
class IncludedItemAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'product_count']
    search_fields = ['name']
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Used In'


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price_modifier', 'display_order']
    list_filter = ['category']
    ordering = ['category', 'display_order']


@admin.register(Topping)
class ToppingAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'created_at']
    search_fields = ['name']


class ProductReviewInline(admin.TabularInline):
    model = ProductReview
    extra = 0
    readonly_fields = ['customer_name', 'customer_email', 'rating', 'comment', 'created_at']
    can_delete = True
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'price_display', 'sale_badge', 'rating_display', 
        'prep_time', 'is_available', 'is_featured', 'created_at'
    ]
    list_filter = ['category', 'tags', 'is_available', 'is_featured', 'is_combo']
    search_fields = ['name', 'description', 'short_description']
    filter_horizontal = ['tags', 'ingredients', 'included_items', 'available_sizes', 'available_toppings']
    readonly_fields = ['average_rating', 'rating_count']
    
    inlines = [ProductReviewInline]
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'short_description', 'description', 'category', 'tags', 'image')
        }),
        ('Pricing', {
            'fields': ('base_price', 'sale_price', 'sale_start_date', 'sale_end_date', 'available_sizes')
        }),
        ('Ingredients & Details', {
            'fields': ('ingredients', 'prep_time_min', 'prep_time_max', 'calories')
        }),
        ('Customization', {
            'fields': ('available_toppings',),
            'classes': ('collapse',)
        }),
        ('Combo Options', {
            'fields': ('is_combo', 'included_items'),
            'classes': ('collapse',)
        }),
        ('Status & Ratings', {
            'fields': ('is_available', 'is_featured', 'average_rating', 'rating_count')
        }),
    )
    
    def rating_display(self, obj):
        if obj.rating_count > 0:
            return format_html(
                '<span style="color: #f1c40f;">★</span> {} ({} reviews)',
                obj.average_rating, obj.rating_count
            )
        return format_html('<span style="color: #95a5a6;">No ratings</span>')
    rating_display.short_description = 'Rating'
    
    def prep_time(self, obj):
        return f"{obj.prep_time_min}-{obj.prep_time_max} min"
    prep_time.short_description = 'Prep Time'
    
    def price_display(self, obj):
        """Show current price with sale indicator"""
        if obj.is_on_sale:
            return format_html(
                '<span style="text-decoration: line-through; color: #95a5a6;">${}</span> '
                '<span style="color: #e74c3c; font-weight: bold;">${}</span>',
                obj.base_price, obj.sale_price
            )
        return f"${obj.base_price}"
    price_display.short_description = 'Price'
    
    def sale_badge(self, obj):
        """Show sale status badge"""
        if obj.is_on_sale:
            return format_html(
                '<span style="background-color: #e74c3c; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-size: 11px; font-weight: bold;">SALE</span>'
            )
        return format_html('<span style="color: #95a5a6;">—</span>')
    sale_badge.short_description = 'Sale'


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'customer_name', 'rating_stars', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'rating', 'created_at']
    search_fields = ['customer_name', 'customer_email', 'product__name', 'comment']
    readonly_fields = ['product', 'customer_name', 'customer_email', 'rating', 'comment', 'created_at']
    actions = ['approve_reviews', 'reject_reviews']
    
    def rating_stars(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color: #f1c40f;">{}</span>', stars)
    rating_stars.short_description = 'Rating'
    
    @admin.action(description='Approve selected reviews')
    def approve_reviews(self, request, queryset):
        for review in queryset:
            review.is_approved = True
            review.save()
        self.message_user(request, f'{queryset.count()} reviews approved.')
    
    @admin.action(description='Reject selected reviews')
    def reject_reviews(self, request, queryset):
        queryset.update(is_approved=False)
        # Update product ratings
        for review in queryset:
            review.product.update_rating()
        self.message_user(request, f'{queryset.count()} reviews rejected.')
    
    def has_add_permission(self, request):
        return False
