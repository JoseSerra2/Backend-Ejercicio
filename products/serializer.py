from rest_framework import serializers

from .models import Product, Brand, Category
from discounts.models import RegularDiscount, WholesaleDiscount
from django.db.models import Prefetch, Q

class RegularDiscountSerializerProduct(serializers.ModelSerializer):
    class Meta:
        model = RegularDiscount
        fields = ['percentage', 'initial_date', 'final_date']

class WholesaleDiscountSerializerProduct(serializers.ModelSerializer):
    class Meta:
        model = WholesaleDiscount
        fields = ['min_quantity', 'max_quantity', 'unit_price']

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    regular_discount =  serializers.SerializerMethodField()
    wholesale_discount = WholesaleDiscountSerializerProduct(many = True, read_only = True)
    class Meta:
        model = Product
        fields = '__all__'
        extra_fields = ['brand_name', 'category_name', 'regular_discount', 'wholesale_discount']

    def get_regular_discount(self, obj):
        items = getattr(obj, 'active_regular_discounts', None)
        if items is None:
            from django.utils import timezone
            today = timezone.now().date()
            items = obj.regular_discount.filter(
                discount_state=1,
                initial_date__lte=today
            ).filter(
                Q(final_date__isnull=True) | Q(final_date__gte=today)
            )
        return RegularDiscountSerializerProduct(items, many=True).data
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['brand_name'] = instance.brand.brand_name
        data['category_name'] = instance.category.category_name
        return data