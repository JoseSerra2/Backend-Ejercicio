from django.db import models
import uuid

# Create your models here.
#Modelos de tablas: Product, Category, Brand

class Category (models.Model):
    category_id= models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category_name= models.CharField(max_length=100)
    category_state= models.SmallIntegerField(default=1)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.category_name

class Brand (models.Model):
    brand_id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand_name = models.CharField(max_length=100)
    brand_state = models.SmallIntegerField(default=1)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.brand_name

class Product (models.Model):
    product_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_stock = models.IntegerField(default=0) 
    image_url = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT)
    product_state = models.SmallIntegerField(default=1)

    def __str__(self):
        return self.product_name