from django.db import models
import uuid

# Modelos de tablas Stock, StockMovement, MovementType.

class MovementType(models.Model):
    movement_type_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    movement_type = models.CharField(max_length=50)
    state = models.SmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.movement_type

class Stock(models.Model):
    batch = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    initial_amount = models.IntegerField()
    current_amount = models.IntegerField()
    expire_date = models.DateField(null=True, blank=True)
    state = models.SmallIntegerField()
    product = models.ForeignKey("products.Product", on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Lote {self.batch} - {self.product.product_name}"


class StockMovement(models.Model):
    class Direction(models.IntegerChoices):
        ENTRADA = 1, 'Entrada'
        SALIDA = 2, 'Salida'
    movement_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    direction = models.SmallIntegerField(choices=Direction.choices)
    date = models.DateField()
    quantity = models.IntegerField()
    observations = models.TextField(null=True, blank=True)
    purchase_reference = models.ForeignKey("purchases.PurchaseDetail", on_delete=models.PROTECT, null=True, blank=True)
    sale_reference = models.ForeignKey("sales.SaleDetail", on_delete=models.PROTECT, null=True, blank=True)
    batch = models.ForeignKey(Stock, on_delete=models.PROTECT)
    movement_type = models.ForeignKey(MovementType, on_delete=models.PROTECT)
    state = models.SmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_direction_display()} - {self.quantity} unidades"
    
