# accounts/management/commands/create_admin.py
"""
Django management command to create or update admin user with full privileges.

Usage:
    python manage.py create_admin
    python manage.py create_admin --username admin --email admin@store.com --password secure123
    python manage.py create_admin --username admin --password secure123 --update
"""
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from accounts.models import User


class Command(BaseCommand):
    help = 'Create or update an admin user with full privileges'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Username for admin account (default: admin)'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@marinapizzas.com.au',
            help='Email for admin account'
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Password for admin account (if not provided, will prompt)'
        )
        parser.add_argument(
            '--first-name',
            type=str,
            default='Admin',
            help='First name (default: Admin)'
        )
        parser.add_argument(
            '--last-name',
            type=str,
            default='User',
            help='Last name (default: User)'
        )
        parser.add_argument(
            '--phone',
            type=str,
            default='',
            help='Phone number (optional)'
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing user if found (default: skip if exists)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update even if user exists (same as --update)'
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options.get('password')
        first_name = options.get('first_name', 'Admin')
        last_name = options.get('last_name', 'User')
        phone = options.get('phone', '')
        update = options.get('update') or options.get('force')

        # Check if user exists
        try:
            user = User.objects.get(username=username)
            if not update:
                self.stdout.write(
                    self.style.WARNING(
                        f'User "{username}" already exists. Use --update to update it.'
                    )
                )
                return
            created = False
            self.stdout.write(f'Updating existing user: {username}')
        except User.DoesNotExist:
            user = None
            created = True
            self.stdout.write(f'Creating new admin user: {username}')

        # Get password if not provided
        if not password:
            import getpass
            password = getpass.getpass('Enter password: ')
            password_confirm = getpass.getpass('Confirm password: ')
            if password != password_confirm:
                self.stdout.write(
                    self.style.ERROR('Passwords do not match!')
                )
                return
            if len(password) < 8:
                self.stdout.write(
                    self.style.WARNING('Warning: Password is less than 8 characters')
                )

        # Create or update user
        if created:
            # Create new user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                role=User.Role.ADMIN
            )
        else:
            # Update existing user
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            if phone:
                user.phone = phone

        # Set admin privileges
        user.role = User.Role.ADMIN
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        
        # Set all permissions to True (for admin, all permissions are granted)
        user.can_manage_orders = True
        user.can_manage_products = True
        user.can_manage_categories = True
        user.can_manage_promotions = True
        user.can_view_reports = True
        user.can_manage_reviews = True

        # Set password
        user.set_password(password)
        user.save()

        # Verify the user
        user.refresh_from_db()

        # Display success message
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('✅ Admin user created/updated successfully!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'\n📋 Account Details:')
        self.stdout.write(f'   Username: {user.username}')
        self.stdout.write(f'   Email: {user.email}')
        self.stdout.write(f'   Password: {"*" * len(password)} (hidden)')
        self.stdout.write(f'   Role: {user.get_role_display()}')
        self.stdout.write(f'   Is Admin: {user.is_admin}')
        self.stdout.write(f'   Is Staff: {user.is_staff}')
        self.stdout.write(f'   Is Superuser: {user.is_superuser}')
        self.stdout.write(f'   Is Active: {user.is_active}')
        self.stdout.write(f'\n🔐 You can now login with these credentials!')
        self.stdout.write(f'\n💡 Use this account to create other users via GraphQL:')
        self.stdout.write(f'   mutation {{ register(input: {{ ... }}) {{ success user {{ id username }} }} }}')
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))
