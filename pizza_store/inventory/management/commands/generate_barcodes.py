# inventory/management/commands/generate_barcodes.py
"""
Django management command to generate barcodes for products
"""
from django.core.management.base import BaseCommand
from inventory.barcode_utils import generate_barcodes_for_all_products, assign_barcode_to_product, assign_sku_to_product
from products.models import Product


class Command(BaseCommand):
    help = 'Generate barcodes and SKUs for products'

    def add_arguments(self, parser):
        parser.add_argument(
            '--product-id',
            type=int,
            help='Generate barcode for specific product ID',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Generate barcodes for all products without barcodes',
        )
        parser.add_argument(
            '--sku-only',
            action='store_true',
            help='Only generate SKUs, not barcodes',
        )

    def handle(self, *args, **options):
        if options['product_id']:
            # Generate for specific product
            try:
                product = Product.objects.get(id=options['product_id'])
                
                if not options['sku_only']:
                    barcode = assign_barcode_to_product(product)
                    self.stdout.write(
                        self.style.SUCCESS(f'Generated barcode {barcode} for product: {product.name}')
                    )
                
                sku = assign_sku_to_product(product)
                self.stdout.write(
                    self.style.SUCCESS(f'Generated SKU {sku} for product: {product.name}')
                )
            except Product.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Product with ID {options["product_id"]} not found')
                )
        
        elif options['all']:
            # Generate for all products
            self.stdout.write('Generating barcodes and SKUs for all products...')
            result = generate_barcodes_for_all_products()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Generated {result["barcodes_assigned"]} barcodes and {result["skus_assigned"]} SKUs'
                )
            )
            
            if result['errors']:
                self.stdout.write(self.style.WARNING('Errors encountered:'))
                for error in result['errors']:
                    self.stdout.write(self.style.ERROR(f'  - {error}'))
        
        else:
            self.stdout.write(
                self.style.ERROR('Please specify --product-id <id> or --all')
            )

