from django.contrib import admin
from product.models import Products


@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'description',
                    'created_at', 'modified_at',)
    search_fields = ('name', 'sku',)
