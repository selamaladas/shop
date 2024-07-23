from django.db import models
from django.contrib.auth.models import AbstractUser


class Client(AbstractUser):
    reset_token = models.CharField(max_length=100, verbose_name="Client reset token", default=None, null=True)
    address = models.CharField(max_length=100, verbose_name="Client address", default=None, null=True)
    phone = models.CharField(max_length=100, verbose_name="Client phone", default=None, null=True)
    profile_image = models.ImageField(upload_to='client_profile_images', verbose_name="Image", default=None, null=True)

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"

    def __str__(self):
        return self.username


class Product(models.Model):
    PRDName = models.CharField(max_length=100, verbose_name="Proudct name")
    PRDDesc = models.TextField(verbose_name="Product description")
    PRDPrice = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Price")
    PRDCost = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Cost")
    PRDCreated = models.DateTimeField(verbose_name="Created At")
    PRDIImage = models.ImageField(upload_to='product_images', verbose_name="Image")
    PRDCategory = models.ForeignKey('Category', on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return self.PRDName


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Category name")
    description = models.TextField(verbose_name="Product description")
    category_image = models.ImageField(upload_to='category_images', verbose_name="Image")
    created_at = models.DateTimeField(verbose_name="Created At")

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Cart(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    items = models.ManyToManyField(Product, through='CartItem')

    def __str__(self):
        return self.client.username


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(verbose_name="Quantity")

    def __str__(self):
        return self.product.PRDName


class Order(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Total")
    items = models.ManyToManyField(Product, through='OrderItem')
    tracking_number = models.CharField(max_length=100, verbose_name="Tracking number", default=None, null=True)
    status = models.CharField(max_length=100, verbose_name="Status", default=None, null=True)
    status_description = models.CharField(max_length=100, verbose_name="Status description", default=None, null=True)
    payment_method = models.CharField(max_length=100, verbose_name="Payment method")
    created_at = models.DateTimeField(verbose_name="Created At")

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return self.client.username


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(verbose_name="Quantity")
    price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Price")

    def __str__(self):
        return self.order.client.username
