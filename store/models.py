from decimal import Decimal

from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=200)

    description = models.TextField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    stock = models.IntegerField(default=0)

    image = models.ImageField(
        upload_to='products/'
    )

    discount_percent = models.PositiveSmallIntegerField(default=0)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def auto_discount_percent(self):
        if self.price >= Decimal("50000"):
            return 15
        if self.price >= Decimal("10000"):
            return 10
        if self.price > 0:
            return 5
        return 0

    @property
    def effective_discount_percent(self):
        return self.discount_percent or self.auto_discount_percent()

    def save(self, *args, **kwargs):
        self.discount_percent = self.auto_discount_percent()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.user.username


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    @property
    def total_price(self):
        return self.quantity * self.product.price

    def __str__(self):
        return self.product.name


class Order(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    full_name = models.CharField(
        max_length=200
    )

    email = models.EmailField()

    address = models.TextField()

    city = models.CharField(
        max_length=100
    )

    state = models.CharField(
        max_length=100
    )

    zip_code = models.CharField(
        max_length=20
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Shipped', 'Shipped'),
            ('Delivered', 'Delivered')
        ],
        default='Pending'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Order #{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.IntegerField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return self.product.name


class Review(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    rating = models.IntegerField()

    comment = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_gallery/')

    def __str__(self):
        return self.product.name


class Coupon(models.Model):
    code = models.CharField(max_length=20)
    discount_percent = models.IntegerField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code
