import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import AnonymousUser
from .models import User


# ==================== GraphQL Types ====================

class UserType(DjangoObjectType):
    """GraphQL type for User"""
    is_admin = graphene.Boolean()
    is_staff_member = graphene.Boolean()
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'is_active', 'date_joined', 'created_at', 'updated_at'
        )
        # Exclude sensitive fields like password
    
    def resolve_is_admin(self, info):
        """Check if user is admin"""
        return self.is_admin
    
    def resolve_is_staff_member(self, info):
        """Check if user is staff member"""
        return self.is_staff_member


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
    role = graphene.String()  # Only admins can set role


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
        graphene.JSONString,
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
        
        import json
        stats = {
            'total_users': User.objects.count(),
            'admins': User.objects.filter(role='ADMIN').count(),
            'staff': User.objects.filter(role='STAFF').count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'inactive_users': User.objects.filter(is_active=False).count(),
        }
        return json.dumps(stats)


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
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        
        return Register(
            user=user,
            success=True,
            message="User created successfully"
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
    """Update user mutation - update current user or other users (admin only)"""
    class Arguments:
        user_id = graphene.ID()
        email = graphene.String()
        first_name = graphene.String()
        last_name = graphene.String()
        role = graphene.String()  # Only admins can change role
        is_active = graphene.Boolean()
    
    user = graphene.Field(UserType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, user_id=None, email=None, first_name=None, last_name=None, role=None, is_active=None):
        current_user = info.context.user
        
        if not current_user.is_authenticated:
            raise GraphQLError("User is not authenticated")
        
        # If user_id is provided, admin can update other users
        if user_id:
            if not current_user.is_admin:
                raise GraphQLError("Only admins can update other users")
            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                raise GraphQLError("User not found")
        else:
            # Update current user
            user = current_user
        
        # Only admins can change role
        if role is not None:
            if not current_user.is_admin:
                raise GraphQLError("Only admins can change user roles")
            if role not in [User.Role.ADMIN, User.Role.STAFF]:
                raise GraphQLError("Invalid role. Must be 'admin' or 'staff'")
            user.role = role
        
        # Only admins can change is_active
        if is_active is not None:
            if not current_user.is_admin:
                raise GraphQLError("Only admins can change user active status")
            user.is_active = is_active
        
        # Update other fields
        if email is not None:
            # Check if email is already taken by another user
            if User.objects.filter(email=email).exclude(pk=user.pk).exists():
                raise GraphQLError("Email already exists")
            user.email = email
        
        if first_name is not None:
            user.first_name = first_name
        
        if last_name is not None:
            user.last_name = last_name
        
        user.save()
        
        return UpdateUser(
            user=user,
            success=True,
            message="User updated successfully"
        )


class AccountsMutation(graphene.ObjectType):
    """All account-related mutations"""
    login = Login.Field()
    logout = Logout.Field()
    register = Register.Field()
    change_password = ChangePassword.Field()
    update_user = UpdateUser.Field()

