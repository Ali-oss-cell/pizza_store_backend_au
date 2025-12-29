from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('product', 'size', 'quantity', 'unit_price', 'include_combo_items', 'is_combo_display')
    fields = ('product', 'size', 'quantity', 'unit_price', 'include_combo_items', 'is_combo_display')
    
    def is_combo_display(self, obj):
        if obj.include_combo_items and obj.product.is_combo:
            items = obj.selected_included_items or []
            item_names = [item.get('name', '') for item in items]
            return f"Yes - {', '.join(item_names)}" if item_names else "Yes"
        return "No"
    is_combo_display.short_description = 'Combo Order'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'session_key_display', 'item_count', 'total', 'created_at')
    readonly_fields = ('session_key', 'created_at', 'updated_at')
    inlines = [CartItemInline]
    
    def session_key_display(self, obj):
        return f"{obj.session_key[:8]}..."
    session_key_display.short_description = 'Session'
    
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'
    
    def total(self, obj):
        return f"${obj.get_total()}"
    total.short_description = 'Total'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'size', 'quantity', 'unit_price', 'combo_status', 'created_at')
    list_filter = ('include_combo_items', 'product__is_combo')
    search_fields = ('product__name',)
    readonly_fields = ('cart', 'product', 'size', 'selected_toppings', 'selected_included_items', 'created_at')
    
    def combo_status(self, obj):
        if obj.include_combo_items and obj.product.is_combo:
            return "✅ Combo"
        elif obj.product.is_combo:
            return "❌ Regular"
        return "—"
    combo_status.short_description = 'Combo Status'
