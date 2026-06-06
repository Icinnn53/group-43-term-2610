from django.db import models
from owner.models import Stall


class Product(models.Model):
    stall = models.ForeignKey(
        Stall,
        on_delete=models.CASCADE,
        related_name='products'
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    product_image = models.ImageField(
        upload_to='product_images/',
        blank=True,
        null=True
    )

    # ✅ STOCK QUANTITY
    stock_quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name