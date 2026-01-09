# inventory/admin.py
from django.contrib import admin
from .models import StockItem, StockMovement, StockAlert


@admin.register(StockItem)
class StockItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'reorder_level', 'is_low_stock', 'last_restocked', 'updated_at')
    list_filter = ('reorder_level', 'last_restocked')
    search_fields = ('product__name', 'product__sku', 'product__barcode')
    readonly_fields = ('created_at', 'updated_at', 'is_low_stock', 'is_out_of_stock')
    fieldsets = (
        ('Product', {
            'fields': ('product',)
        }),
        ('Stock Information', {
            'fields': ('quantity', 'reorder_level', 'reorder_quantity', 'last_restocked')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('stock_item', 'movement_type', 'quantity_change', 'quantity_before', 'quantity_after', 'reference', 'created_by', 'created_at')
    list_filter = ('movement_type', 'created_at')
    search_fields = ('stock_item__product__name', 'reference', 'notes')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Stock Item', {
            'fields': ('stock_item',)
        }),
        ('Movement Details', {
            'fields': ('movement_type', 'quantity_change', 'quantity_before', 'quantity_after')
        }),
        ('Reference Information', {
            'fields': ('reference', 'notes', 'created_by')
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )


@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = ('stock_item', 'status', 'message', 'created_at', 'acknowledged_at', 'resolved_at')
    list_filter = ('status', 'created_at')
    search_fields = ('stock_item__product__name', 'message')
    readonly_fields = ('created_at', 'acknowledged_at', 'resolved_at')
    fieldsets = (
        ('Stock Item', {
            'fields': ('stock_item',)
        }),
        ('Alert Information', {
            'fields': ('status', 'message')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'acknowledged_at', 'resolved_at')
        }),
    )
