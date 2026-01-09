from django.db import models
from django.core.validators import MinValueValidator


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0, help_text="Order in menu display")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Tags for categorizing products (e.g., Meat, Vegetarian, Chicken)"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#000000')  # For UI display
    
    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class IncludedItem(models.Model):
    """Items included in a combo (e.g., chips, salad with Parmas)"""
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Base ingredients for products (e.g., Mushrooms, Mozzarella, Garlic)"""
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Emoji or icon name")
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Size(models.Model):
    """Product sizes with price modifiers"""
    name = models.CharField(max_length=50)  # Small, Medium, Large, Can, 1.25L
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='sizes',
        help_text="Category this size belongs to"
    )
    price_modifier = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        help_text="Additional price for this size (can be negative)"
    )
    display_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['category', 'display_order', 'name']
        unique_together = [['name', 'category']]  # Same size name can exist for different categories
    
    def __str__(self):
        return f"{self.category.name}: {self.name}"


class Topping(models.Model):
    """Extra toppings/add-ons"""
    name = models.CharField(max_length=255, unique=True)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (+${self.price})"


class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True, help_text="URL-friendly identifier")
    description = models.TextField(blank=True)
    short_description = models.CharField(max_length=255, blank=True, help_text="Brief tagline for the product")
    base_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Base price (smallest size)"
    )
    # Sale pricing
    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Sale price (applies to all users when active)"
    )
    sale_start_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the sale starts (leave empty to start immediately)"
    )
    sale_end_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the sale ends (leave empty for no end date)"
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE,
        related_name='products'
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='products')
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False, help_text="Show on homepage/featured section")
    is_combo = models.BooleanField(default=False, help_text="Does this include other items?")
    included_items = models.ManyToManyField(IncludedItem, blank=True, related_name='products')
    
    # Ingredients (base ingredients shown in product detail)
    ingredients = models.ManyToManyField(
        Ingredient, 
        blank=True, 
        related_name='products',
        help_text="Base ingredients for this product"
    )
    
    # Preparation time
    prep_time_min = models.PositiveIntegerField(
        default=15,
        help_text="Minimum preparation time in minutes"
    )
    prep_time_max = models.PositiveIntegerField(
        default=20,
        help_text="Maximum preparation time in minutes"
    )
    
    # Ratings (calculated from reviews)
    average_rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0)]
    )
    rating_count = models.PositiveIntegerField(default=0)
    
    # Calories (optional nutritional info)
    calories = models.PositiveIntegerField(null=True, blank=True, help_text="Calories per serving")
    
    # Inventory fields
    barcode = models.CharField(
        max_length=50, 
        unique=True, 
        null=True, 
        blank=True,
        help_text="Product barcode (EAN-13, UPC-A, etc.)"
    )
    sku = models.CharField(
        max_length=50, 
        unique=True, 
        null=True, 
        blank=True,
        help_text="Stock Keeping Unit (SKU) - unique product identifier"
    )
    track_inventory = models.BooleanField(
        default=False, 
        help_text="Track stock quantity for this product"
    )
    reorder_level = models.PositiveIntegerField(
        default=10,
        validators=[MinValueValidator(0)],
        help_text="Alert when stock falls below this level (if tracking inventory)"
    )
    
    available_sizes = models.ManyToManyField(
        Size, 
        blank=True,
        related_name='products',
        help_text="Sizes available for this product"
    )
    available_toppings = models.ManyToManyField(
        Topping, 
        blank=True,
        related_name='products',
        help_text="Toppings that can be added to this product"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.category.name})"
    
    @property
    def prep_time_display(self):
        """Return formatted prep time string"""
        return f"{self.prep_time_min}-{self.prep_time_max} min"
    
    @property
    def is_on_sale(self):
        """Check if product is currently on sale"""
        if not self.sale_price:
            return False
        
        from django.utils import timezone
        now = timezone.now()
        
        # Check if sale has started
        if self.sale_start_date and now < self.sale_start_date:
            return False
        
        # Check if sale has ended
        if self.sale_end_date and now > self.sale_end_date:
            return False
        
        return True
    
    def get_current_base_price(self):
        """Get current base price (sale price if on sale, otherwise regular price)"""
        if self.is_on_sale:
            return self.sale_price
        return self.base_price
    
    def get_price_for_size(self, size):
        """Calculate price for a specific size (uses sale price if on sale)"""
        base_price = self.get_current_base_price()
        if size in self.available_sizes.all():
            return base_price + size.price_modifier
        return base_price
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage when on sale"""
        if not self.is_on_sale or not self.sale_price:
            return 0
        if self.base_price == 0:
            return 0
        discount = self.base_price - self.sale_price
        return round((discount / self.base_price) * 100, 0)
    
    def update_rating(self):
        """Recalculate average rating from reviews"""
        from django.db.models import Avg
        reviews = self.reviews.all()
        if reviews.exists():
            self.average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
            self.rating_count = reviews.count()
        else:
            self.average_rating = 0
            self.rating_count = 0
        self.save()
    
    @property
    def stock_quantity(self):
        """Get current stock quantity (0 if not tracking inventory)"""
        if not self.track_inventory:
            return None
        try:
            return self.stock.quantity
        except:
            return 0
    
    @property
    def is_in_stock(self):
        """Check if product is in stock"""
        if not self.track_inventory:
            return True  # If not tracking, assume in stock
        try:
            return self.stock.quantity > 0
        except:
            return True  # If no stock item exists yet, assume in stock
    
    @property
    def is_low_stock(self):
        """Check if product has low stock"""
        if not self.track_inventory:
            return False
        try:
            return self.stock.is_low_stock
        except:
            return False


class ProductReview(models.Model):
    """Customer reviews for products"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Rating from 1 to 5"
    )
    comment = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False, help_text="Approved by admin to display")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer_name} - {self.product.name} ({self.rating}★)"
    
    def save(self, *args, **kwargs):
        # Validate rating is between 1-5
        if self.rating > 5:
            self.rating = 5
        super().save(*args, **kwargs)
        # Update product rating when review is saved
        if self.is_approved:
            self.product.update_rating()