#!/usr/bin/env python
"""
Script to create or update admin user
Run: python manage.py shell < create_admin.py
Or: python create_admin.py (if run from pizza_store directory)
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pizza_store.settings')
django.setup()

from accounts.models import User

def create_or_update_admin():
    username = 'admin'
    email = 'admin@admin.com'
    password = 'admin123'  # Change this to your preferred password
    
    # Try to get existing admin
    admin, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'role': User.Role.ADMIN,
            'is_staff': True,
            'is_superuser': True,
        }
    )
    
    if not created:
        # Update existing admin
        admin.email = email
        admin.role = User.Role.ADMIN
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()
        print(f"✅ Updated existing admin user: {username}")
    else:
        print(f"✅ Created new admin user: {username}")
    
    # Set password
    admin.set_password(password)
    admin.save()
    
    print(f"\n📋 Admin Account Details:")
    print(f"   Username: {username}")
    print(f"   Email: {email}")
    print(f"   Password: {password}")
    print(f"   Role: {admin.role}")
    print(f"   Is Admin: {admin.is_admin}")
    print(f"\n🔐 You can now login with these credentials!")

if __name__ == '__main__':
    create_or_update_admin()

