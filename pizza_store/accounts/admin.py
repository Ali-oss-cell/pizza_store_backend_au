from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for team member management"""
    
    list_display = [
        'username', 'full_name', 'email', 'role_badge', 
        'permissions_summary', 'is_active', 'created_at'
    ]
    list_filter = ['role', 'is_active', 'can_manage_orders', 'can_manage_products']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-created_at']
    list_per_page = 20
    
    # Customize fieldsets
    fieldsets = (
        ('Account Info', {
            'fields': ('username', 'email', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'phone')
        }),
        ('Role & Status', {
            'fields': ('role', 'is_active')
        }),
        ('Permissions', {
            'fields': (
                'can_manage_orders', 'can_manage_products', 
                'can_manage_categories', 'can_manage_promotions',
                'can_view_reports', 'can_manage_reviews'
            ),
            'description': 'Permissions only apply to Staff role. Admins have all permissions.'
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('date_joined', 'last_login', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login', 'created_at', 'updated_at']
    
    # Customize add form
    add_fieldsets = (
        ('Account Info', {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'phone')
        }),
        ('Role & Status', {
            'fields': ('role', 'is_active')
        }),
        ('Permissions', {
            'fields': (
                'can_manage_orders', 'can_manage_products', 
                'can_manage_categories', 'can_manage_promotions',
                'can_view_reports', 'can_manage_reviews'
            )
        }),
    )
    
    def full_name(self, obj):
        """Display full name or username if no name"""
        name = f"{obj.first_name} {obj.last_name}".strip()
        return name if name else obj.username
    full_name.short_description = 'Name'
    
    def role_badge(self, obj):
        """Display role with colored badge"""
        if obj.is_admin:
            return format_html(
                '<span style="background-color: #e74c3c; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-size: 11px; font-weight: bold;">ADMIN</span>'
            )
        return format_html(
            '<span style="background-color: #3498db; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">STAFF</span>'
        )
    role_badge.short_description = 'Role'
    
    def permissions_summary(self, obj):
        """Show summary of permissions"""
        if obj.is_admin:
            return format_html('<span style="color: #2ecc71;">All Permissions</span>')
        
        permissions = obj.get_permissions_list()
        if not permissions:
            return format_html('<span style="color: #95a5a6;">No permissions</span>')
        
        return format_html(
            '<span style="color: #3498db;">{}</span>',
            ', '.join(permissions)
        )
    permissions_summary.short_description = 'Permissions'
    