from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """Inline display of order items"""
    model = OrderItem
    extra = 0
    readonly_fields = [
        'product_name', 'product_id', 'is_combo', 'included_items',
        'size_name', 'selected_toppings', 'unit_price', 'quantity', 'subtotal'
    ]
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin interface for Order management"""
    
    list_display = [
        'order_number', 'status_badge', 'customer_name', 'customer_phone',
        'order_type_badge', 'total_display', 'time_since_order', 'created_at'
    ]
    list_filter = ['status', 'order_type', 'created_at']
    search_fields = ['order_number', 'customer_name', 'customer_email', 'customer_phone']
    readonly_fields = [
        'order_number', 'customer_name', 'customer_email', 'customer_phone',
        'order_type', 'delivery_address', 'delivery_instructions',
        'subtotal', 'delivery_fee', 'total', 'created_at', 'updated_at',
        'completed_at', 'cart_session_key'
    ]
    ordering = ['-created_at']
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Info', {
            'fields': ('order_number', 'status', 'order_type')
        }),
        ('Customer Details', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Delivery Info', {
            'fields': ('delivery_address', 'delivery_instructions'),
            'classes': ('collapse',)
        }),
        ('Pricing', {
            'fields': ('subtotal', 'delivery_fee', 'discount_code', 'discount_amount', 'total')
        }),
        ('Order Notes', {
            'fields': ('order_notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_confirmed', 'mark_preparing', 'mark_ready', 'mark_delivered', 'mark_cancelled']
    
    def status_badge(self, obj):
        """Display status with color-coded badge"""
        colors = {
            'pending': '#f39c12',      # Orange
            'confirmed': '#3498db',    # Blue
            'preparing': '#9b59b6',    # Purple
            'ready': '#2ecc71',        # Green
            'delivered': '#27ae60',    # Dark Green
            'picked_up': '#27ae60',    # Dark Green
            'cancelled': '#e74c3c',    # Red
        }
        color = colors.get(obj.status, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def order_type_badge(self, obj):
        """Display order type with icon"""
        if obj.order_type == 'delivery':
            return format_html('🚗 Delivery')
        return format_html('🏪 Pickup')
    order_type_badge.short_description = 'Type'
    
    def total_display(self, obj):
        """Display total with currency"""
        return format_html('<strong>${}</strong>', obj.total)
    total_display.short_description = 'Total'
    total_display.admin_order_field = 'total'
    
    def time_since_order(self, obj):
        """Display time since order was placed"""
        delta = timezone.now() - obj.created_at
        minutes = int(delta.total_seconds() / 60)
        
        if minutes < 60:
            time_str = f"{minutes} min"
            if minutes > 30:
                color = '#e74c3c'  # Red for old orders
            elif minutes > 15:
                color = '#f39c12'  # Orange
            else:
                color = '#2ecc71'  # Green
        else:
            hours = minutes // 60
            time_str = f"{hours}h {minutes % 60}m"
            color = '#e74c3c'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, time_str
        )
    time_since_order.short_description = 'Age'
    
    # Bulk actions for quick status updates
    @admin.action(description='Mark selected orders as Confirmed')
    def mark_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
        self.message_user(request, f'{queryset.count()} orders marked as confirmed.')
    
    @admin.action(description='Mark selected orders as Preparing')
    def mark_preparing(self, request, queryset):
        queryset.update(status='preparing')
        self.message_user(request, f'{queryset.count()} orders marked as preparing.')
    
    @admin.action(description='Mark selected orders as Ready')
    def mark_ready(self, request, queryset):
        queryset.update(status='ready')
        self.message_user(request, f'{queryset.count()} orders marked as ready.')
    
    @admin.action(description='Mark selected orders as Delivered/Picked Up')
    def mark_delivered(self, request, queryset):
        now = timezone.now()
        for order in queryset:
            if order.order_type == 'delivery':
                order.status = 'delivered'
            else:
                order.status = 'picked_up'
            order.completed_at = now
            order.save()
        self.message_user(request, f'{queryset.count()} orders marked as completed.')
    
    @admin.action(description='Cancel selected orders')
    def mark_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
        self.message_user(request, f'{queryset.count()} orders cancelled.')
    
    def save_model(self, request, obj, form, change):
        """Auto-set completed_at when order is delivered/picked up"""
        if obj.status in ['delivered', 'picked_up'] and not obj.completed_at:
            obj.completed_at = timezone.now()
        elif obj.status not in ['delivered', 'picked_up']:
            obj.completed_at = None
        super().save_model(request, obj, form, change)
    
    def has_delete_permission(self, request, obj=None):
        """Only admins can delete orders"""
        return request.user.is_superuser or getattr(request.user, 'is_admin', False)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Read-only admin for order items"""
    list_display = ['order', 'product_name', 'size_name', 'quantity', 'subtotal']
    list_filter = ['order__status']
    search_fields = ['product_name', 'order__order_number']
    readonly_fields = [
        'order', 'product_name', 'product_id', 'is_combo', 'included_items',
        'size_name', 'size_id', 'selected_toppings', 'unit_price', 'quantity', 'subtotal'
    ]
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
