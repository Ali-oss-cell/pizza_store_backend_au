from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import StoreSettings, Promotion


@admin.register(StoreSettings)
class StoreSettingsAdmin(admin.ModelAdmin):
    """Admin for Store Settings (singleton)"""
    
    fieldsets = (
        ('Store Information', {
            'fields': ('store_name', 'store_phone', 'store_email', 'store_address')
        }),
        ('Business Hours', {
            'fields': ('business_hours',),
            'description': 'JSON format: {"monday": {"open": "10:00", "close": "22:00"}, ...}'
        }),
        ('Order Settings', {
            'fields': ('accept_orders', 'delivery_enabled', 'pickup_enabled', 'order_notes_enabled')
        }),
        ('Delivery Settings', {
            'fields': (
                'delivery_fee', 'free_delivery_threshold', 'minimum_order_amount',
                'delivery_radius_km', 'estimated_delivery_time', 'estimated_pickup_time'
            )
        }),
        ('Tax Settings', {
            'fields': ('tax_rate', 'tax_included_in_prices')
        }),
    )
    
    def has_add_permission(self, request):
        """Prevent creating multiple settings instances"""
        return not StoreSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deleting settings"""
        return False


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    """Admin for Promotions/Coupons"""
    
    list_display = [
        'code', 'name', 'discount_display', 'status_badge', 
        'usage_display', 'valid_from', 'valid_until'
    ]
    list_filter = ['is_active', 'discount_type', 'valid_from', 'valid_until']
    search_fields = ['code', 'name', 'description']
    readonly_fields = ['times_used', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('code', 'name', 'description', 'is_active')
        }),
        ('Discount Details', {
            'fields': ('discount_type', 'discount_value', 'maximum_discount')
        }),
        ('Product Selection', {
            'fields': (
                'applicable_products', 'apply_to_entire_order',
                'apply_to_base_price', 'apply_to_toppings', 'apply_to_included_items'
            ),
            'description': 'Select specific products or leave empty to apply to all products. Choose what parts of the product to discount.'
        }),
        ('Conditions', {
            'fields': ('minimum_order_amount',)
        }),
        ('Usage Limits', {
            'fields': ('usage_limit', 'times_used')
        }),
        ('Validity Period', {
            'fields': ('valid_from', 'valid_until')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    filter_horizontal = ['applicable_products']
    
    def discount_display(self, obj):
        """Display discount with type"""
        if obj.discount_type == 'percentage':
            return f"{obj.discount_value}%"
        elif obj.discount_type == 'fixed':
            return f"${obj.discount_value}"
        else:
            return "Free Delivery"
    discount_display.short_description = 'Discount'
    
    def status_badge(self, obj):
        """Show active/expired/upcoming status"""
        now = timezone.now()
        
        if not obj.is_active:
            return format_html(
                '<span style="color: #95a5a6;">Inactive</span>'
            )
        
        if now < obj.valid_from:
            return format_html(
                '<span style="color: #3498db;">Upcoming</span>'
            )
        
        if now > obj.valid_until:
            return format_html(
                '<span style="color: #e74c3c;">Expired</span>'
            )
        
        if obj.usage_limit and obj.times_used >= obj.usage_limit:
            return format_html(
                '<span style="color: #f39c12;">Limit Reached</span>'
            )
        
        return format_html(
            '<span style="color: #2ecc71; font-weight: bold;">Active</span>'
        )
    status_badge.short_description = 'Status'
    
    def usage_display(self, obj):
        """Show usage count"""
        if obj.usage_limit:
            return f"{obj.times_used} / {obj.usage_limit}"
        return f"{obj.times_used} / ∞"
    usage_display.short_description = 'Usage'
