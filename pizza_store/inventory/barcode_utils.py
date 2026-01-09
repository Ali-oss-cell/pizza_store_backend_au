# inventory/barcode_utils.py
"""
Barcode generation and validation utilities
"""
import random
import string
from products.models import Product


def generate_barcode(length=13):
    """
    Generate a random barcode (EAN-13 format compatible)
    
    Args:
        length: Barcode length (default 13 for EAN-13)
    
    Returns:
        str: Generated barcode
    """
    # EAN-13 format: 13 digits
    # For internal use, we can generate any format
    if length == 13:
        # Generate 12 digits, then calculate check digit
        digits = ''.join([str(random.randint(0, 9)) for _ in range(12)])
        check_digit = calculate_ean13_check_digit(digits)
        return digits + str(check_digit)
    else:
        # For other lengths, just generate random digits
        return ''.join([str(random.randint(0, 9)) for _ in range(length)])


def calculate_ean13_check_digit(barcode_12):
    """
    Calculate EAN-13 check digit
    
    Args:
        barcode_12: 12-digit barcode (without check digit)
    
    Returns:
        int: Check digit (0-9)
    """
    if len(barcode_12) != 12:
        raise ValueError("Barcode must be 12 digits")
    
    # EAN-13 check digit calculation
    sum_even = sum(int(barcode_12[i]) for i in range(1, 12, 2))
    sum_odd = sum(int(barcode_12[i]) for i in range(0, 12, 2))
    total = sum_odd * 3 + sum_even
    check_digit = (10 - (total % 10)) % 10
    
    return check_digit


def generate_sku(category_name, product_name, product_id):
    """
    Generate SKU from product information
    
    Format: CATEGORY-PRODUCTID or CATEGORY-NAME-PRODUCTID
    
    Args:
        category_name: Product category name
        product_name: Product name
        product_id: Product ID
    
    Returns:
        str: Generated SKU
    """
    # Get first 3-4 letters of category
    category_prefix = category_name[:4].upper().replace(' ', '')
    
    # Get first 3-4 letters of product name
    product_prefix = ''.join([c for c in product_name[:4] if c.isalnum()]).upper()
    
    # Format: CAT-PROD-ID
    sku = f"{category_prefix}-{product_prefix}-{product_id:04d}"
    
    return sku


def assign_barcode_to_product(product, barcode=None):
    """
    Assign a barcode to a product
    
    Args:
        product: Product instance
        barcode: Optional barcode (if None, generates one)
    
    Returns:
        str: Assigned barcode
    """
    if barcode:
        # Check if barcode already exists
        if Product.objects.filter(barcode=barcode).exclude(id=product.id).exists():
            raise ValueError(f"Barcode {barcode} already assigned to another product")
        product.barcode = barcode
    else:
        # Generate unique barcode
        max_attempts = 100
        for _ in range(max_attempts):
            new_barcode = generate_barcode(13)
            if not Product.objects.filter(barcode=new_barcode).exists():
                product.barcode = new_barcode
                break
        else:
            raise ValueError("Could not generate unique barcode after 100 attempts")
    
    product.save()
    return product.barcode


def assign_sku_to_product(product, sku=None):
    """
    Assign an SKU to a product
    
    Args:
        product: Product instance
        sku: Optional SKU (if None, generates one)
    
    Returns:
        str: Assigned SKU
    """
    if sku:
        # Check if SKU already exists
        if Product.objects.filter(sku=sku).exclude(id=product.id).exists():
            raise ValueError(f"SKU {sku} already assigned to another product")
        product.sku = sku
    else:
        # Generate SKU from product info
        new_sku = generate_sku(
            product.category.name,
            product.name,
            product.id
        )
        
        # Ensure uniqueness
        base_sku = new_sku
        counter = 1
        while Product.objects.filter(sku=new_sku).exclude(id=product.id).exists():
            new_sku = f"{base_sku}-{counter}"
            counter += 1
        
        product.sku = new_sku
    
    product.save()
    return product.sku


def generate_barcodes_for_all_products():
    """
    Generate barcodes for all products that don't have one
    
    Returns:
        dict: Statistics of barcode generation
    """
    products_without_barcode = Product.objects.filter(barcode__isnull=True)
    products_without_sku = Product.objects.filter(sku__isnull=True)
    
    barcodes_assigned = 0
    skus_assigned = 0
    errors = []
    
    for product in products_without_barcode:
        try:
            assign_barcode_to_product(product)
            barcodes_assigned += 1
        except Exception as e:
            errors.append(f"Product {product.id} ({product.name}): {str(e)}")
    
    for product in products_without_sku:
        try:
            assign_sku_to_product(product)
            skus_assigned += 1
        except Exception as e:
            errors.append(f"Product {product.id} ({product.name}): {str(e)}")
    
    return {
        'barcodes_assigned': barcodes_assigned,
        'skus_assigned': skus_assigned,
        'errors': errors
    }

