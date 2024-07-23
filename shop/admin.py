from django.contrib import admin

from shop.models import Product, Category, Client

# Register your models here.
admin.site.register(Product)
admin.site.register(Client)
admin.site.register(Category)
