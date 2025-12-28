"""
Root GraphQL schema for Pizza Store
Combines all app schemas into a single schema
"""
import graphene

# Import app schemas
from accounts.schema import AccountsQuery, AccountsMutation
from products.schema import ProductsQuery, ProductsMutation
from cart.schema import CartQuery, CartMutation
from orders.schema import OrdersQuery, OrdersMutation
from team.schema import TeamQuery, TeamMutation
# from payments.schema import PaymentsQuery, PaymentsMutation


class Query(
    AccountsQuery,
    ProductsQuery,
    CartQuery,
    OrdersQuery,
    TeamQuery,
    # PaymentsQuery,
    graphene.ObjectType,
):
    """Root query combining all app queries"""
    pass


class Mutation(
    AccountsMutation,
    ProductsMutation,
    CartMutation,
    OrdersMutation,
    TeamMutation,
    # PaymentsMutation,
    graphene.ObjectType,
):
    """Root mutation combining all app mutations"""
    pass


# Create the root schema
schema = graphene.Schema(query=Query, mutation=Mutation)

