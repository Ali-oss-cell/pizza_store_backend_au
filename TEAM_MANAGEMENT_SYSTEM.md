# Team Management System

## Overview

The team management system allows store admins to create and manage team members (staff) with granular permission control. Team members can have different levels of access based on their role and assigned permissions.

---

## 🎯 **Roles**

### 1. Admin
- **Full access** to everything in the system
- Can create, update, and delete team members
- Can change store settings
- Can do everything staff members can do
- All permission checks automatically pass for admins

### 2. Staff (Team Member)
- **Limited access** based on assigned permissions
- Cannot change store settings
- Cannot manage other team members
- Access is controlled by individual permission flags

---

## 🔐 **Permission Flags**

Staff members have the following permission flags:

| Permission | Description | Default |
|------------|-------------|---------|
| `can_manage_orders` | View and update order status | ✅ True |
| `can_manage_products` | Create, update, delete products, sizes, toppings, etc. | ❌ False |
| `can_manage_categories` | Create, update, delete categories | ❌ False |
| `can_manage_promotions` | Create, update, delete promotions | ❌ False |
| `can_view_reports` | View sales reports and analytics | ❌ False |
| `can_manage_reviews` | Approve or reject product reviews | ✅ True |

### Permission Methods

The User model provides convenient methods to check permissions:

```python
user.has_order_permission()      # Can manage orders
user.has_product_permission()    # Can manage products
user.has_category_permission()   # Can manage categories
user.has_promotion_permission()  # Can manage promotions
user.has_report_permission()     # Can view reports
user.has_review_permission()     # Can manage reviews
```

**Note:** These methods automatically return `True` for admins.

---

## 📋 **User Model Fields**

```python
class User(AbstractUser):
    # Role
    role = CharField(choices=['admin', 'staff'], default='staff')
    
    # Contact
    phone = CharField(max_length=20, blank=True)
    
    # Permissions (staff only)
    can_manage_orders = BooleanField(default=True)
    can_manage_products = BooleanField(default=False)
    can_manage_categories = BooleanField(default=False)
    can_manage_promotions = BooleanField(default=False)
    can_view_reports = BooleanField(default=False)
    can_manage_reviews = BooleanField(default=True)
    
    # Notes
    notes = TextField(blank=True)
    
    # Timestamps
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

---

## 📝 **GraphQL API**

### UserType

```graphql
type UserType {
  id: ID!
  username: String!
  email: String!
  firstName: String
  lastName: String
  phone: String
  role: String!
  isActive: Boolean!
  dateJoined: DateTime!
  createdAt: DateTime!
  updatedAt: DateTime!
  
  # Computed fields
  isAdmin: Boolean!
  isStaffMember: Boolean!
  permissions: [String!]!
  
  # Permission flags
  canManageOrders: Boolean!
  canManageProducts: Boolean!
  canManageCategories: Boolean!
  canManagePromotions: Boolean!
  canViewReports: Boolean!
  canManageReviews: Boolean!
  
  notes: String
}
```

### TeamMemberInput

```graphql
input TeamMemberInput {
  username: String
  email: String
  password: String
  firstName: String
  lastName: String
  phone: String
  role: String
  isActive: Boolean
  
  # Permissions
  canManageOrders: Boolean
  canManageProducts: Boolean
  canManageCategories: Boolean
  canManagePromotions: Boolean
  canViewReports: Boolean
  canManageReviews: Boolean
  
  notes: String
}
```

---

## 🔧 **GraphQL Operations**

### Queries

#### Get Current User
```graphql
query {
  me {
    id
    username
    email
    firstName
    lastName
    role
    isAdmin
    permissions
    canManageOrders
    canManageProducts
  }
}
```

#### Get All Team Members (Admin Only)
```graphql
query {
  allUsers(role: "staff", isActive: true) {
    id
    username
    email
    firstName
    lastName
    role
    isActive
    permissions
    canManageOrders
    canManageProducts
    canManageCategories
    canManagePromotions
    canViewReports
    canManageReviews
    createdAt
  }
}
```

#### Get Team Member by ID (Admin Only)
```graphql
query {
  user(id: "1") {
    id
    username
    email
    role
    permissions
    notes
  }
}
```

#### Get Team Statistics (Admin Only)
```graphql
query {
  teamStats
}
```

**Response:**
```json
{
  "total_users": 5,
  "admins": 1,
  "staff": 4,
  "active_users": 4,
  "inactive_users": 1
}
```

---

### Mutations

#### Create Team Member (Admin Only)
```graphql
mutation {
  createTeamMember(input: {
    username: "john_staff"
    email: "john@store.com"
    password: "securepassword123"
    firstName: "John"
    lastName: "Smith"
    phone: "+1234567890"
    role: "staff"
    isActive: true
    canManageOrders: true
    canManageProducts: false
    canManageCategories: false
    canManagePromotions: false
    canViewReports: false
    canManageReviews: true
    notes: "Part-time evening shift"
  }) {
    user {
      id
      username
      email
      role
      permissions
    }
    success
    message
  }
}
```

#### Update Team Member (Admin Only)
```graphql
mutation {
  updateTeamMember(
    id: "2"
    input: {
      firstName: "John"
      lastName: "Smith Jr."
      canManageProducts: true
      canManagePromotions: true
      notes: "Promoted to senior staff"
    }
  ) {
    user {
      id
      username
      permissions
    }
    success
    message
  }
}
```

#### Delete Team Member (Admin Only)
```graphql
mutation {
  deleteTeamMember(id: "2") {
    success
    message
  }
}
```

#### Reset Team Member Password (Admin Only)
```graphql
mutation {
  resetTeamMemberPassword(
    id: "2"
    newPassword: "newsecurepassword123"
  ) {
    success
    message
  }
}
```

#### Update Own Profile (Any Authenticated User)
```graphql
mutation {
  updateUser(
    email: "newemail@store.com"
    firstName: "John"
    lastName: "Smith"
    phone: "+1234567890"
  ) {
    user {
      id
      email
      firstName
      lastName
      phone
    }
    success
    message
  }
}
```

#### Change Own Password (Any Authenticated User)
```graphql
mutation {
  changePassword(
    oldPassword: "currentpassword"
    newPassword: "newsecurepassword123"
    newPasswordConfirm: "newsecurepassword123"
  ) {
    success
    message
  }
}
```

---

## 🛡️ **Permission Matrix**

| Action | Admin | Staff (with permission) | Staff (without permission) |
|--------|-------|------------------------|---------------------------|
| View orders | ✅ | ✅ (can_manage_orders) | ❌ |
| Update order status | ✅ | ✅ (can_manage_orders) | ❌ |
| View order stats | ✅ | ✅ (can_view_reports) | ❌ |
| Create/edit products | ✅ | ✅ (can_manage_products) | ❌ |
| Create/edit categories | ✅ | ✅ (can_manage_categories) | ❌ |
| Create/edit promotions | ✅ | ✅ (can_manage_promotions) | ❌ |
| Approve reviews | ✅ | ✅ (can_manage_reviews) | ❌ |
| View all users | ✅ | ❌ | ❌ |
| Create team members | ✅ | ❌ | ❌ |
| Update team members | ✅ | ❌ | ❌ |
| Delete team members | ✅ | ❌ | ❌ |
| Update store settings | ✅ | ❌ | ❌ |

---

## 🎨 **Admin Interface**

The Django Admin interface provides:

### List View
- Username, full name, email
- Role badge (Admin: red, Staff: blue)
- Permissions summary
- Active status
- Created date

### Edit Form
- **Account Info**: Username, email, password
- **Personal Info**: First name, last name, phone
- **Role & Status**: Role selection, active toggle
- **Permissions**: All permission checkboxes
- **Notes**: Admin notes about the team member

---

## 💡 **Example Use Cases**

### 1. Cashier/Order Handler
```json
{
  "role": "staff",
  "canManageOrders": true,
  "canManageProducts": false,
  "canManageCategories": false,
  "canManagePromotions": false,
  "canViewReports": false,
  "canManageReviews": false
}
```

### 2. Kitchen Staff
```json
{
  "role": "staff",
  "canManageOrders": true,
  "canManageProducts": false,
  "canManageCategories": false,
  "canManagePromotions": false,
  "canViewReports": false,
  "canManageReviews": false
}
```

### 3. Senior Staff / Manager
```json
{
  "role": "staff",
  "canManageOrders": true,
  "canManageProducts": true,
  "canManageCategories": true,
  "canManagePromotions": true,
  "canViewReports": true,
  "canManageReviews": true
}
```

### 4. Marketing Staff
```json
{
  "role": "staff",
  "canManageOrders": false,
  "canManageProducts": false,
  "canManageCategories": false,
  "canManagePromotions": true,
  "canViewReports": true,
  "canManageReviews": true
}
```

---

## 🔒 **Security Notes**

1. **Password Requirements**: Minimum 8 characters
2. **Admin Protection**: Admins cannot delete their own account
3. **Session-Based Auth**: Uses Django session authentication
4. **Role Validation**: Role must be 'admin' or 'staff'
5. **Unique Constraints**: Username and email must be unique

---

## 📊 **Frontend Integration**

### Check User Permissions
```typescript
// After login, check user permissions
const { data } = await graphql.query({ query: ME_QUERY });
const user = data.me;

if (user.isAdmin) {
  // Show all admin features
} else {
  // Show features based on permissions
  if (user.canManageOrders) {
    // Show order management
  }
  if (user.canManageProducts) {
    // Show product management
  }
  // etc.
}
```

### Permission-Based UI
```typescript
// Use permissions list for UI rendering
const permissions = user.permissions; // ['orders', 'reviews']

const canShowOrders = permissions.includes('orders') || permissions.includes('all');
const canShowProducts = permissions.includes('products') || permissions.includes('all');
```

---

## ✅ **Summary**

The team management system provides:

✅ **Role-Based Access**: Admin and Staff roles  
✅ **Granular Permissions**: 6 different permission flags  
✅ **Easy Management**: GraphQL mutations for CRUD operations  
✅ **Self-Service**: Users can update their own profile and password  
✅ **Admin Control**: Full team management for admins  
✅ **Security**: Password hashing, session auth, role validation  
✅ **Flexibility**: Permissions can be combined for different roles  

This system allows you to create team members with exactly the permissions they need for their job! 🎉

