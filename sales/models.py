from django.db import models
import uuid

# Modelos de tablas Sale, SaleDetail y SaleBill

class Sale(models.Model):
    sale_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sale_date = models.DateField(auto_now_add=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    total_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    sale_state = models.SmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Venta {self.sale_date} - Total: {self.total}"

    
class SaleDetail(models.Model):
    sale_detail_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    unit_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sale_state = models.SmallIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount_subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sale = models.ForeignKey(Sale, on_delete=models.PROTECT, related_name='details')
    product = models.ForeignKey("products.Product", on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.quantity} unidades - Subtotal {self.subtotal}"


class SaleBill(models.Model):
    bill_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField()
    series = models.CharField(max_length=30, default='A', blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    total_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    sale = models.OneToOneField(Sale, on_delete=models.PROTECT, related_name='bill')
    bill_state = models.SmallIntegerField(default=1)
    client = models.ForeignKey("usuarios.Client", on_delete=models.PROTECT, null=True, blank=True, default='CF')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.bill_number


