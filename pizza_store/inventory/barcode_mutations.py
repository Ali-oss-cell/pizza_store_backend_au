# inventory/barcode_mutations.py
"""
GraphQL mutations for barcode generation and management
"""
import graphene
from graphql import GraphQLError
from products.models import Product
from .barcode_utils import assign_barcode_to_product, assign_sku_to_product, generate_barcodes_for_all_products


class GenerateBarcode(graphene.Mutation):
    """Generate and assign barcode to a product"""
    
    class Arguments:
        product_id = graphene.ID(required=True)
        barcode = graphene.String(description="Optional: specific barcode to assign")
    
    success = graphene.Boolean()
    message = graphene.String()
    barcode = graphene.String()
    product = graphene.Field('products.schema.ProductType')
    
    @staticmethod
    def mutate(root, info, product_id, barcode=None):
        user = info.context.user if info.context.user.is_authenticated else None
        
        # Check permissions
        if not user or not (user.is_staff or user.is_superuser):
            raise GraphQLError("Permission denied. Staff access required.")
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise GraphQLError("Product not found")
        
        try:
            assigned_barcode = assign_barcode_to_product(product, barcode)
            product.refresh_from_db()
            
            return GenerateBarcode(
                success=True,
                message=f"Barcode {assigned_barcode} assigned to {product.name}",
                barcode=assigned_barcode,
                product=product
            )
        except ValueError as e:
            raise GraphQLError(str(e))


class GenerateSKU(graphene.Mutation):
    """Generate and assign SKU to a product"""
    
    class Arguments:
        product_id = graphene.ID(required=True)
        sku = graphene.String(description="Optional: specific SKU to assign")
    
    success = graphene.Boolean()
    message = graphene.String()
    sku = graphene.String()
    product = graphene.Field('products.schema.ProductType')
    
    @staticmethod
    def mutate(root, info, product_id, sku=None):
        user = info.context.user if info.context.user.is_authenticated else None
        
        # Check permissions
        if not user or not (user.is_staff or user.is_superuser):
            raise GraphQLError("Permission denied. Staff access required.")
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise GraphQLError("Product not found")
        
        try:
            assigned_sku = assign_sku_to_product(product, sku)
            product.refresh_from_db()
            
            return GenerateSKU(
                success=True,
                message=f"SKU {assigned_sku} assigned to {product.name}",
                sku=assigned_sku,
                product=product
            )
        except ValueError as e:
            raise GraphQLError(str(e))


class GenerateAllBarcodes(graphene.Mutation):
    """Generate barcodes and SKUs for all products that don't have them"""
    
    success = graphene.Boolean()
    message = graphene.String()
    barcodes_assigned = graphene.Int()
    skus_assigned = graphene.Int()
    errors = graphene.List(graphene.String)
    
    @staticmethod
    def mutate(root, info):
        user = info.context.user if info.context.user.is_authenticated else None
        
        # Check permissions (admin only)
        if not user or not user.is_superuser:
            raise GraphQLError("Permission denied. Admin access required.")
        
        result = generate_barcodes_for_all_products()
        
        return GenerateAllBarcodes(
            success=True,
            message=f"Generated {result['barcodes_assigned']} barcodes and {result['skus_assigned']} SKUs",
            barcodes_assigned=result['barcodes_assigned'],
            skus_assigned=result['skus_assigned'],
            errors=result['errors']
        )

