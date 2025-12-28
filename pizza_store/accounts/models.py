from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom User model with Admin/Staff roles and granular permissions.
    AbstractUser already provides: username, email, password, first_name, last_name
    
    Permission Hierarchy:
    - Admin: Full access to everything
    - Staff: Limited access based on individual permissions
    """
    
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        STAFF = 'staff', 'Staff'
    
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STAFF
    )
    
    # Contact info
    phone = models.CharField(max_length=20, blank=True)
    
    # Staff-specific permissions (only relevant for staff role)
    can_manage_orders = models.BooleanField(
        default=True,
        help_text="Can view and update order status"
    )
    can_manage_products = models.BooleanField(
        default=False,
        help_text="Can create, update, and delete products"
    )
    can_manage_categories = models.BooleanField(
        default=False,
        help_text="Can create, update, and delete categories"
    )
    can_manage_promotions = models.BooleanField(
        default=False,
        help_text="Can create, update, and delete promotions"
    )
    can_view_reports = models.BooleanField(
        default=False,
        help_text="Can view sales reports and analytics"
    )
    can_manage_reviews = models.BooleanField(
        default=True,
        help_text="Can approve or reject product reviews"
    )
    
    # Work schedule (optional)
    notes = models.TextField(
        blank=True,
        help_text="Admin notes about this team member"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def is_admin(self):
        """Check if user is an admin"""
        return self.role == self.Role.ADMIN
    
    @property
    def is_staff_member(self):
        """Check if user is staff (not admin)"""
        return self.role == self.Role.STAFF
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    # Permission check methods
    def has_order_permission(self):
        """Check if user can manage orders"""
        return self.is_admin or (self.is_staff_member and self.can_manage_orders)
    
    def has_product_permission(self):
        """Check if user can manage products"""
        return self.is_admin or (self.is_staff_member and self.can_manage_products)
    
    def has_category_permission(self):
        """Check if user can manage categories"""
        return self.is_admin or (self.is_staff_member and self.can_manage_categories)
    
    def has_promotion_permission(self):
        """Check if user can manage promotions"""
        return self.is_admin or (self.is_staff_member and self.can_manage_promotions)
    
    def has_report_permission(self):
        """Check if user can view reports"""
        return self.is_admin or (self.is_staff_member and self.can_view_reports)
    
    def has_review_permission(self):
        """Check if user can manage reviews"""
        return self.is_admin or (self.is_staff_member and self.can_manage_reviews)
    
    def get_permissions_list(self):
        """Get list of permissions for this user"""
        if self.is_admin:
            return ['all']
        
        permissions = []
        if self.can_manage_orders:
            permissions.append('orders')
        if self.can_manage_products:
            permissions.append('products')
        if self.can_manage_categories:
            permissions.append('categories')
        if self.can_manage_promotions:
            permissions.append('promotions')
        if self.can_view_reports:
            permissions.append('reports')
        if self.can_manage_reviews:
            permissions.append('reviews')
        return permissions