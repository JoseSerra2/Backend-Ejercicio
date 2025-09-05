from django.db import models
import uuid

class RegularDiscount(models.Model):
    discount_id= models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    discount_name = models.CharField(max_length=100)
    discount_description = models.TextField(null=True, blank=True)
    percentage = models.DecimalField(max_digits=2, decimal_places=2)
    initial_date = models.DateField()
    final_date = models.DateField(null=True, blank= True)
    discount_state= models.SmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    product = models.ForeignKey("products.Product", on_delete=models.PROTECT, related_name="regular_discount")

    def __str__(self):
        return self.discount_name

class WholesaleDiscount(models.Model):
    wholesale_discount_id= models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    min_quantity=models.IntegerField()
    max_quantity=models.IntegerField(null=True, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    w_state = models.SmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    product = models.ForeignKey("products.Product", on_delete=models.PROTECT, related_name="wholesale_discount")

def __str__(self):
    return f"{self.unit_price}"