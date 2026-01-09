# inventory/test_pos_api.py
"""
Automated tests for POS API endpoints
Tests all POS queries and mutations
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from graphene.test import Client
from pizza_store.schema import schema

from products.models import Product, Category, Size
from orders.models import Order, OrderItem
from inventory.utils import receive_stock

User = get_user_model()


class POSTestCase(TestCase):
    """Base test case for POS API tests"""
    
    def setUp(self):
        # Create test user (staff member)
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@test.com',
            password='testpass123',
            is_staff=True
        )
        
        # Create regular user (non-staff)
        self.regular_user = User.objects.create_user(
            username='customer',
            email='customer@test.com',
            password='testpass123',
            is_staff=False
        )
        
        # Create category
        self.category = Category.objects.create(name="Pizza")
        
        # Create size
        self.size = Size.objects.create(
            name="Large",
            category=self.category,
            price_modifier=Decimal('3.00')
        )
        
        # Create products
        self.product1 = Product.objects.create(
            name="Margherita Pizza",
            base_price=Decimal('12.99'),
            category=self.category,
            track_inventory=True,
            barcode="1234567890123",
            sku="PIZZA-001",
            reorder_level=10
        )
        self.product1.available_sizes.add(self.size)
        
        self.product2 = Product.objects.create(
            name="Pepperoni Pizza",
            base_price=Decimal('14.99'),
            category=self.category,
            track_inventory=True,
            barcode="1234567890124",
            sku="PIZZA-002",
            reorder_level=10
        )
        
        # Product without inventory tracking
        self.product3 = Product.objects.create(
            name="Drink",
            base_price=Decimal('3.50'),
            category=self.category,
            track_inventory=False
        )
        
        # Receive stock for tracked products
        receive_stock(self.product1, 100, user=self.staff_user)
        receive_stock(self.product2, 50, user=self.staff_user)
        
        # Create GraphQL client
        self.client = Client(schema)
        
        # Create authenticated context for staff
        self.staff_context = self._create_context(self.staff_user)
        self.regular_context = self._create_context(self.regular_user)
    
    def _create_context(self, user):
        """Create GraphQL context with authenticated user"""
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.post('/graphql/')
        request.user = user
        return request


class POSQueriesTest(POSTestCase):
    """Test POS queries"""
    
    def test_pos_products_query(self):
        """Test posProducts query"""
        query = """
        query {
            posProducts {
                id
                name
                basePrice
                currentPrice
                barcode
                sku
                stockQuantity
                isInStock
                isLowStock
                category
                trackInventory
            }
        }
        """
        
        # Test with staff user (should work)
        result = self.client.execute(query, context_value=self.staff_context)
        self.assertIsNone(result.get('errors'))
        self.assertIn('data', result)
        self.assertIn('posProducts', result['data'])
        products = result['data']['posProducts']
        self.assertGreater(len(products), 0)
        
        # Check product data
        product = products[0]
        self.assertIn('id', product)
        self.assertIn('name', product)
        self.assertIn('basePrice', product)
        self.assertIn('stockQuantity', product)
    
    def test_pos_products_with_category_filter(self):
        """Test posProducts with category filter"""
        query = """
        query {
            posProducts(categoryId: "%s") {
                id
                name
                category
            }
        }
        """ % self.category.id
        
        result = self.client.execute(query, context_value=self.staff_context)
        self.assertIsNone(result.get('errors'))
        products = result['data']['posProducts']
        self.assertGreater(len(products), 0)
        self.assertEqual(products[0]['category'], "Pizza")
    
    def test_pos_products_with_search(self):
        """Test posProducts with search"""
        query = """
        query {
            posProducts(search: "Margherita") {
                id
                name
            }
        }
        """
        
        result = self.client.execute(query, context_value=self.staff_context)
        self.assertIsNone(result.get('errors'))
        products = result['data']['posProducts']
        self.assertGreater(len(products), 0)
        self.assertIn('Margherita', products[0]['name'])
    
    def test_pos_products_in_stock_only(self):
        """Test posProducts with inStockOnly filter"""
        query = """
        query {
            posProducts(inStockOnly: true) {
                id
                name
                isInStock
            }
        }
        """
        
        result = self.client.execute(query, context_value=self.staff_context)
        self.assertIsNone(result.get('errors'))
        products = result['data']['posProducts']
        # All returned products should be in stock
        for product in products:
            self.assertTrue(product['isInStock'])
    
    def test_pos_products_permission_denied(self):
        """Test posProducts requires staff access"""
        query = """
        query {
            posProducts {
                id
                name
            }
        }
        """
        
        # Test with regular user (should fail)
        result = self.client.execute(query, context_value=self.regular_context)
        self.assertIsNotNone(result.get('errors'))
        self.assertIn('Permission denied', result['errors'][0]['message'])
    
    def test_pos_product_query(self):
        """Test posProduct query"""
        query = """
        query {
            posProduct(productId: "%s") {
                id
                name
                basePrice
                stockQuantity
                isInStock
            }
        }
        """ % self.product1.id
        
        result = self.client.execute(query, context_value=self.staff_context)
        self.assertIsNone(result.get('errors'))
        product = result['data']['posProduct']
        self.assertEqual(product['id'], str(self.product1.id))
        self.assertEqual(product['name'], "Margherita Pizza")
        self.assertEqual(product['stockQuantity'], 100)
        self.assertTrue(product['isInStock'])
    
    def test_scan_barcode(self):
        """Test scanBarcode query"""
        query = """
        query {
            scanBarcode(barcode: "1234567890123") {
                id
                name
                barcode
                stockQuantity
                isInStock
            }
        }
        """
        
        result = self.client.execute(query, context_value=self.staff_context)
        self.assertIsNone(result.get('errors'))
        product = result['data']['scanBarcode']
        self.assertEqual(product['barcode'], "1234567890123")
        self.assertEqual(product['name'], "Margherita Pizza")
        self.assertEqual(product['stockQuantity'], 100)
    
    def test_scan_barcode_not_found(self):
        """Test scanBarcode with invalid barcode"""
        query = """
        query {
            scanBarcode(barcode: "9999999999999") {
                id
                name
            }
        }
        """
        
        result = self.client.execute(query, context_value=self.staff_context)
        self.assertIsNotNone(result.get('errors'))
        self.assertIn('not found', result['errors'][0]['message'].lower())
    
    def test_pos_recent_orders(self):
        """Test posRecentOrders query"""
        # Create a test order
        order = Order.objects.create(
            order_number="ORD-001",
            customer_name="Test Customer",
            customer_email="test@test.com",
            customer_phone="0412345678",
            order_type="pickup",
            subtotal=Decimal('12.99'),
            total=Decimal('12.99'),
            status=Order.Status.CONFIRMED
        )
        
        query = """
        query {
            posRecentOrders(limit: 10) {
                id
                orderNumber
                customerName
                total
                status
                itemCount
            }
        }
        """
        
        result = self.client.execute(query, context_value=self.staff_context)
        self.assertIsNone(result.get('errors'))
        orders = result['data']['posRecentOrders']
        self.assertGreater(len(orders), 0)
        self.assertEqual(orders[0]['orderNumber'], "ORD-001")
    
    def test_receipt_query(self):
        """Test receipt query"""
        # Create order with items
        order = Order.objects.create(
            order_number="ORD-002",
            customer_name="John Doe",
            customer_email="john@test.com",
            customer_phone="0412345678",
            order_type="pickup",
            subtotal=Decimal('25.98'),
            total=Decimal('25.98'),
            status=Order.Status.CONFIRMED
        )
        
        OrderItem.objects.create(
            order=order,
            product_name="Margherita Pizza",
            product_id=self.product1.id,
            quantity=2,
            unit_price=Decimal('12.99'),
            subtotal=Decimal('25.98')
        )
        
        query = """
        query {
            receipt(orderId: "%s") {
                orderNumber
                date
                time
                customerName
                customerPhone
                items {
                    productName
                    quantity
                    unitPrice
                    subtotal
                }
                subtotal
                total
            }
        }
        """ % order.id
        
        result = self.client.execute(query, context_value=self.staff_context)
        self.assertIsNone(result.get('errors'))
        receipt = result['data']['receipt']
        self.assertEqual(receipt['orderNumber'], "ORD-002")
        self.assertEqual(receipt['customerName'], "John Doe")
        self.assertEqual(len(receipt['items']), 1)
        self.assertEqual(receipt['items'][0]['productName'], "Margherita Pizza")
        self.assertEqual(receipt['items'][0]['quantity'], 2)
    
    def test_pos_daily_stats(self):
        """Test posDailyStats query"""
        # Create orders for today
        from django.utils import timezone
        from datetime import datetime, timedelta
        
        today = timezone.now().date()
        
        Order.objects.create(
            order_number="ORD-003",
            customer_name="Customer 1",
            customer_email="c1@test.com",
            customer_phone="0411111111",
            order_type="pickup",
            subtotal=Decimal('12.99'),
            total=Decimal('12.99'),
            status=Order.Status.CONFIRMED
        )
        
        Order.objects.create(
            order_number="ORD-004",
            customer_name="Customer 2",
            customer_email="c2@test.com",
            customer_phone="0422222222",
            order_type="delivery",
            subtotal=Decimal('14.99'),
            total=Decimal('14.99'),
            status=Order.Status.CONFIRMED
        )
        
        query = """
        query {
            posDailyStats {
                date
                totalSales
                orderCount
                averageOrderValue
                deliveryOrders
                pickupOrders
            }
        }
        """
        
        result = self.client.execute(query, context_value=self.staff_context)
        self.assertIsNone(result.get('errors'))
        stats = result['data']['posDailyStats']
        self.assertEqual(stats['orderCount'], 2)
        self.assertEqual(stats['deliveryOrders'], 1)
        self.assertEqual(stats['pickupOrders'], 1)
        self.assertGreater(Decimal(stats['totalSales']), Decimal('0'))
    
    def test_pos_today_stats(self):
        """Test posTodayStats query"""
        query = """
        query {
            posTodayStats {
                date
                totalSales
                orderCount
            }
        }
        """
        
        result = self.client.execute(query, context_value=self.staff_context)
        self.assertIsNone(result.get('errors'))
        stats = result['data']['posTodayStats']
        self.assertIn('date', stats)
        self.assertIn('totalSales', stats)
        self.assertIn('orderCount', stats)


class POSMutationsTest(POSTestCase):
    """Test POS mutations"""
    
    def test_create_pos_order(self):
        """Test createPosOrder mutation"""
        mutation = """
        mutation {
            createPosOrder(input: {
                customerName: "Test Customer"
                customerPhone: "0412345678"
                customerEmail: "test@test.com"
                orderType: "pickup"
                paymentMethod: "cash"
                items: [
                    {
                        productId: "%s"
                        quantity: 2
                    }
                ]
            }) {
                success
                message
                order {
                    id
                    orderNumber
                    total
                    status
                }
            }
        }
        """ % self.product1.id
        
        result = self.client.execute(mutation, context_value=self.staff_context)
        self.assertIsNone(result.get('errors'))
        data = result['data']['createPosOrder']
        self.assertTrue(data['success'])
        self.assertIn('Order created successfully', data['message'])
        self.assertIsNotNone(data['order'])
        self.assertIn('orderNumber', data['order'])
        
        # Verify order was created
        order_number = data['order']['orderNumber']
        order = Order.objects.get(order_number=order_number)
        self.assertEqual(order.customer_name, "Test Customer")
        self.assertEqual(order.items.count(), 1)
        
        # Verify stock was deducted
        self.product1.refresh_from_db()
        stock_item = self.product1.stock
        self.assertEqual(stock_item.quantity, 98)  # 100 - 2
    
    def test_create_pos_order_with_size(self):
        """Test createPosOrder with size"""
        mutation = """
        mutation {
            createPosOrder(input: {
                customerName: "Test Customer"
                customerPhone: "0412345678"
                orderType: "pickup"
                paymentMethod: "cash"
                items: [
                    {
                        productId: "%s"
                        quantity: 1
                        sizeId: "%s"
                    }
                ]
            }) {
                success
                order {
                    orderNumber
                    total
                }
            }
        }
        """ % (self.product1.id, self.size.id)
        
        result = self.client.execute(mutation, context_value=self.staff_context)
        self.assertIsNone(result.get('errors'))
        self.assertTrue(result['data']['createPosOrder']['success'])
        
        # Verify order item has size
        order_number = result['data']['createPosOrder']['order']['orderNumber']
        order = Order.objects.get(order_number=order_number)
        order_item = order.items.first()
        self.assertEqual(order_item.size_name, "Large")
    
    def test_create_pos_order_delivery(self):
        """Test createPosOrder for delivery"""
        mutation = """
        mutation {
            createPosOrder(input: {
                customerName: "Delivery Customer"
                customerPhone: "0412345678"
                orderType: "delivery"
                deliveryAddress: "123 Main St"
                paymentMethod: "card"
                items: [
                    {
                        productId: "%s"
                        quantity: 1
                    }
                ]
            }) {
                success
                order {
                    orderNumber
                    orderType
                    deliveryAddress
                }
            }
        }
        """ % self.product1.id
        
        result = self.client.execute(mutation, context_value=self.staff_context)
        self.assertIsNone(result.get('errors'))
        self.assertTrue(result['data']['createPosOrder']['success'])
        
        order_number = result['data']['createPosOrder']['order']['orderNumber']
        order = Order.objects.get(order_number=order_number)
        self.assertEqual(order.order_type, "delivery")
        self.assertEqual(order.delivery_address, "123 Main St")
    
    def test_create_pos_order_multiple_items(self):
        """Test createPosOrder with multiple items"""
        mutation = """
        mutation {
            createPosOrder(input: {
                customerName: "Multi Item Customer"
                customerPhone: "0412345678"
                orderType: "pickup"
                paymentMethod: "cash"
                items: [
                    {
                        productId: "%s"
                        quantity: 2
                    },
                    {
                        productId: "%s"
                        quantity: 1
                    }
                ]
            }) {
                success
                order {
                    orderNumber
                }
            }
        }
        """ % (self.product1.id, self.product2.id)
        
        result = self.client.execute(mutation, context_value=self.staff_context)
        self.assertIsNone(result.get('errors'))
        self.assertTrue(result['data']['createPosOrder']['success'])
        
        order_number = result['data']['createPosOrder']['order']['orderNumber']
        order = Order.objects.get(order_number=order_number)
        self.assertEqual(order.items.count(), 2)
    
    def test_create_pos_order_permission_denied(self):
        """Test createPosOrder requires staff access"""
        mutation = """
        mutation {
            createPosOrder(input: {
                customerName: "Test"
                customerPhone: "0412345678"
                orderType: "pickup"
                paymentMethod: "cash"
                items: [{ productId: "%s", quantity: 1 }]
            }) {
                success
            }
        }
        """ % self.product1.id
        
        result = self.client.execute(mutation, context_value=self.regular_context)
        self.assertIsNotNone(result.get('errors'))
        self.assertIn('Permission denied', result['errors'][0]['message'])
    
    def test_create_pos_order_missing_delivery_address(self):
        """Test createPosOrder requires delivery address for delivery orders"""
        mutation = """
        mutation {
            createPosOrder(input: {
                customerName: "Test"
                customerPhone: "0412345678"
                orderType: "delivery"
                paymentMethod: "cash"
                items: [{ productId: "%s", quantity: 1 }]
            }) {
                success
            }
        }
        """ % self.product1.id
        
        result = self.client.execute(mutation, context_value=self.staff_context)
        self.assertIsNotNone(result.get('errors'))
        self.assertIn('Delivery address is required', result['errors'][0]['message'])
    
    def test_create_pos_order_empty_items(self):
        """Test createPosOrder requires at least one item"""
        mutation = """
        mutation {
            createPosOrder(input: {
                customerName: "Test"
                customerPhone: "0412345678"
                orderType: "pickup"
                paymentMethod: "cash"
                items: []
            }) {
                success
            }
        }
        """
        
        result = self.client.execute(mutation, context_value=self.staff_context)
        self.assertIsNotNone(result.get('errors'))
        self.assertIn('at least one item', result['errors'][0]['message'])
    
    def test_create_pos_order_invalid_product(self):
        """Test createPosOrder with invalid product ID"""
        mutation = """
        mutation {
            createPosOrder(input: {
                customerName: "Test"
                customerPhone: "0412345678"
                orderType: "pickup"
                paymentMethod: "cash"
                items: [{ productId: "99999", quantity: 1 }]
            }) {
                success
            }
        }
        """
        
        result = self.client.execute(mutation, context_value=self.staff_context)
        self.assertIsNotNone(result.get('errors'))
        self.assertIn('not found', result['errors'][0]['message'])

