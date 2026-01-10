import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import AnonymousUser
from .models import User


# ==================== GraphQL Types ====================

class TeamStatsType(graphene.ObjectType):
    """GraphQL type for team statistics"""
    total_users = graphene.Int(description="Total number of users")
    admins = graphene.Int(description="Number of admin users")
    admins_count = graphene.Int(description="Number of admin users (alias)")
    staff = graphene.Int(description="Number of staff users")
    staff_count = graphene.Int(description="Number of staff users (alias)")
    active_users = graphene.Int(description="Number of active users")
    inactive_users = graphene.Int(description="Number of inactive users")
    
    def resolve_admins_count(self, info):
        """Alias for admins field"""
        return self.admins
    
    def resolve_staff_count(self, info):
        """Alias for staff field"""
        return self.staff


class UserType(DjangoObjectType):
    """GraphQL type for User"""
    is_admin = graphene.Boolean()
    is_staff_member = graphene.Boolean()
    permissions = graphene.List(graphene.String)
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'phone',
            'role', 'is_active', 'date_joined', 'created_at', 'updated_at',
            'can_manage_orders', 'can_manage_products', 'can_manage_categories',
            'can_manage_promotions', 'can_view_reports', 'can_manage_reviews', 'notes'
        )
        # Exclude sensitive fields like password
    
    def resolve_is_admin(self, info):
        """Check if user is admin"""
        return self.is_admin
    
    def resolve_is_staff_member(self, info):
        """Check if user is staff member"""
        return self.is_staff_member
    
    def resolve_permissions(self, info):
        """Get list of permissions"""
        return self.get_permissions_list()


# ==================== Input Types ====================

class LoginInput(graphene.InputObjectType):
    username = graphene.String(required=True)
    password = graphene.String(required=True)


class RegisterInput(graphene.InputObjectType):
    username = graphene.String(required=True)
    email = graphene.String(required=True)
    password = graphene.String(required=True)
    password_confirm = graphene.String(required=True)
    first_name = graphene.String()
    last_name = graphene.String()
    phone = graphene.String()
    role = graphene.String()  # Only admins can set role
    # Staff permissions (only for staff role)
    can_manage_orders = graphene.Boolean(default_value=True, description="Can view and update order status")
    can_manage_products = graphene.Boolean(default_value=False, description="Can create, update, delete products")
    can_manage_categories = graphene.Boolean(default_value=False, description="Can create, update, delete categories")
    can_manage_promotions = graphene.Boolean(default_value=False, description="Can create, update, delete promotions")
    can_view_reports = graphene.Boolean(default_value=False, description="Can view sales reports")
    can_manage_reviews = graphene.Boolean(default_value=False, description="Can approve or reject reviews")


class TeamMemberInput(graphene.InputObjectType):
    """Input for creating/updating team members"""
    username = graphene.String()
    email = graphene.String()
    password = graphene.String()
    first_name = graphene.String()
    last_name = graphene.String()
    phone = graphene.String()
    role = graphene.String()
    is_active = graphene.Boolean()
    # Permissions
    can_manage_orders = graphene.Boolean()
    can_manage_products = graphene.Boolean()
    can_manage_categories = graphene.Boolean()
    can_manage_promotions = graphene.Boolean()
    can_view_reports = graphene.Boolean()
    can_manage_reviews = graphene.Boolean()
    notes = graphene.String()


# ==================== Queries ====================

class AccountsQuery(graphene.ObjectType):
    """All account-related queries"""
    
    me = graphene.Field(
        UserType,
        description="Get current authenticated user"
    )
    
    # Team management queries (admin only)
    all_users = graphene.List(
        UserType,
        role=graphene.String(),
        is_active=graphene.Boolean(),
        description="Get all users (admin only)"
    )
    
    user = graphene.Field(
        UserType,
        id=graphene.ID(required=True),
        description="Get user by ID (admin only)"
    )
    
    team_stats = graphene.Field(
        TeamStatsType,
        description="Get team statistics (admin only)"
    )
    
    def resolve_me(self, info):
        """Get current user from session"""
        user = info.context.user
        
        # Check if user is authenticated
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return None
        
        return user
    
    def resolve_all_users(self, info, role=None, is_active=None):
        """Get all users (admin only)"""
        current_user = info.context.user
        
        if not current_user.is_authenticated:
            raise GraphQLError("Authentication required")
        
        if not current_user.is_admin:
            raise GraphQLError("Only admins can view all users")
        
        queryset = User.objects.all().order_by('-created_at')
        
        if role:
            queryset = queryset.filter(role=role)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset
    
    def resolve_user(self, info, id):
        """Get user by ID (admin only)"""
        current_user = info.context.user
        
        if not current_user.is_authenticated:
            raise GraphQLError("Authentication required")
        
        if not current_user.is_admin:
            raise GraphQLError("Only admins can view user details")
        
        try:
            return User.objects.get(pk=id)
        except User.DoesNotExist:
            return None
    
    def resolve_team_stats(self, info):
        """Get team statistics"""
        current_user = info.context.user
        
        if not current_user.is_authenticated:
            raise GraphQLError("Authentication required")
        
        if not current_user.is_admin:
            raise GraphQLError("Only admins can view team stats")
        
        return TeamStatsType(
            total_users=User.objects.count(),
            admins=User.objects.filter(role='admin').count(),
            staff=User.objects.filter(role='staff').count(),
            active_users=User.objects.filter(is_active=True).count(),
            inactive_users=User.objects.filter(is_active=False).count(),
        )


# ==================== Mutations ====================

class Login(graphene.Mutation):
    """Login mutation - authenticate user with username and password"""
    class Arguments:
        input = LoginInput(required=True)
    
    user = graphene.Field(UserType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, input):
        username = input.get('username')
        password = input.get('password')
        
        # Authenticate user
        user = authenticate(
            request=info.context,
            username=username,
            password=password
        )
        
        if user is None:
            raise GraphQLError("Invalid username or password")
        
        if not user.is_active:
            raise GraphQLError("User account is disabled")
        
        # Login user (creates session)
        login(info.context, user)
        
        return Login(
            user=user,
            success=True,
            message="Login successful"
        )


class Logout(graphene.Mutation):
    """Logout mutation - logout current user"""
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info):
        user = info.context.user
        
        if not user.is_authenticated:
            raise GraphQLError("User is not authenticated")
        
        # Logout user (destroys session)
        logout(info.context)
        
        return Logout(
            success=True,
            message="Logout successful"
        )


class Register(graphene.Mutation):
    """Register mutation - create new user (admin only for now)"""
    class Arguments:
        input = RegisterInput(required=True)
    
    user = graphene.Field(UserType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, input):
        # Check if user is admin (only admins can create users)
        current_user = info.context.user
        if not current_user.is_authenticated or not current_user.is_admin:
            raise GraphQLError("Only admins can create new users")
        
        username = input.get('username')
        email = input.get('email')
        password = input.get('password')
        password_confirm = input.get('password_confirm')
        first_name = input.get('first_name', '')
        last_name = input.get('last_name', '')
        role = input.get('role', User.Role.STAFF)
        
        # Validate passwords match
        if password != password_confirm:
            raise GraphQLError("Passwords do not match")
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            raise GraphQLError("Username already exists")
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            raise GraphQLError("Email already exists")
        
        # Validate role
        if role not in [User.Role.ADMIN, User.Role.STAFF]:
            raise GraphQLError("Invalid role. Must be 'admin' or 'staff'")
        
        # Get phone number
        phone = input.get('phone', '')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role=role
        )
        
        # Set permissions for staff users
        if role == User.Role.STAFF:
            user.can_manage_orders = input.get('can_manage_orders', True)
            user.can_manage_products = input.get('can_manage_products', False)
            user.can_manage_categories = input.get('can_manage_categories', False)
            user.can_manage_promotions = input.get('can_manage_promotions', False)
            user.can_view_reports = input.get('can_view_reports', False)
            user.can_manage_reviews = input.get('can_manage_reviews', False)
            user.save()
        
        return Register(
            user=user,
            success=True,
            message=f"{'Admin' if role == User.Role.ADMIN else 'Staff'} user created successfully"
        )


class ChangePassword(graphene.Mutation):
    """Change password mutation - change current user's password"""
    class Arguments:
        old_password = graphene.String(required=True)
        new_password = graphene.String(required=True)
        new_password_confirm = graphene.String(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, old_password, new_password, new_password_confirm):
        user = info.context.user
        
        if not user.is_authenticated:
            raise GraphQLError("User is not authenticated")
        
        # Validate old password
        if not user.check_password(old_password):
            raise GraphQLError("Current password is incorrect")
        
        # Validate new passwords match
        if new_password != new_password_confirm:
            raise GraphQLError("New passwords do not match")
        
        # Validate password length
        if len(new_password) < 8:
            raise GraphQLError("Password must be at least 8 characters long")
        
        # Set new password
        user.set_password(new_password)
        user.save()
        
        return ChangePassword(
            success=True,
            message="Password changed successfully"
        )


class UpdateUser(graphene.Mutation):
    """Update user mutation - update current user's profile"""
    class Arguments:
        email = graphene.String()
        first_name = graphene.String()
        last_name = graphene.String()
        phone = graphene.String()
    
    user = graphene.Field(UserType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, email=None, first_name=None, last_name=None, phone=None):
        current_user = info.context.user
        
        if not current_user.is_authenticated:
            raise GraphQLError("User is not authenticated")
        
        user = current_user
        
        # Update fields
        if email is not None:
            # Check if email is already taken by another user
            if User.objects.filter(email=email).exclude(pk=user.pk).exists():
                raise GraphQLError("Email already exists")
            user.email = email
        
        if first_name is not None:
            user.first_name = first_name
        
        if last_name is not None:
            user.last_name = last_name
        
        if phone is not None:
            user.phone = phone
        
        user.save()
        
        return UpdateUser(
            user=user,
            success=True,
            message="Profile updated successfully"
        )


class CreateTeamMember(graphene.Mutation):
    """Create a new team member (admin only)"""
    class Arguments:
        input = TeamMemberInput(required=True)
    
    user = graphene.Field(UserType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, input):
        current_user = info.context.user
        
        if not current_user.is_authenticated or not current_user.is_admin:
            raise GraphQLError("Only admins can create team members")
        
        username = input.get('username')
        email = input.get('email')
        password = input.get('password')
        
        if not username or not email or not password:
            raise GraphQLError("Username, email, and password are required")
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            raise GraphQLError("Username already exists")
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            raise GraphQLError("Email already exists")
        
        # Validate role
        role = input.get('role', User.Role.STAFF)
        if role not in [User.Role.ADMIN, User.Role.STAFF]:
            raise GraphQLError("Invalid role. Must be 'admin' or 'staff'")
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=input.get('first_name', ''),
            last_name=input.get('last_name', ''),
            phone=input.get('phone', ''),
            role=role,
            is_active=input.get('is_active', True),
            can_manage_orders=input.get('can_manage_orders', True),
            can_manage_products=input.get('can_manage_products', False),
            can_manage_categories=input.get('can_manage_categories', False),
            can_manage_promotions=input.get('can_manage_promotions', False),
            can_view_reports=input.get('can_view_reports', False),
            can_manage_reviews=input.get('can_manage_reviews', True),
            notes=input.get('notes', '')
        )
        
        return CreateTeamMember(
            user=user,
            success=True,
            message="Team member created successfully"
        )


class UpdateTeamMember(graphene.Mutation):
    """Update a team member (admin only)"""
    class Arguments:
        id = graphene.ID(required=True)
        input = TeamMemberInput(required=True)
    
    user = graphene.Field(UserType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, id, input):
        current_user = info.context.user
        
        if not current_user.is_authenticated or not current_user.is_admin:
            raise GraphQLError("Only admins can update team members")
        
        try:
            user = User.objects.get(pk=id)
        except User.DoesNotExist:
            raise GraphQLError("Team member not found")
        
        # Update basic info
        if input.get('username') is not None:
            if User.objects.filter(username=input.get('username')).exclude(pk=user.pk).exists():
                raise GraphQLError("Username already exists")
            user.username = input.get('username')
        
        if input.get('email') is not None:
            if User.objects.filter(email=input.get('email')).exclude(pk=user.pk).exists():
                raise GraphQLError("Email already exists")
            user.email = input.get('email')
        
        if input.get('password'):
            user.set_password(input.get('password'))
        
        if input.get('first_name') is not None:
            user.first_name = input.get('first_name')
        
        if input.get('last_name') is not None:
            user.last_name = input.get('last_name')
        
        if input.get('phone') is not None:
            user.phone = input.get('phone')
        
        # Update role
        if input.get('role') is not None:
            role = input.get('role')
            if role not in [User.Role.ADMIN, User.Role.STAFF]:
                raise GraphQLError("Invalid role. Must be 'admin' or 'staff'")
            user.role = role
        
        if input.get('is_active') is not None:
            user.is_active = input.get('is_active')
        
        # Update permissions
        if input.get('can_manage_orders') is not None:
            user.can_manage_orders = input.get('can_manage_orders')
        
        if input.get('can_manage_products') is not None:
            user.can_manage_products = input.get('can_manage_products')
        
        if input.get('can_manage_categories') is not None:
            user.can_manage_categories = input.get('can_manage_categories')
        
        if input.get('can_manage_promotions') is not None:
            user.can_manage_promotions = input.get('can_manage_promotions')
        
        if input.get('can_view_reports') is not None:
            user.can_view_reports = input.get('can_view_reports')
        
        if input.get('can_manage_reviews') is not None:
            user.can_manage_reviews = input.get('can_manage_reviews')
        
        if input.get('notes') is not None:
            user.notes = input.get('notes')
        
        user.save()
        
        return UpdateTeamMember(
            user=user,
            success=True,
            message="Team member updated successfully"
        )


class DeleteTeamMember(graphene.Mutation):
    """Delete a team member (admin only)"""
    class Arguments:
        id = graphene.ID(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, id):
        current_user = info.context.user
        
        if not current_user.is_authenticated or not current_user.is_admin:
            raise GraphQLError("Only admins can delete team members")
        
        try:
            user = User.objects.get(pk=id)
        except User.DoesNotExist:
            raise GraphQLError("Team member not found")
        
        # Prevent deleting yourself
        if user.pk == current_user.pk:
            raise GraphQLError("You cannot delete your own account")
        
        username = user.username
        user.delete()
        
        return DeleteTeamMember(
            success=True,
            message=f"Team member '{username}' deleted successfully"
        )


class ResetTeamMemberPassword(graphene.Mutation):
    """Reset a team member's password (admin only)"""
    class Arguments:
        id = graphene.ID(required=True)
        new_password = graphene.String(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, id, new_password):
        current_user = info.context.user
        
        if not current_user.is_authenticated or not current_user.is_admin:
            raise GraphQLError("Only admins can reset passwords")
        
        try:
            user = User.objects.get(pk=id)
        except User.DoesNotExist:
            raise GraphQLError("Team member not found")
        
        if len(new_password) < 8:
            raise GraphQLError("Password must be at least 8 characters long")
        
        user.set_password(new_password)
        user.save()
        
        return ResetTeamMemberPassword(
            success=True,
            message=f"Password reset successfully for '{user.username}'"
        )


class AccountsMutation(graphene.ObjectType):
    """All account-related mutations"""
    login = Login.Field()
    logout = Logout.Field()
    register = Register.Field()
    change_password = ChangePassword.Field()
    update_user = UpdateUser.Field()
    # Team management (admin only)
    create_team_member = CreateTeamMember.Field()
    update_team_member = UpdateTeamMember.Field()
    delete_team_member = DeleteTeamMember.Field()
    reset_team_member_password = ResetTeamMemberPassword.Field()

