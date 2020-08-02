from django.db import models


class Products(models.Model):
    name = models.CharField(max_length=1000, blank=True, null=True)
    sku = models.CharField(max_length=1000, primary_key=True, editable=False,
                           db_index=True)
    description = models.CharField(max_length=1000, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='Created At',
                                      db_index=True)
    modified_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.sku

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Product Informations'
