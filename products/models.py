from django.db import models


class Category(models.Model):
    """A product category such as Electronics, Footwear or Beauty."""

    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='categories/', blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    """A product that is sold in MiniShop."""

    # ---- main fields ----
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='products/')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    stock_quantity = models.IntegerField(default=0)
    created_date = models.DateTimeField(auto_now_add=True)

    # ---- optional extra fields (used by the product details page) ----
    old_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text='Price before discount. Leave empty if there is no discount.',
    )
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=4.5)
    review_count = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)

    # extra gallery images (thumbnails on the details page)
    image_2 = models.ImageField(upload_to='products/', blank=True)
    image_3 = models.ImageField(upload_to='products/', blank=True)
    image_4 = models.ImageField(upload_to='products/', blank=True)

    # product information (mainly for laptops and phones)
    processor = models.CharField(max_length=100, blank=True)
    ram = models.CharField(max_length=100, blank=True)
    storage = models.CharField(max_length=100, blank=True)
    display = models.CharField(max_length=100, blank=True)
    battery = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['-created_date']

    def __str__(self):
        return self.name

    # ---- small helper methods used in templates ----

    @property
    def discount_percent(self):
        """Example: old price 700, price 650 -> 7 (% off)."""
        if self.old_price and self.old_price > self.price:
            return round((self.old_price - self.price) / self.old_price * 100)
        return 0

    @property
    def in_stock(self):
        return self.stock_quantity > 0

    def gallery(self):
        """All images of the product that are not empty."""
        return [img for img in [self.image, self.image_2, self.image_3, self.image_4] if img]

    def specs(self):
        """List of (icon, label, value) for the product information box."""
        rows = [
            ('bi-cpu', 'Processor', self.processor),
            ('bi-memory', 'RAM', self.ram),
            ('bi-device-hdd', 'Storage', self.storage),
            ('bi-display', 'Display', self.display),
            ('bi-battery-full', 'Battery', self.battery),
        ]
        return [row for row in rows if row[2]]

    def stars(self):
        """Turn the rating (e.g. 4.5) into a list of star types for the template:
        ['full', 'full', 'full', 'full', 'half']"""
        result = []
        for i in range(1, 6):
            if self.rating >= i:
                result.append('full')
            elif self.rating >= i - 0.5:
                result.append('half')
            else:
                result.append('empty')
        return result


class Order(models.Model):
    """An order placed by a customer from the cart page."""

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    customer_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_date']

    def __str__(self):
        return f'Order #{self.id} - {self.customer_name}'


class OrderItem(models.Model):
    """One product line inside an order (product + quantity)."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)   # kept even if the product is deleted
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.quantity} x {self.product_name}'

    @property
    def subtotal(self):
        return self.price * self.quantity
