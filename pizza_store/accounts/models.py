from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom User model with Admin/Staff roles
    AbstractUser already provides: username, email, password, first_name, last_name
    """
    
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        STAFF = 'staff', 'Staff'
    
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STAFF
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
        return self.username