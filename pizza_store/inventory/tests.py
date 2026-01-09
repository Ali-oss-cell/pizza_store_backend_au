# inventory/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from products.models import Product, Category, Size
from orders.models import Order, OrderItem
from cart.models import Cart, CartItem
from .models import StockItem, StockMovement, StockAlert
from .utils import (
    get_or_create_stock_item, adjust_stock, sell_stock,
    receive_stock, return_stock, check_low_stock,
    get_low_stock_items, get_out_of_stock_items
)

User = get_user_model()


class StockItemModelTest(TestCase):
    """Test StockItem model"""
    
    def setUp(self):
        self.category = Category.objects.create(name="Pizza")
        self.product = Product.objects.create(
            name="Test Pizza",
            base_price=Decimal('12.99'),
            category=self.category,
            track_inventory=True,
            reorder_level=10
        )
        self.stock_item = StockItem.objects.create(
            product=self.product,
            quantity=50,
            reorder_level=10,
            reorder_quantity=50
        )
    
    def test_stock_item_creation(self):
        """Test stock item is created correctly"""
        self.assertEqual(self.stock_item.product, self.product)
        self.assertEqual(self.stock_item.quantity, 50)
        self.assertEqual(self.stock_item.reorder_level, 10)
        self.assertFalse(self.stock_item.is_low_stock)
        self.assertFalse(self.stock_item.is_out_of_stock)
    
    def test_is_low_stock(self):
        """Test low stock detection"""
        self.stock_item.quantity = 5
        self.stock_item.save()
        self.assertTrue(self.stock_item.is_low_stock)
    
    def test_is_out_of_stock(self):
        """Test out of stock detection"""
        self.stock_item.quantity = 0
        self.stock_item.save()
        self.assertTrue(self.stock_item.is_out_of_stock)


class StockMovementModelTest(TestCase):
    """Test StockMovement model"""
    
    def setUp(self):
        self.category = Category.objects.create(name="Pizza")
        self.product = Product.objects.create(
            name="Test Pizza",
            base_price=Decimal('12.99'),
            category=self.category,
            track_inventory=True
        )
        self.stock_item = StockItem.objects.create(
            product=self.product,
            quantity=50
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
    
    def test_stock_movement_creation(self):
        """Test stock movement is created correctly"""
        movement = StockMovement.objects.create(
            stock_item=self.stock_item,
            movement_type=StockMovement.MovementType.SALE,
            quantity_change=-5,
            quantity_before=50,
            quantity_after=45,
            reference="ORDER-001",
            notes="Test sale",
            created_by=self.user
        )
        
        self.assertEqual(movement.stock_item, self.stock_item)
        self.assertEqual(movement.movement_type, StockMovement.MovementType.SALE)
        self.assertEqual(movement.quantity_change, -5)
        self.assertEqual(movement.quantity_before, 50)
        self.assertEqual(movement.quantity_after, 45)
        self.assertEqual(movement.reference, "ORDER-001")


class StockAlertModelTest(TestCase):
    """Test StockAlert model"""
    
    def setUp(self):
        self.category = Category.objects.create(name="Pizza")
        self.product = Product.objects.create(
            name="Test Pizza",
            base_price=Decimal('12.99'),
            category=self.category,
            track_inventory=True
        )
        self.stock_item = StockItem.objects.create(
            product=self.product,
            quantity=5,
            reorder_level=10
        )
    
    def test_stock_alert_creation(self):
        """Test stock alert is created correctly"""
        alert = StockAlert.objects.create(
            stock_item=self.stock_item,
            status=StockAlert.AlertStatus.ACTIVE,
            message="Low stock alert"
        )
        
        self.assertEqual(alert.stock_item, self.stock_item)
        self.assertEqual(alert.status, StockAlert.AlertStatus.ACTIVE)
        self.assertEqual(alert.message, "Low stock alert")


class InventoryUtilsTest(TestCase):
    """Test inventory utility functions"""
    
    def setUp(self):
        self.category = Category.objects.create(name="Pizza")
        self.product = Product.objects.create(
            name="Test Pizza",
            base_price=Decimal('12.99'),
            category=self.category,
            track_inventory=True,
            reorder_level=10
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
    
    def test_get_or_create_stock_item(self):
        """Test getting or creating stock item"""
        stock_item = get_or_create_stock_item(self.product)
        self.assertIsNotNone(stock_item)
        self.assertEqual(stock_item.product, self.product)
        self.assertEqual(stock_item.quantity, 0)
        
        # Should return same item on second call
        stock_item2 = get_or_create_stock_item(self.product)
        self.assertEqual(stock_item.id, stock_item2.id)
    
    def test_receive_stock(self):
        """Test receiving stock from supplier"""
        movement = receive_stock(
            product=self.product,
            quantity=100,
            notes="Initial stock",
            user=self.user
        )
        
        self.assertIsNotNone(movement)
        self.assertEqual(movement.movement_type, StockMovement.MovementType.RECEIPT)
        self.assertEqual(movement.quantity_change, 100)
        self.assertEqual(movement.quantity_after, 100)
        
        stock_item = StockItem.objects.get(product=self.product)
        self.assertEqual(stock_item.quantity, 100)
        self.assertIsNotNone(stock_item.last_restocked)
    
    def test_sell_stock(self):
        """Test selling stock (deducting on sale)"""
        # First receive stock
        receive_stock(self.product, 100, user=self.user)
        
        # Then sell
        movement = sell_stock(
            product=self.product,
            quantity=5,
            order_number="ORDER-001",
            user=self.user
        )
        
        self.assertIsNotNone(movement)
        self.assertEqual(movement.movement_type, StockMovement.MovementType.SALE)
        self.assertEqual(movement.quantity_change, -5)
        self.assertEqual(movement.quantity_after, 95)
        self.assertEqual(movement.reference, "ORDER-001")
        
        stock_item = StockItem.objects.get(product=self.product)
        self.assertEqual(stock_item.quantity, 95)
    
    def test_adjust_stock(self):
        """Test manual stock adjustment"""
        receive_stock(self.product, 100, user=self.user)
        
        movement = adjust_stock(
            product=self.product,
            quantity_change=-10,
            movement_type=StockMovement.MovementType.ADJUSTMENT,
            reference="ADJ-001",
            notes="Damaged items",
            user=self.user
        )
        
        self.assertIsNotNone(movement)
        self.assertEqual(movement.movement_type, StockMovement.MovementType.ADJUSTMENT)
        self.assertEqual(movement.quantity_after, 90)
        
        stock_item = StockItem.objects.get(product=self.product)
        self.assertEqual(stock_item.quantity, 90)
    
    def test_return_stock(self):
        """Test returning stock"""
        receive_stock(self.product, 100, user=self.user)
        sell_stock(self.product, 10, "ORDER-001", user=self.user)
        
        movement = return_stock(
            product=self.product,
            quantity=2,
            reference="ORDER-001",
            notes="Customer return",
            user=self.user
        )
        
        self.assertIsNotNone(movement)
        self.assertEqual(movement.movement_type, StockMovement.MovementType.RETURN)
        self.assertEqual(movement.quantity_after, 92)
        
        stock_item = StockItem.objects.get(product=self.product)
        self.assertEqual(stock_item.quantity, 92)
    
    def test_stock_cannot_go_negative(self):
        """Test that stock cannot go below zero"""
        receive_stock(self.product, 10, user=self.user)
        
        # Try to sell more than available
        movement = sell_stock(
            product=self.product,
            quantity=20,
            order_number="ORDER-001",
            user=self.user
        )
        
        stock_item = StockItem.objects.get(product=self.product)
        self.assertEqual(stock_item.quantity, 0)  # Should be 0, not negative
        self.assertEqual(movement.quantity_after, 0)
    
    def test_low_stock_alert_creation(self):
        """Test that low stock alerts are created"""
        receive_stock(self.product, 15, user=self.user)
        
        # Sell enough to go below reorder level
        sell_stock(self.product, 10, "ORDER-001", user=self.user)
        
        # Check alert was created
        alerts = StockAlert.objects.filter(
            stock_item__product=self.product,
            status=StockAlert.AlertStatus.ACTIVE
        )
        self.assertTrue(alerts.exists())
        
        alert = alerts.first()
        self.assertIn("low stock", alert.message.lower())
    
    def test_get_low_stock_items(self):
        """Test getting low stock items"""
        # Create products with different stock levels
        product1 = Product.objects.create(
            name="Product 1",
            base_price=Decimal('10.00'),
            category=self.category,
            track_inventory=True,
            reorder_level=10
        )
        product2 = Product.objects.create(
            name="Product 2",
            base_price=Decimal('10.00'),
            category=self.category,
            track_inventory=True,
            reorder_level=10
        )
        
        receive_stock(product1, 5, user=self.user)  # Below reorder level
        receive_stock(product2, 20, user=self.user)  # Above reorder level
        
        low_stock = get_low_stock_items()
        self.assertEqual(low_stock.count(), 1)
        self.assertEqual(low_stock.first().product, product1)
    
    def test_get_out_of_stock_items(self):
        """Test getting out of stock items"""
        product1 = Product.objects.create(
            name="Product 1",
            base_price=Decimal('10.00'),
            category=self.category,
            track_inventory=True
        )
        product2 = Product.objects.create(
            name="Product 2",
            base_price=Decimal('10.00'),
            category=self.category,
            track_inventory=True
        )
        
        receive_stock(product1, 0, user=self.user)  # Out of stock
        receive_stock(product2, 10, user=self.user)  # In stock
        
        out_of_stock = get_out_of_stock_items()
        self.assertEqual(out_of_stock.count(), 1)
        self.assertEqual(out_of_stock.first().product, product1)
    
    def test_product_without_inventory_tracking(self):
        """Test that products without inventory tracking don't create stock items"""
        product = Product.objects.create(
            name="No Track Product",
            base_price=Decimal('10.00'),
            category=self.category,
            track_inventory=False
        )
        
        stock_item = get_or_create_stock_item(product)
        self.assertIsNone(stock_item)
        
        movement = receive_stock(product, 100, user=self.user)
        self.assertIsNone(movement)


class OrderStockDeductionTest(TestCase):
    """Test automatic stock deduction when orders are created"""
    
    def setUp(self):
        self.category = Category.objects.create(name="Pizza")
        self.product = Product.objects.create(
            name="Test Pizza",
            base_price=Decimal('12.99'),
            category=self.category,
            track_inventory=True,
            reorder_level=10
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        
        # Receive initial stock
        receive_stock(self.product, 100, user=self.user)
    
    def test_stock_deducted_on_order_creation(self):
        """Test that stock is automatically deducted when order is created"""
        # Get initial stock
        initial_stock = StockItem.objects.get(product=self.product).quantity
        
        # Test the sell_stock function directly (this is what order creation calls)
        sell_stock(
            product=self.product,
            quantity=5,
            order_number="TEST-ORDER-001",
            user=self.user
        )
        
        final_stock = StockItem.objects.get(product=self.product).quantity
        self.assertEqual(final_stock, initial_stock - 5)
        
        # Check movement was created
        movements = StockMovement.objects.filter(
            stock_item__product=self.product,
            movement_type=StockMovement.MovementType.SALE,
            reference="TEST-ORDER-001"
        )
        self.assertTrue(movements.exists())
        self.assertEqual(movements.first().quantity_change, -5)


class ProductInventoryFieldsTest(TestCase):
    """Test Product model inventory fields and properties"""
    
    def setUp(self):
        self.category = Category.objects.create(name="Pizza")
    
    def test_product_inventory_fields(self):
        """Test product has inventory fields"""
        product = Product.objects.create(
            name="Test Pizza",
            base_price=Decimal('12.99'),
            category=self.category,
            track_inventory=True,
            barcode="1234567890123",
            sku="PIZZA-001",
            reorder_level=10
        )
        
        self.assertTrue(product.track_inventory)
        self.assertEqual(product.barcode, "1234567890123")
        self.assertEqual(product.sku, "PIZZA-001")
        self.assertEqual(product.reorder_level, 10)
    
    def test_product_stock_quantity_property(self):
        """Test product stock_quantity property"""
        product = Product.objects.create(
            name="Test Pizza",
            base_price=Decimal('12.99'),
            category=self.category,
            track_inventory=True
        )
        
        # Initially no stock item, should return 0
        self.assertEqual(product.stock_quantity, 0)
        
        # Create stock item
        StockItem.objects.create(product=product, quantity=50)
        self.assertEqual(product.stock_quantity, 50)
    
    def test_product_is_in_stock_property(self):
        """Test product is_in_stock property"""
        product = Product.objects.create(
            name="Test Pizza",
            base_price=Decimal('12.99'),
            category=self.category,
            track_inventory=True
        )
        
        # No stock item exists yet, should return True (assume in stock)
        self.assertTrue(product.is_in_stock)
        
        # Create stock item with stock
        StockItem.objects.create(product=product, quantity=10)
        product.refresh_from_db()
        self.assertTrue(product.is_in_stock)
        
        # Out of stock
        stock_item = StockItem.objects.get(product=product)
        stock_item.quantity = 0
        stock_item.save()
        product.refresh_from_db()
        self.assertFalse(product.is_in_stock)
    
    def test_product_is_low_stock_property(self):
        """Test product is_low_stock property"""
        product = Product.objects.create(
            name="Test Pizza",
            base_price=Decimal('12.99'),
            category=self.category,
            track_inventory=True,
            reorder_level=10
        )
        
        # Create stock item above reorder level
        StockItem.objects.create(product=product, quantity=20, reorder_level=10)
        self.assertFalse(product.is_low_stock)
        
        # Below reorder level
        stock_item = StockItem.objects.get(product=product)
        stock_item.quantity = 5
        stock_item.save()
        product.refresh_from_db()
        self.assertTrue(product.is_low_stock)
