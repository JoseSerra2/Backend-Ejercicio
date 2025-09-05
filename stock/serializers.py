from rest_framework import serializers
from .models import MovementType, Stock, StockMovement
from products.serializer import ProductSerializer
from products.models import Product

class MoveSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovementType
        fields = '__all__'
        
class StockSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)  # anida el producto
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), write_only=True, source='product'
    )
    description = serializers.CharField(source='product.description', read_only=True)

    class Meta:
        model = Stock
        fields = [
            'batch',
            'initial_amount',
            'current_amount',
            'expire_date',
            'description',
            'product',      # para lectura (anidado)
            'product_id',   # para escritura
            'state',        # <<<<< AÑADE ESTO
        ]
        
class StockMovementSerializer(serializers.ModelSerializer):
    movement_type_text = serializers.CharField(write_only=True, required=False)

    direction_display = serializers.CharField(source='get_direction_display', read_only=True)
    movement_type_name = serializers.CharField(source='movement_type.movement_type', read_only=True)
    product_name = serializers.CharField(source='batch.product.product_name', read_only=True)
    batch_id = serializers.CharField(source='batch.batch', read_only=True)

    class Meta:
        model = StockMovement
        fields = [
            'movement_id',
            'date',
            'direction',
            'direction_display',
            'quantity',
            'observations',
            'movement_type',
            'movement_type_name',
            'movement_type_text',  # nuevo campo
            'batch',
            'batch_id',
            'product_name',
            'state',
        ]
        extra_kwargs = {
            'movement_type': {'required': False, 'allow_null': True},
        }

    def create(self, validated_data):
        movement_type_text = validated_data.pop('movement_type_text', None)
        
        if movement_type_text:
            movement_type_obj, created = MovementType.objects.get_or_create(
                movement_type=movement_type_text,
                defaults={'state': 1}
            )
            validated_data['movement_type'] = movement_type_obj
        
        return super().create(validated_data)

