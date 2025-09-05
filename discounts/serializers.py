from rest_framework import serializers
from .models import RegularDiscount, WholesaleDiscount
from datetime import date
from django.db import models

class RegularDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegularDiscount
        fields= '__all__'

    def validate(self, data):
        product = data['product']
        initial_date = data['initial_date']
        final_date = data.get('final_date', None)

        regular_discount= RegularDiscount.objects.filter(
            product=product,
            discount_state=1,
        ).exclude(discount_id=self.instance.discount_id if self.instance else None)

        for discount in regular_discount:
            if(
                (not final_date or discount.final_date >= initial_date) and 
                (not discount.initial_date or initial_date <= discount.final_date)
            ):
                raise serializers.ValidationError("Ya existe un descuento regular que esta activo para este producto dentro del rango de fechas")

        wholesale_discount= WholesaleDiscount.objects.filter(
            product = product,
            w_state = 1
        )
        if wholesale_discount.exists():
            raise serializers.ValidationError("Ya existe un descuento por mayoreo activo para este producto")
        return data 
    
class WholesaleDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model= WholesaleDiscount
        fields='__all__'

    def validate(self, data):
        product = data['product']
        today = date.today()
        wholesale_discount= WholesaleDiscount.objects.filter(
            product = product,
            w_state = 1
        )
        if self.instance:
            wholesale_discount= wholesale_discount.exclude(wholesale_discount_id=self.instance.wholesale_discount_id)
        
        if wholesale_discount.exists():
            raise serializers.ValidationError("Ya tiene un descuento por mayoreo activo para este producto")

        regular_discounts = RegularDiscount.objects.filter(
            product = product,
            discount_state = 1,
            initial_date__lte=today,
        ).filter(
            models.Q(final_date__gte=today) | models.Q(final_date__isnull= True)
        )
        if regular_discounts.exists():
            raise serializers.ValidationError("Ya tiene un descuento regular acttivo para este productos")
        return data
